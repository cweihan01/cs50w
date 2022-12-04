import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.utils import DJANGO_VERSION_PICKLE_KEY, ProgrammingError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators import csrf
from django.views.decorators.csrf import csrf_exempt

from .forms import NewPostForm
from .models import FollowUserManager, User, Post, FollowUser, Like


def index(request):
    # Access posts
    posts = Post.objects.all().order_by("-created")
    return render(request, "network/index.html", {
        "posts": posts
    })


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
        if request.user.is_authenticated:
            return redirect(reverse("index"))
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure username and email are provided
        if not username:
            return render(request, "network/register.html", {
                "message": "Username cannot be empty."
            })
        elif not email:
            return render(request, "network/register.html", {
                "message": "Email cannot be empty."
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if not password or not confirmation:
            return render(request, "network/register.html", {
                "message": "Password cannot be empty."
            })
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
        if request.user.is_authenticated:
            return redirect(reverse("index"))
        return render(request, "network/register.html")


@login_required(login_url='/login')
def new_post(request):
    if request.method == "POST":
        
        # Validate form data
        title = request.POST["title"]
        contents = request.POST["contents"]
        if not title or not contents:
            return render(request, "network/new_post.html", {
                "message": "Fields cannot be empty!"
            })

        # Save new Form instance
        Post.objects.create(user=request.user, title=title, contents=contents)
        
        # Redirect to index page
        return redirect(reverse("index"))
    
    else:
        return render(request, "network/new_post.html")


def profile(request, username):
    """
    Displays a user's profile.
    `profile` is the user we are querying.
    `user` is the current user (if logged in).
    """
    
    # Obtain current profile
    profile = User.objects.get(username=username)
    
    # Obtain profile's posts
    posts = profile.posts.all().order_by("-created")

    return render(request, "network/profile.html", {
        "profile": profile,
        "posts": posts
    })


@login_required(login_url='/login')
def following(request):
    """ Displays list of posts the user from accounts the user follows. """

    # Obtain all accounts that user follows
    users_following = FollowUser.objects.filter(user=request.user).values_list("profile", flat=True)

    # Obtain all posts that user follows
    posts_following = Post.objects.filter(user__in=users_following).order_by("-created")

    return render(request, "network/following.html", {
        "posts": posts_following
    })


# API Routes
@csrf_exempt
def follow(request, username):
    """
    API that does:
    1. dynamically update following/followers count on a profile page when loaded
    2. handles the follow/unfollow button
    """
    # Get profile
    profile = User.objects.get(username=username)

    # Get the following and followers of `profile`
    if request.method == "GET":
        # These variables give a list of `User` id
        following = FollowUser.objects.serialize_following(profile)
        followers = FollowUser.objects.serialize_followers(profile)
        
        # For unique logged in users, check if `user` following `profile`
        if request.user.is_authenticated and request.user != profile:
            try:
                FollowUser.objects.get(user=request.user, profile=profile)
                is_following = True
            except FollowUser.DoesNotExist:
                is_following = False

            return JsonResponse({
                "following": following,
                "followers": followers,
                "is_following": is_following,
                "user_logged_in": True,
            })

        # For anonymous users, unable to check if `user` is following `profile`
        else:
            return JsonResponse({
                "following": following,
                "followers": followers,
                "user_logged_in": False
            })

    # Update database when `user` follows `profile`
    elif request.method == "PUT":
        try:
            FollowUser.objects.get(user=request.user, profile=profile).delete()
            return JsonResponse({"is_following": False})
        except FollowUser.DoesNotExist:
            FollowUser.objects.create(user=request.user, profile=profile)
            return JsonResponse({"is_following": True})


@csrf_exempt
def edit(request, post_id):
    """
    API that allows a user to edit their own post.
    """
    post = Post.objects.get(id=post_id)

    # First validate that the post is indeed made by user (in case user accesses API manually)
    if post.user != request.user:
        return JsonResponse({"error": "You are not authorised for this action."})

    # User pressed edit button, retrieve Post to pre-fill form
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # User submitted edit form
    elif request.method == "POST":
        # Get what user typed in edit form
        body = json.loads(request.body)
        
        # Update database
        post.title = body["title"]
        post.contents = body["contents"]
        post.save()

        return JsonResponse({
            "success": True,
            "post": post.serialize()
        })


@csrf_exempt
def like(request, post_id):
    """
    API that allows a user to like a post.
    """
    try:
        post = Post.objects.get(id=post_id)
        likes = Like.objects.serialize_likes(post)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post does not exist."})

    # Send data to client
    if request.method == "GET":
        return JsonResponse({
            "like_count": len(likes),
            "is_liked": request.user.username in likes if request.user.is_authenticated else False,
            "liked_by": likes
        })

    # Allow users to like a post
    elif request.method == "PUT":
        # Only logged in users can like a post
        if request.user.is_authenticated:
            # If user already liked post, unlike it
            if request.user.username in likes:
                Like.objects.get(post=post, user=request.user).delete()
                return JsonResponse({"post_liked": False})
            else:
                Like.objects.create(post=post, user=request.user)
                return JsonResponse({"post_liked": True})

        # Anonymous users will be thrown an error
        else:
            return JsonResponse({"error": "You must log in to like a post!"})