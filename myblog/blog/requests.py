# blog/requests.py

from django.db import connection
from .models import CustomUser
from .models import Post
from django.contrib.auth.hashers import check_password

from .sql_queries import (
    INSERT_USER,
    INSERT_USER_PROFILE,
    SELECT_USER_BY_CREDENTIALS,
    SELECT_ALL_POSTS,
    SELECT_USER_PROFILE,
)

def register_user(username, password, email, first_name, last_name, bio, avatar_url):
    with connection.cursor() as cursor:
        cursor.execute(INSERT_USER, [username, password, email, first_name, last_name])
        user_id = cursor.lastrowid
        cursor.execute(INSERT_USER_PROFILE, [user_id, bio, avatar_url])

def authenticate_user(username, password):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_USER_BY_CREDENTIALS, [username])
        user_data = cursor.fetchone()
    if user_data:
        # Extract the hashed password from the database
        hashed_password = user_data[1]  # Assuming the hashed password is in the second column

        # Check if the provided password matches the hashed password
        if check_password(password, hashed_password):
            # If the passwords match, create a user object with the retrieved data
            user = CustomUser(*user_data)  # Replace with your actual user model
            return user

    return None

def get_all_posts():
    with connection.cursor() as cursor:
        cursor.execute(SELECT_ALL_POSTS)
        columns = [col[0] for col in cursor.description]
        posts_data = cursor.fetchall()
        posts_dicts = [dict(zip(columns, row)) for row in posts_data]
        posts = [Post(**data) for data in posts_dicts]
        post_queryset = Post.objects.filter(id__in=[post.id for post in posts])
    return post_queryset

def get_user_profile(user_id):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_USER_PROFILE, [user_id])
        profile = cursor.fetchone()
    return profile
