from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User, Post, Follow, Like
from django.contrib.auth.decorators import login_required

@login_required
def toggle_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        user = request.user
        liked = Like.objects.filter(user=user, post=post).exists()

        if liked:
            Like.objects.filter(user=user, post=post).delete()
        else:
            Like.objects.create(user=user, post=post)

        new_like_count = post.likes.count()
        return JsonResponse({'new_like_count': new_like_count, 'liked': not liked})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def edit(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)

        # Check if the current user is the author of the post
        if request.user != post.user:
            return JsonResponse({'error': 'You do not have permission to edit this post.'}, status=403)

        # Update the post content
        data = json.loads(request.body)
        post.content = data['content']
        post.save()

        # Return the updated content in the 'data' field
        return JsonResponse({'message': 'Post updated successfully.', 'data': post.content})
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

def index(request):
    allPosts = Post.objects.all().order_by("id").reverse()

    # Pagination
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    allLikes = Like.objects.all()

    whoYouLiked = []
    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLiked.append(like.post.id)
    except:
        whoYouLiked = []

    return render(request, "network/index.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "whoYouLiked": whoYouLiked
    })

@login_required
def newPost(request):
    if request.method == "POST":
        content = request.POST.get('content')
        if not content:
            return JsonResponse({'error': 'Post content cannot be empty.'}, status=400)
        try:
            user = request.user
            post = Post.objects.create(content=content, user=user)
            return HttpResponseRedirect(reverse('index'))
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    allPosts = Post.objects.filter(user=user).order_by("-id")

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    isFollowing = False
    if request.user.is_authenticated:
        isFollowing = followers.filter(user=request.user).exists()

    # Pagination
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "allPosts": allPosts,
        "posts_of_the_page": posts_of_the_page,
        "username": user.username,
        "following": following,
        "followers": followers,
        "isFollowing": isFollowing,
        "user_profile": user
    })

def following(request):
    currentUser = User.objects.get(pk=request.user.id)
    followingPeople = Follow.objects.filter(user=currentUser)
    allPosts = Post.objects.all().order_by('id').reverse()

    followingPosts = []

    for post in allPosts:
        for person in followingPeople:
            if person.user_follower == post.user:
                followingPosts.append(post)

    # Pagination
    paginator = Paginator(followingPosts, 10)
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page
    })



@login_required
def follow(request):
    if request.method == "POST":
        userfollow = request.POST.get('userfollow')
        if userfollow:
            current_user = request.user
            user_to_follow = get_object_or_404(User, username=userfollow)

            # Prevent users from following themselves
            if current_user == user_to_follow:
                return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

            # Check if the current user is already following the target user
            follow_relationship = Follow.objects.filter(user=current_user, user_follower=user_to_follow).first()

            if follow_relationship:
                # If a follow relationship exists, delete it (unfollow)
                follow_relationship.delete()
            else:
                # If no follow relationship exists, create one (follow)
                Follow.objects.create(user=current_user, user_follower=user_to_follow)

            return HttpResponseRedirect(reverse('profile', kwargs={'user_id': user_to_follow.id}))
        else:
            return JsonResponse({'error': 'User to follow not provided.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)



def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")