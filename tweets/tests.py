from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Like, Tweet

User = get_user_model()


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@email.com", password="testpass"
        )
        self.client.login(username="test", password="testpass")
        self.url = reverse("tweets:create")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tweets/tweets_create.html")

    def test_success_post(self):
        test_post = {"content": "this is a test"}
        response = self.client.post(self.url, test_post)
        self.assertTrue(Tweet.objects.filter(content=test_post["content"]).exists())
        self.assertRedirects(
            response,
            reverse("accounts:home"),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_failure_post_with_empty_content(self):
        post_without_content = {"content": ""}
        response = self.client.post(self.url, post_without_content)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Tweet.objects.filter(content=post_without_content["content"]).exists()
        )
        self.assertFormError(response, "form", "content", "このフィールドは必須です。")

    def test_failure_post_with_too_long_content(self):
        post_long = {"content": "a" * 141}  # dict型{}
        response = self.client.post(self.url, post_long)  # postの引数になれるのはdict,クエリではない
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(content=post_long["content"]).exists())
        self.assertFormError(
            response,
            "form",
            "content",
            "この値は 140 文字以下でなければなりません( "
            + str(len(post_long["content"]))
            + " 文字になっています)。",
        )


class TestTweetDetailView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="test", email="test@email.com", password="testpass"
        )
        self.client.login(username="test", password="testpass")
        self.tweet = Tweet.objects.create(user=self.user, content="this is a test")

    def test_success_get(self):
        response = self.client.get(
            reverse("tweets:detail", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.tweet, response.context["tweet"])


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="test1", email="test@email.com", password="testpass1"
        )
        self.user2 = User.objects.create_user(
            username="test2", email="test2@test.com", password="testpass2"
        )
        test_post = {"content": "this is a test"}
        Tweet.objects.create(user=self.user1, content=test_post["content"])

    def test_success_post(self):
        self.client.login(username="test1", password="testpass1")
        tweet = Tweet.objects.get(content="this is a test")
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tweet.objects.filter(content="this is a test").exists())

    def test_failure_post_with_not_exist_tweet(self):
        self.client.login(username="test1", password="testpass1")
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 100}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Tweet.objects.filter(content="this is a test").exists)

    def test_failure_post_with_incorrect_user(self):
        self.client.login(username="test2", password="testpass2")
        tweet = Tweet.objects.get(content="this is a test")
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": tweet.pk}))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Tweet.objects.filter(content="this is a test").exists())


class TestFavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="example_tweet")

    def test_success_post(self):
        response = self.client.post(
            reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(target_tweet=self.tweet).exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:like", kwargs={"pk": 0}))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Like.objects.filter(target_tweet=self.tweet).exists())

    def test_failure_post_with_favorited_tweet(self):
        Like.objects.create(target_tweet=self.tweet, user=self.user)
        response = self.client.post(
            reverse("tweets:like", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.filter(target_tweet=self.tweet).count(), 1)


class TestUnfavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="example_tweet")
        Like.objects.create(target_tweet=self.tweet, user=self.user)

    def test_success_post(self):
        response = self.client.post(
            reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(target_tweet=self.tweet).exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:unlike", kwargs={"pk": 0}))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Like.objects.filter(target_tweet=self.tweet).exists())

    def test_failure_post_with_unfavorited_tweet(self):
        Like.objects.filter(target_tweet=self.tweet, user=self.user).delete()
        response = self.client.post(
            reverse("tweets:unlike", kwargs={"pk": self.tweet.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Like.objects.filter(target_tweet=self.tweet).exists())
