# blog/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm
from .models import CustomUser, UserProfile, Post, Comment, Tag, SubscriptionPlan, PostLike, Bookmark, Follow, Advertisement, Payment
from django.db import connection
from .forms import EditProfileForm, EditUserForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseServerError

@login_required
def user_profile(request):

    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM get_current_user_profile_with_followers(%s, %s);', [request.user.id, request.user.id])
        user_data = cursor.fetchone()
    print(user_data)
    context = {
        'user_profile': {
            'id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'bio': user_data[3],
            'followers_count': user_data[4],
        },
    }

    return render(request, 'current_user_profile.html', context)

def post_list(request):
    raw_query = "SELECT * FROM get_all_posts()"
    posts = Post.objects.raw(raw_query)
    return render(request, 'post_list.html', {'posts': posts})

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('post_list')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('post_list')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

@login_required
def logout(request):
    auth_logout(request)
    return redirect('post_list')

def edit_profile(request):
    user = request.user
    user_profile = user.userprofile

    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditProfileForm(request.POST, instance=user_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            # Extract form data
            new_first_name = user_form.cleaned_data['first_name']
            new_last_name = user_form.cleaned_data['last_name']
            new_bio = profile_form.cleaned_data['bio']
            new_avatar_url = profile_form.cleaned_data['avatar_url']

            # Execute the stored procedure
            with connection.cursor() as cursor:
                cursor.callproc('update_user_profile', [user.id, new_first_name, new_last_name, new_bio, new_avatar_url])
            return redirect('user_profile')
    else:
        user_form = EditUserForm(instance=user)
        profile_form = EditProfileForm(instance=user_profile)

    return render(request, 'edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})

def edit_post(request, post_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM get_post_by_id(%s);', [post_id])
        post_data = cursor.fetchone()

    # Prepare the response with post data
    if post_data:
        post = {
            'id': post_data[0],
            'title': post_data[1],
            'content': post_data[2],
            'created_at': post_data[3],
            'updated_at': post_data[4],
            'user_id': post_data[5],
            'user_username': post_data[6],
        }

    if request.method == 'POST':
        new_title = request.POST.get('new_title')
        new_content = request.POST.get('new_content')

        with connection.cursor() as cursor:
            cursor.callproc('edit_post', [post_id, new_title, new_content])

        return redirect('post_details', post_id=post_id)

    context = {
        'post': post,
    }

    return render(request, 'edit_post.html', context)

def delete_post(request, post_id):
    with connection.cursor() as cursor:
        cursor.callproc('delete_post', [post_id])

    # Redirect to a different page after deletion
    return redirect('post_list')

def add_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        user_id = request.user.id if request.user.is_authenticated else 1  # Replace with your logic to get the user ID

        with connection.cursor() as cursor:
            cursor.execute('SELECT add_post(%s, %s, %s);', [title, content, user_id])

        return redirect('post_list')

    return render(request, 'add_post.html')

def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        user_id = request.user.id

        with connection.cursor() as cursor:
            cursor.callproc('add_comment', [post_id, content, user_id])

        return redirect('post_details', post_id=post_id)

    context = {
        'post': post,
    }

    return render(request, 'add_comment.html', context)


def post_details(request, post_id):
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM get_post_by_id(%s);', [post_id])
        post_data = cursor.fetchone()
    print(post_data)
    # Prepare the response with post data
    if post_data:
        c_post = {
            'id': post_data[0],
            'title': post_data[1],
            'content': post_data[2],
            'created_at': post_data[3],
            'updated_at': post_data[4],
            'user_id': post_data[5],
            'user_username': post_data[6],
            'likes_count': post_data[7],
        }
    # Get the count of likes for the post
        like_count = c_post['likes_count']
        is_current_user_post = (request.user.id == c_post['user_id'])
        
     # Call SQL function to get comments
        with connection.cursor() as cursor:
            cursor.callproc('get_post_comments', [post_id])
            comments_data = cursor.fetchall()

    # Convert comments data to a list of dictionaries
        comments = [
            {
                'comment_id': comment[0],
                'content': comment[1],
                'created_at': comment[2],
                'updated_at': comment[3],
                'user_id': comment[4],
                'user_username': comment[5],
            }
            for comment in comments_data
        ]
        context = {
            'post': c_post,
            'post_id': post_id,
            'is_current_user_post': is_current_user_post,
            'like_count': like_count,
            'comments': comments,
        }
    return render(request, 'post_details.html', context)

@csrf_exempt
@require_POST
def toggle_like(request, post_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return HttpResponseBadRequest("User not authenticated")

    # Get user ID
    user_id = request.user.id

    # Execute the toggle_like SQL function
    with connection.cursor() as cursor:
        cursor.execute('SELECT toggle_like(%s, %s); ', [post_id, user_id])

    # Call the get_post_by_id SQL function to fetch updated post data
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM get_post_by_id(%s);', [post_id])
        post_data = cursor.fetchone()

    # Prepare the response with post data
    if post_data:
        post = {
            'id': post_data[0],
            'title': post_data[1],
            'content': post_data[2],
            'created_at': post_data[3],
            'updated_at': post_data[4],
            'user_id': post_data[5],
            'user_username': post_data[6],
            'likes_count': post_data[7],
        }
        print(post)
        return JsonResponse({'success': True,'post': post})
    else:
        # Post not found
        return HttpResponseBadRequest("Post not found")


@csrf_exempt
@require_POST
def toggle_follow(request, target_user_id):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'User not authenticated'})

    # Get current user ID
    current_user_id = request.user.id

    # Execute the toggle_follow SQL function
    with connection.cursor() as cursor:
        cursor.execute('BEGIN; '
                       'SELECT toggle_follow(%s, %s); '
                       'COMMIT;', [current_user_id, target_user_id])

    # Get the updated follow status
    with connection.cursor() as cursor:
        cursor.execute('SELECT check_follow_status(%s, %s);', [current_user_id, target_user_id])
        is_following = cursor.fetchone()[0]

    # Return the updated follow status and user data
    user_data = {
        'id': target_user_id,  # Assuming you have the user ID in your data
        'is_following': is_following,
    }

    return JsonResponse({'success': True, 'user_data': user_data})


def profile_view(request, user_id):
    # Get the user details
 # Get the user details and follower count
    with connection.cursor() as cursor:
        cursor.execute('SELECT * FROM get_current_user_profile_with_followers(%s, %s);', [request.user.id, user_id])
        user_data = cursor.fetchone()
    is_following = False
    if request.user.is_authenticated:
        with connection.cursor() as cursor:
            cursor.execute('SELECT check_follow_status(%s, %s);', [request.user.id, user_id])
            is_following = cursor.fetchone()[0]

    print(user_data)
    context = {
        'user_data': {
            'id': user_data[0],
            'username': user_data[1],
            'email': user_data[2],
            'bio': user_data[3],
            'followers_count': user_data[4],
        },
        'is_following': is_following,
        # Add other context data as needed
    }
    print(user_profile)
    # Check if the current user is following the target user
    
    return render(request, 'profile.html', context)

@login_required
def edit_comment(request, post_id, comment_id):
    # Fetch the comment details
    with connection.cursor() as cursor:
        cursor.callproc('get_comment_details', [comment_id])
        comment_data = cursor.fetchone()
    if request.method == 'POST':
        # Handle the form submission for editing the comment
        content = request.POST.get('content')

        with connection.cursor() as cursor:
            cursor.callproc('edit_comment', [comment_id, content])

        return redirect('post_details', post_id)
    print(comment_data)
    # Prepare the context for rendering the edit comment form
    context = {
        'comment': {
            'comment_id': comment_data[0],
            'content': comment_data[1],
            'created_at': comment_data[2],
            'post_id': comment_data[3],
        }
    }

    return render(request, 'edit_comment.html', context)
@login_required
def delete_comment(request, post_id, comment_id):
    # Fetch the comment details
    print(post_id)
    with connection.cursor() as cursor:
        cursor.callproc('delete_comment', [comment_id])

    return redirect('post_details', post_id)


@login_required
def following(request):
    current_user_id = request.user.id
    with connection.cursor() as cursor:
            cursor.callproc('get_following_users', [current_user_id])
            following_data = cursor.fetchall()

    # Convert comments data to a list of dictionaries
    following_users = [
    {
        'user_id': follow[0],
        'user_username': follow[1],
    }
        for follow in following_data
    ]

    print(following_users)
    context = {
        'following_users': following_users,
    }

    return render(request, 'following.html', context)

