from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Script(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=320)
    description = models.CharField(max_length=2080)
    codeFolder = models.CharField(max_length=500)
    users = models.ManyToManyField(User)
    dateCreated = models.DateTimeField(auto_now_add=True, blank=True, editable=False)

