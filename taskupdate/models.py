from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Post_Details(models.Model):
    list_type = (('task' , 'Task'), ('project','Project') , ('subtask' ,'Subtask'))
    post_name = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    duration = models.DateTimeField(null=True, blank=True)
    created_date = models.DateTimeField(null=True, blank=True)
    update_date = models.DateTimeField(null=True, blank=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, null=True,
                                          blank=True, related_name='Created_by')
    post_type = models.CharField(max_length=7, choices=list_type, default='Project')
    post_related = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)


    class Meta:
        verbose_name = 'Post_Detail'
        verbose_name_plural = 'Post_Details'

#assignee, assignee_id, created_date, description, duration, id, post_details, post_name, post_related, post_related_id, post_type, update_date