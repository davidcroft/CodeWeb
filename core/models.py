from django.db import models
from django.db import transaction

from django import forms

from django.contrib.auth.models import User

from image_cropping import ImageCropField, ImageRatioField

class Tweet(models.Model):
    text = models.CharField(max_length=200)
    url = models.URLField()
    department = models.CharField(max_length=10)

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    degree = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=10, blank=True)
    bio = models.TextField(blank=True)
    picture = ImageCropField(upload_to='codelab-images-users', blank=True)
    cropPicture = ImageRatioField('picture', '500x500', allow_fullsize=True)

    def __unicode__(self):
        return self.user.username

class Project(models.Model):
    topic = models.CharField(max_length=200, blank=True)
    picture = ImageCropField(upload_to='codelab-images-projects', blank=True)
    cropPicture = ImageRatioField('picture', '1000x1000', allow_fullsize=True)
    dateTime = models.DateTimeField("Project Created Time")
    author = models.ForeignKey(User)
    def __unicode__(self):
        return self.topic

class Item(models.Model):
    project = models.ForeignKey(Project)
    TYPE_CHOICES = (('default', 'Please choose a type'), ('text', 'Text'), ('video', 'Video Embedding'), ('image', 'Picture'))
    itemType = models.CharField(max_length=5, choices=TYPE_CHOICES, default='default')
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to="codelab-images-project-items", blank=True)
    video = models.TextField(blank=True)

class Paper(models.Model):
    topic = models.CharField(max_length=200)
    description = models.CharField(max_length=2000, blank=True)
    fileDoc = models.FileField(upload_to='codelab-papers')
    dateTime = models.DateTimeField("Paper Created Time")
    author = models.ForeignKey(User)
    def __unicode__(self):
        return self.topic

class NewsPost(models.Model):
    topic = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    dateTime = models.DateTimeField('News Post Created Time')
    picture = ImageCropField(upload_to='codelab-images-users', blank=True)
    cropPicture = ImageRatioField('picture', '800x450', allow_fullsize=True)
    def __unicode__(self):
        return self.topic

class Slide(models.Model):
    description = models.CharField(max_length=200, blank=True)
    picture = ImageCropField(upload_to='codelab-slides', blank=True)
    cropPicture = ImageRatioField('picture', '1200x550', allow_fullsize=True)
    def __unicode__(self):
        return self.description

class About(models.Model):
    description = models.TextField()
    picture = models.ImageField(upload_to='codelab-about', blank=True)
    dateTime = models.DateTimeField('About Created Time')
    def __unicode__(self):
        return self.description

class Admission(models.Model):
    description = models.CharField(max_length=2000)
    picture = models.ImageField(upload_to='codelab-admission', blank=True)
    dateTime = models.DateTimeField('About Created Time')
    def __unicode__(self):
        return self.description


class Post(models.Model):
    topic = models.CharField(max_length=200)
    description = models.CharField(max_length=2000)
    picture = models.ImageField(upload_to='codelab-posts', blank=True)
    dateTime = models.DateTimeField("Post Created Time")
    userProfile = models.ForeignKey(UserProfile)
    likes = models.IntegerField(blank=True)

    def __unicode__(self):
        return self.description

class Comment(models.Model):
    description = models.TextField()
    post = models.ForeignKey(Post)
    userProfile = models.ForeignKey(UserProfile)
    dateTime = models.DateTimeField('Comment created time')

    def __unicode__(self):
        return self.content

