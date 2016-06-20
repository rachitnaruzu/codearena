from django.contrib.auth.models import User
from django.db import models
import base64
from datetime import timedelta, datetime as dt
from django.utils import timezone

class Setting(models.Model):
    parameter = models.CharField(max_length=50, default='')
    value = models.IntegerField(default=1)

class Problem(models.Model):
    code = models.CharField(max_length=30)
    url = models.TextField()
    platform = models.CharField(max_length=100)
    solved = models.IntegerField(default = 0)
    points = models.IntegerField(default = 0)
    users = models.ManyToManyField(User)

    def __str__(self):
        return self.code

class Customuser(models.Model):
    user = models.OneToOneField(User)
    
    passwordkey = models.CharField(max_length=60, default='none')
    passwordkey_exdate = models.DateTimeField(default = timezone.now() - timedelta(minutes = 15))
    
    rollno = models.CharField(max_length=30)
    batch =  models.IntegerField(default = 0)
    branch = models.CharField(max_length=60, default = 'CSE')
    activatekey = models.CharField(max_length=60, default='none')
    points = models.IntegerField(default = 0)
    
    picflag = models.IntegerField(default=2)
    _pic = models.TextField(blank=True)
    def get_pic(self):
        return base64.b64decode(self._pic)
    def set_pic(self, pic):
        self._pic = base64.b64encode(pic)
    pic = property(get_pic, set_pic)
    
    spojhandle = models.CharField(max_length=50, default='')
    spojflag = models.IntegerField(default=2)
    spojrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    hackerrankhandle = models.CharField(max_length=50, default='')
    hackerrankflag = models.IntegerField(default=2)
    hackerrankrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    geeksforgeekshandle = models.CharField(max_length=50, default='')
    geeksforgeeksflag = models.IntegerField(default=2)
    geeksforgeeksrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    topcoderhandle = models.CharField(max_length=50, default='')
    topcoderflag = models.IntegerField(default=2)
    topcoderrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    topcodermaxrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    codeforceshandle = models.CharField(max_length=50, default='')
    codeforcesflag = models.IntegerField(default=2)
    codeforcesrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    codeforcesmaxrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    interviewbithandle = models.CharField(max_length=50, default='')
    interviewbitflag = models.IntegerField(default=2)
    interviewbitrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    
    codechefhandle = models.CharField(max_length=50, default='')
    codechefflag = models.IntegerField(default=2)
    codecheflongrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    codechefshortrating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    codechefltimerating = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    def __str__(self):
        return self.user.username
        
class AllowedMail(models.Model):
    mailid = models.CharField(max_length=60, unique = True)
    
    def __str__(self):
        return self.mailid

class Dummy(models.Model):
    name = models.CharField(max_length=60)
    
    def __str__(self):
        return self.name
