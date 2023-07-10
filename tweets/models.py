from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tweet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    target_tweet = models.ForeignKey(Tweet, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["target_tweet", "user"], name="like_unique"
            ),
        ]
