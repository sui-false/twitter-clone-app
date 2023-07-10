from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(max_length=254, unique=True)
    followers = models.ManyToManyField(
        "User",
        verbose_name="フォローされているユーザー",
        through="FriendShip",
        related_name="followings",
        through_fields=("following", "follower"),
    )


class FriendShip(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="follow_unique"
            )
        ]
