from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
import json
from django.http import JsonResponse

from .models import User, Post, Follow, Like


def index(request):
    allPost = Post.objects.all().order_by("id").reverse()

    # paginator
    paginator = Paginator(allPost, 10)
    page_number = request.GET.get('page')
    posts_on_the_page = paginator.get_page(page_number)

    allLikes = Like.objects.all()

    whoYouLike = []

    try:
        for like in allLikes:
            if like.user.id == request.user.id:
                whoYouLike.append(like.post.id)
    except:
        whoYouLike = []

    return render(request, "network/index.html", {
        "allPost": allPost,
        "posts_on_the_page": posts_on_the_page,
        "whoYouLike": whoYouLike
    })


def newPost(request):
    if request.method == "POST":
        content = request.POST["content"]
        user = User.object.get(pk=request.user.id)
        post = Post(content=content, user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))


def edit(request, post_id):
    if request.method == "POST":
        data = json.loads(request.body)
        edit_post = Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"massage": "Change successful", "data": data["content"]})


def remove_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    like = Like.objects.filter(post=post, user=user)
    like.delete()
    return JsonResponse({"message": "like removed"})


def add_like(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    newLike = Like(user=user, post=post)
    newLike.save()
    return JsonResponse({"message": "Like added!"})


def profile(request, user_id):
    user = User.objects.get(pk=user_id)
    allPost = Post.objects.filter(user=user).order_by("id").reverse()

    following = Follow.objects.filter(user=user)
    followers = Follow.objects.filter(user_follower=user)

    try:
        checkFollow = followers.filter(
            user=User.object.get(pk=request.user.id))
        if len(checkFollow) != 0:
            isFollowing = True

        else:
            isFollowing = False

    except:
        isFollowing = False

    # paginator
    paginator = Paginator(allPost, 10)
    page_number = request.GET.get('page')
    posts_on_the_page = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "allPost": allPost,
        "posts_on_the_page": posts_on_the_page,
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
            if person.userfollower == post.user:
                followingPosts.append(post)

    # paginator
    paginator = Paginator(followingPosts, 10)
    page_number = request.GET.get('page')
    posts_on_the_page = paginator.get_page(page_number)

    return render(request, "network/followin.html", {
        "posts_on_the_page": posts_on_the_page
    })


def follow(request):
    userFollow = request.POST['userFollow']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=userFollow)
    f = Follow(user=currentUser, user_follower=userFollowData)
    f.save()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={"user_id": user_id}))


def unfollow(request):
    userFollow = request.POST['userFollow']
    currentUser = User.objects.get(pk=request.user.id)
    userFollowData = User.objects.get(username=userFollow)
    f = Follow.objects.get(user=currentUser, user_Follower=userFollowData)
    f.remove()
    user_id = userFollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={"user_id": user_id}))


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
