from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import json
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import *

import datetime


def index(request):
    allPosts = Post.objects.all().order_by("date").reverse()
    paginator = Paginator(allPosts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, "network/index.html", {
        "posts": allPosts,
        "user": request.user,
        "page_obj": page
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

def newPost(request):
    if request.method == "POST":
        content = request.POST["content"]
        current_time = datetime.datetime.now().replace(microsecond=0)
        post = Post (
            content = content,
            owner = request.user,
            date = current_time
        )
        post.save()
        return HttpResponseRedirect(reverse("index"))
    

def edit(request, post_id):
    if request.method == "POST":
        post = Post.objects.get(pk = post_id)
        body = json.loads(request.body)
        post.content = body["content"]
        post.save()
        return JsonResponse({"message": "Change successful", "data": body["content"]})
    
def following(request):
    currUser = request.user

    # Get the list of users that the current user follows
    followed_users = Follow.objects.filter(follower=currUser).values_list('followed', flat=True)

    # Fetch posts only from followed users
    posts = Post.objects.filter(owner__in=followed_users).order_by('date')

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": posts,
        "user": currUser,
        "page_obj": page
    })

def profile(request, user_id):
    currUser = request.user
    user = User.objects.get(pk=user_id)
    followings = Follow.objects.filter(follower = user).values_list('followed', flat=True)
    followers = Follow.objects.filter(followed = user).values_list('follower', flat=True)

    posts = Post.objects.filter(owner = user).order_by('date').reverse()

    follows = currUser.id in followers

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "loadedUser": user,
        "user": currUser,
        "following": followings,
        "follower": followers,
        "posts": posts,
        "follows": follows,
        "page_obj": page
    })


def follow(request, user_id):
    currUser = request.user
    user = User.objects.get(pk = user_id)
    follow = Follow(
        follower = currUser,
        followed = user 
    )
    follow.save()
    return HttpResponseRedirect(reverse("profile", args=(user.id,)))


def unfollow(request, user_id):
    currUser = request.user
    user = User.objects.get(pk = user_id)
    print(user, currUser)
    follow = Follow.objects.filter(follower = currUser, followed = user)
   
    follow.delete()
    return HttpResponseRedirect(reverse("profile", args=(user.id,)))


def like(request, post_id):
    post = Post.objects.get(pk = post_id)
    post.likes.add(request.user)
    return JsonResponse({"message": "Like added!"})

def unlike(request, post_id):
    post = Post.objects.get(pk = post_id)
    post.likes.remove(request.user)
    return JsonResponse({"message": "Like removed!"})