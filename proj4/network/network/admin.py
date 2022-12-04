from django.contrib import admin

from .models import User, Post, FollowUser, Like

# Register your models here.
admin.site.register(User)
admin.site.register(Post)
admin.site.register(FollowUser)
admin.site.register(Like)