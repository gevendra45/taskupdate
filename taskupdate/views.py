from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.utils import timezone
from django_rest_passwordreset.signals import reset_password_token_created
from django.contrib.auth.models import User
from django.db.models import Q
from datetime import timedelta, date, datetime
import pandas as pd
import pytz
from .models import Post_Details
from .serializers import loginSerializer

@api_view(['POST', ])
def register(request):
    """
    url -> /auth/register/
    DataFormat -> {
        "email" : "",
        "first_name" : "",
        "last_name" : "",
        "password1" : "",
        "password2" : ""
    }"""
    if "email" not in request.data or "first_name" not in request.data or "last_name" not in request.data or "password1" not in request.data or "password2" not in request.data:
        return Response(status = 400, data={"Msg": "Details missing for querying"})
    same_email = User.objects.filter(email=request.data['email'])
    if len(same_email):
        return Response(status=400, data={'msg': 'User already exists with given email address'})
    if request.data["password1"] != request.data["password2"]:
        return Response(status=400, data={'msg': 'Passwords not matching please try again'})
    try:
        a=User(
            username=request.data['email'], 
            first_name=request.data['first_name'], 
            last_name=request.data['last_name'], 
            email=request.data['email'], 
            password=request.data['password1'])
        a.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Some error"})
    return Response(status=200, data={'Msg': request.data['email']+" was registered successfully."})

@api_view(["POST", ])
def login(request):
    """
    url -> /auth/login/
    DataFormat -> {
        "username" : "",
        "password" : "",
    }
    """
    serializer = loginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data
        if not user.is_active:
            return Response(status=401, data={'Msg': 'No longer access provided'})
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh = str(refresh)
        return Response(data={'Msg': "Login Successful.", 'AccessToken':access, "RefreshToken":refresh})
    else:
        res = serializer.errors
        return Response(res, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    url -> /auth/me/
    Headers -> {
        Authorization : JWT JWT_TOKEN
    }
    """
    try:
        user = User.objects.get(username=request.user)
    except Exception as e:
        return Response({'Message': 'Logout Failed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'Message': 'Logout Successful'})

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def fetch_users(request):
    try:
        user=User.objects.all().values('username')
        if len(user)>0:
            df = pd.DataFrame.from_dict(user)
            result = df.to_dict('records')
        else:
            return Response(status=200 , data={"Msg":"No User Exist"} )
    except Exception as e:
        return Response(status=200 , data={"Msg":"No User Exist"} )
        pass
    return Response(status=200 , data=result)

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def create_project(request):
    input_data=request.data
    if ("post_name" not in input_data or "description" not in input_data or 
        "duration" not in input_data or "post_type" not in input_data):
        return Response(status=401, data={'Msg': 'Parameter are missing for creating a Project'})
    if request.data["post_type"] != "Project":
        return Response(status=401, data={'Msg': 'Invalid Parameter for creating a Project'})
    if "assignee" not in request.data:
        request.data["assignee"]=User.objects.get(username=request.user)
    else:
        request.data["assignee"]=User.objects.get(username=request.data["assignee"])
    request.data["post_related"]=None
    try:
        creating=Post_Details(
            post_name = request.data['post_name'], 
            description = request.data['description'],
            duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration'])),
            created_date = timezone.now(),
            update_date = timezone.now(),
            assignee = request.data['assignee'], 
            post_type = request.data['post_type'].lower(), 
            post_related = request.data['post_related'])
        creating.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while creating Project"})
    return Response(data={'Msg': "Project Created Successfully"})

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def view_project(request):
    try:
        post_details=Post_Details.objects.filter(post_type="project").values('post_name', 'description', 'duration', 'created_date', 'update_date', 'assignee__username')
        print(post_details)
        if len(post_details)>0:
            df = pd.DataFrame.from_dict(post_details)
            result = df.to_dict('records')
        else:
            return Response(status=200, data={"Msg":"No Project exist under this User"})
    except Exception as e:
        return Response(status=200, data={"Msg":"No Project exist under this User"} )
        pass
    return Response(status=200, data=result)

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def update_project(request):
    if ("id" not in request.data or "post_name" not in request.data or "description" not in request.data or "duration" not in request.data or "post_type" not in request.data):
        return Response(status=401, data={'Msg': 'Parameter are missing for updating a Project'})
    if request.data["post_type"] != "Project":
        return Response(status=401, data={'Msg': 'Invalid Parameter for Updating the Project'})
    request.data['post_related']=None
    try:
        update=Post_Details.objects.get(id=request.data["id"])
        if "post_name" in request.data:
            update.post_name = request.data['post_name']
        if "description" in request.data:
            update.description = request.data['description']
        if "duration" in request.data:
            update.duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration']))
        update.update_date = timezone.now()
        if "assignee" not in request.data:
            update.assignee=User.objects.get(username=request.user)
        else:
            update.assignee=User.objects.get(username=request.data["assignee"])
        if "post_type" in request.data:
            update.post_type = request.data['post_type'].lower()
        if "post_related" in request.data:
            update.post_related = request.data['post_related']
        update.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while updating Project"})
    return Response(data={'Msg': "Project Details Updated Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def delete_project(request):
    if "id" not in request.data:
        return Response(status=401, data={'Msg': 'Parameter are missing for deleting a project'})
    try:
        delete_post=Post_Details.objects.get(id=int(request.data["id"]))
        if delete_post is None:
            return Response(status=400, data={'Error': "No such Project exist"})
        if str(delete_post.assignee.username) != str(User.objects.get(username=request.user)):
            return Response(status=400, data={'Error': "Project can't be deleted as you are not the author"})
        delete_post.delete()
    except Exception as e:
        return Response(status=400, data={'Error': "No such Project exist"})
    try:
        delete_sub_post=Post_Details.objects.filter(post_related=int(request.data["id"]))
        if delete_sub_post is None:
            return Response(status=400, data={'Error': "No such Project exist"})
        delete_post.delete()
    except Exception as e:
        pass
    return Response(data={'Msg': "Project Details Deleted Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def create_task(request):
    if ("post_name" not in request.data or "description" not in request.data or "duration" not in request.data 
        or "post_type" not in request.data or "post_related" not in request.data):
        return Response(status=401, data={'Msg': 'Parameter are missing for creating a Task'})
    if request.data["post_type"] != "Task" or request.data["post_related"] is None:
        return Response(status=401, data={'Msg': 'Invalid Parameter for creating a Task'})
    if "assignee" not in request.data:
        request.data["assignee"]=User.objects.get(username=request.user)
    else:
        request.data["assignee"]=User.objects.get(username=request.data["assignee"])
    try:
        creating=Post_Details(
            post_name = request.data['post_name'], 
            description = request.data['description'],
            duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration'])),
            created_date = timezone.now(),
            update_date = timezone.now(),
            assignee = request.data['assignee'], 
            post_type = request.data['post_type'].lower(), 
            post_related = Post_Details.objects.get(id=int(request.data['post_related'])))
        creating.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while creating Task"})
    return Response(data={'Msg': "Task Created Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def view_task(request):
    if "project_id" not in request.data:
        return Response(status=400, data={'Error':'No Project ID provided'})
    try:
        task_details=Post_Details.objects.filter(post_related=request.data["project_id"]).values('post_name', 'description', 'duration', 'created_date', 'update_date', 'assignee__username')
        df = pd.DataFrame.from_dict(task_details)
        if len(df)>0:
            result = df.to_dict('records')
        else:
            return Response(status=200, data={"Msg":"No Task exist under this project"} )    
    except Exception as e:
        return Response(status=200, data={"Msg":"No Task exist under this project ex"} )
        pass
    return Response(status=200, data=result)

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def update_task(request):
    if ("id" not in request.data or "post_name" not in request.data or "description" not in request.data 
            or "duration" not in request.data or "post_type" not in request.data):
        return Response(status=401, data={'Msg': 'Parameter are missing for updating a task'})
    if request.data["post_type"] != "Task" or request.data["post_related"] is None:
        return Response(status=401, data={'Msg': 'Invalid Parameter for updating as task'})
    try:
        update=Post_Details.objects.get(id=request.data["id"])
        if "post_name" in request.data: 
            update.post_name = request.data['post_name']    
        if "description" in request.data:   
            update.description = request.data['description']    
        if "duration" in request.data:  
            update.duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration']))  
        update.update_date = timezone.now() 
        if "assignee" not in request.data:  
            update.assignee=User.objects.get(username=request.user) 
        else:   
            update.assignee=User.objects.get(username=request.data["assignee"]) 
        if "post_type" in request.data: 
            update.post_type = request.data['post_type'].lower()    
        if "post_related" in request.data:
            update.post_related = Post_Details.objects.get(id=int(request.data['post_related']))
            update.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while updating Task"})
    return Response(data={'Msg': "Task Details Updated Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def delete_task(request):
    if "task_id" not in request.data:
        return Response(status=401, data={'Msg': 'Parameter are missing for deleting a task'})
    try:
        delete_post=Post_Details.objects.get(id=request.data["task_id"])
        if delete_post is None: 
            return Response(status=400, data={'Error': "No such Sub Task exist"})   
        if str(delete_post.assignee.username) != str(User.objects.get(username=request.user)):  
            return Response(status=400, data={'Error': "Sub Task can't be deleted as you are not the author"})        
        delete_post.delete()
    except Exception as e: 
        return Response(status=400, data={'Error': "No such Project exist"})    
    try:
        delete_sub_post=Post_Details.objects.filter(post_related=int(request.data["id"]))   
        delete_sub_post.delete()    
    except Exception as e:
        pass
    return Response(data={'Msg': "Task Details Deleted Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def create_subtask(request):
    if ("post_name" not in request.data or "description" not in request.data or "duration" not in request.data 
        or "post_type" not in request.data or "post_related" not in request.data):
        return Response(status=401, data={'Msg': 'Parameter are missing for creating a subtask'})
    if request.data["post_type"] != "Subtask" or request.data["post_related"] is None:
        return Response(status=401, data={'Msg': 'Invalid Parameter for deleting as subtask post_related'})
    if "assignee" not in request.data:
        request.data["assignee"]=User.objects.get(username=request.user)
    else:
        request.data["assignee"]=User.objects.get(username=request.data["assignee"])
    try:
        creating=Post_Details(
            post_name = request.data['post_name'], 
            description = request.data['description'],
            duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration'])),
            created_date = timezone.now(), 
            update_date = timezone.now(), 
            assignee = request.data['assignee'], 
            post_type = request.data['post_type'].lower(), 
            post_related = Post_Details.objects.get(id=int(request.data['post_related'])))
        creating.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while creating Subtask"})
    return Response(data={'Msg': "Subtask Created Successfully"})

@api_view(['GET', ])
@permission_classes([IsAuthenticated])
def view_subtask(request):
    if "subtask_id" not in request.data:
        return Response(status=400, data={'Error':'No Subtask ID provided'})
    try:
        subtask_details=Post_Details.objects.filter(post_related=request.data["subtask_id"]).values('post_name', 'description', 'duration', 'created_date', 'update_date', 'assignee__username')
        df = pd.DataFrame.from_dict(subtask_details)
        if len(df)>0:
            result = df.to_dict('records')
        else:
            return Response(status=200 , data={"Msg":"No Subtask exist under this Task"} )    
    except Exception as e:
        return Response(status=200 , data={"Msg":"No Subtask exist under this Task"} )
        pass
    return Response(status=200 , data=result)

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def update_subtask(request):
    if "id" not in request.data or "post_name" not in request.data or "description" not in request.data or "duration" not in request.data or "post_type" not in request.data:
        return Response(status=401, data={'Msg': 'Parameter are missing for updating a Subtask'})
    if request.data["post_type"] != "Subtask" or request.data["post_related"] is None:
        return Response(status=401, data={'Msg': 'Invalid Parameter for updating as Subtask'})
    try:
        update=Post_Details.objects.get(id=request.data["id"])
        if "post_name" in request.data:     
            update.post_name = request.data['post_name']        
        if "description" in request.data:       
            update.description = request.data['description']        
        if "duration" in request.data:      
            update.duration = pytz.UTC.localize(datetime.now())+ timedelta(days=int(request.data['duration']))      
        update.update_date = timezone.now()     
        if "assignee" not in request.data:      
            update.assignee=User.objects.get(username=request.user)     
        else:       
            update.assignee=User.objects.get(username=request.data["assignee"])     
        if "post_type" in request.data:     
            update.post_type = request.data['post_type'].lower()        
        if "post_related" in request.data:  
            update.post_related = Post_Details.objects.get(id=int(request.data['post_related']))
        update.save()
    except Exception as e:
        return Response(status=400, data={'Error': "Error while updating Subtask"})
    return Response(data={'Msg': "Subtask Details Updated Successfully"})

@api_view(['POST', ])
@permission_classes([IsAuthenticated])
def delete_subtask(request):
    if "id" not in request.data:
        return Response(status=401, data={'Msg': 'Parameter are missing for deleting a Subtask'})
    try:
        delete_post=Post_Details.objects.get(id=request.data["id"])
        if delete_post is None: 
            return Response(status=400, data={'Error': "No such Sub Task exist"})   
        if str(delete_post.assignee.username) != str(User.objects.get(username=request.user)):  
            return Response(status=400, data={'Error': "Sub Task can't be deleted as you are not the author"})        
        delete_post.delete()
    except Exception as e: 
        return Response(status=400, data={'Error': "No such Sub Task exist"})
    return Response(data={'Msg': "Project Details Deleted Successfully"})