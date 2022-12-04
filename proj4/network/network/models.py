from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields.related_descriptors import create_forward_many_to_many_manager


class User(AbstractUser):
    pass
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }


class Post(models.Model):
    """
    Model that stores a post.
    Likes are stored in a separate model, else each time a user likes a post the post will be modified.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=128)
    contents = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Post {self.id} made by {self.user}: '{self.title}' at {self.created}"

    def serialize(self):
        return {
            "user_id": self.user.id,
            "title": self.title,
            "contents": self.contents,
            "created": self.created.strftime("%b. %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m."),
            "modified": self.modified.strftime("%b. %d, %Y, %I:%M %p").replace("AM", "a.m.").replace("PM", "p.m.")
            # is there a better way to convert datetimefield to string... need check how django does it
        }
    
    def add_like(self, user):
        """Adds `user` to Post `likes` and `liked_by`"""
        self.liked_by.add(user)
        self.likes += 1
        self.save()

    def remove_like(self, user):
        """Remove `user` from Post `likes` and `liked_by`"""
        self.liked_by.remove(user)
        self.likes -= 1
        self.save()


class FollowUserManager(models.Manager):
    def serialize_following(self, profile):
        """ Returns a list of `User` id that `profile` is following. """
        following = super(FollowUserManager, self).get_queryset().filter(user=profile)
        return [f.profile.id for f in following]

    def serialize_followers(self, profile):
        """ Returns a list of `User` id that is following `profile`. """
        followers = super(FollowUserManager, self).get_queryset().filter(profile=profile)
        return [f.user.id for f in followers]

class FollowUser(models.Model):
    """
    Model that saves the following/followed relationship between users.
    `user` is the user that is following.
    `profile` is the user that is being followed.
    """
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="following")
    profile = models.ForeignKey(User, on_delete=models.PROTECT, related_name="followers")

    objects = FollowUserManager()

    def __str__(self):
        return f"{self.user} is following {self.profile}"


class LikeManager(models.Manager):
    def serialize_likes(self, post):
        objects = super(LikeManager, self).get_queryset().filter(post=post)
        return [o.user.username for o in objects]

# Add new model for likes
class Like(models.Model):
    """
    Model that stores a User's like for a Post.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="liked")
    created = models.DateTimeField(auto_now_add=True)

    objects = LikeManager()

    def __str__(self):
        return f"{self.user} liked {self.post} at {self.created}"
