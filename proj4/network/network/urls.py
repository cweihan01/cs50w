
from django.urls import path

from . import views

urlpatterns = [
    # API routes
    path("profile/<str:username>/follow", views.follow, name="follow"),
    path("posts/edit/<int:post_id>", views.edit, name="edit"),
    path("posts/like/<int:post_id>", views.like, name="like"),

    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("new", views.new_post, name="new_post"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),
]
