# blog/models.py

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    email_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    objects = CustomUserManager()

    class Meta:
        swappable = 'AUTH_USER_MODEL'

class CustomGroup(Group):
    class Meta:
        proxy = True

    @classmethod
    def _get_permissions_query(cls, perms, ctype):
        return super()._get_permissions_query(perms, ctype).using('default')

class SubscriptionPlan(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.IntegerField()
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    bio = models.TextField()
    avatar_url = models.CharField(max_length=255)
    followers_count = models.IntegerField(default=0)
    subscription = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.user.username
 
class Post(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', related_name='posts')
    likes_count = models.IntegerField(default=0)

class PostLike(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class PostTag(models.Model):
    id = models.AutoField(primary_key=True)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

class Bookmark(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    note = models.TextField()

class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

class Advertisement(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    content = models.TextField()
    image_url = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

class Payment(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_date = models.DateField()


class Log(models.Model):
    TABLE_CHOICES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('like', 'Like'),
        ('follow', 'Follow'),
    ]

    OPERATION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    ]

    table_name = models.CharField(max_length=50, choices=TABLE_CHOICES)
    operation = models.CharField(max_length=10, choices=OPERATION_CHOICES)
    element_id = models.PositiveBigIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.table_name} {self.operation} (ID: {self.element_id})"

