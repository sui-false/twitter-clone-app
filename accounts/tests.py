from django.contrib.auth import SESSION_KEY, get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from mysite import settings
from tweets.models import Tweet

from .models import FriendShip

User = get_user_model()


class TestSignUpView(TestCase):
    def test_success_get(self):

        response = self.client.get(reverse("accounts:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        data_post = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        # user_record_count = User.objects.all().count()
        # print(user_record_count)
        response = self.client.post(reverse("accounts:signup"), data_post)
        self.assertRedirects(
            response, reverse("accounts:home"), status_code=302, target_status_code=200
        )
        self.assertTrue(
            User.objects.filter(username="sample", email="email@example.com").exists()
        )

        user_record_count = User.objects.all().count()
        print(user_record_count)
        print(User.objects.all().count())
        self.assertTrue(user_record_count + 1, User.objects.all().count())
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        data_empty_form = {
            "email": "",
            "username": "",
            "password1": "",
            "password2": "",
        }

        response = self.client.post(reverse("accounts:signup"), data_empty_form)
        self.assertEquals(response.status_code, 200)

        self.assertFalse(User.objects.exists())
        # userにダブリがないかを確認
        self.assertFormError(response, "form", "username", "このフィールドは必須です。")
        self.assertFormError(response, "form", "email", "このフィールドは必須です。")
        self.assertFormError(response, "form", "password1", "このフィールドは必須です。")
        self.assertFormError(response, "form", "password2", "このフィールドは必須です。")

    def test_failure_post_with_empty_username(self):

        data_empty_username = {
            "email": "email@example.com",
            "username": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), data_empty_username)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="email@example.com").exists())
        # self.assertFalse(User.objects.exists())
        # userにダブリがないかを確認
        self.assertFormError(response, "form", "username", "このフィールドは必須です。")

    def test_failure_post_with_empty_email(self):
        data_empty_email = {
            "email": "",
            "username": "sample",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(reverse("accounts:signup"), data_empty_email)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        # userにダブリがないかを確認
        self.assertFormError(response, "form", "email", "このフィールドは必須です。")

    def test_failure_post_with_empty_password(self):
        data_empty_password = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "testpassword",
            "password2": "",
        }
        response = self.client.post(reverse("accounts:signup"), data_empty_password)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFormError(response, "form", "password2", "このフィールドは必須です。")

    def test_failure_post_with_duplicated_user(self):
        data_duplicated_user = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create(username=data_duplicated_user["username"])
        response = self.client.post(reverse("accounts:signup"), data_duplicated_user)
        self.assertEquals(response.status_code, 200)

        self.assertFormError(response, "form", "username", "同じユーザー名が既に登録済みです。")

    def test_failure_post_with_invalid_email(self):
        data_invalid_email = {
            "email": "email",
            "sername": "sample",
            "password1": "password1234",
            "password2": "password1234",
        }
        response = self.client.post(reverse("accounts:signup"), data_invalid_email)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFormError(response, "form", "email", "有効なメールアドレスを入力してください。")

    def test_failure_post_with_too_short_password(self):
        data_short_password = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "pu",
            "password2": "pu",
        }
        response = self.client.post(reverse("accounts:signup"), data_short_password)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(User.objects.exists())
        self.assertFormError(
            response, "form", "password2", "このパスワードは短すぎます。最低 8 文字以上必要です。"
        )

    def test_failure_post_with_password_similar_to_username(self):
        data_similar_to_username = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "sample001",
            "password2": "sample001",
        }

        response = self.client.post(
            reverse("accounts:signup"), data_similar_to_username
        )
        self.assertFalse(User.objects.exists())
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, "form", "password2", "このパスワードは ユーザー名 と似すぎています。")

    def test_failure_post_with_only_numbers_password(self):
        data_only_numbers_password = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "12345678",
            "password2": "12345678",
        }
        response = self.client.post(
            reverse("accounts:signup"), data_only_numbers_password
        )
        self.assertFalse(User.objects.exists())
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, "form", "password2", "このパスワードは数字しか使われていません。")

    def test_failure_post_with_mismatch_password(self):
        data_mismatch_password = {
            "email": "email@example.com",
            "username": "sample",
            "password1": "testpassword",
            "password2": "testpasswora",
        }
        response = self.client.post(reverse("accounts:signup"), data_mismatch_password)
        self.assertFalse(User.objects.exists())
        self.assertEquals(response.status_code, 200)
        self.assertFormError(response, "form", "password2", "確認用パスワードが一致しません。")


class TestHomeView(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.client.force_login(user)

    def test_success_get(self):
        response = self.client.get(reverse("accounts:home"))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/home.html")
        self.assertQuerysetEqual(
            response.context["tweets"], Tweet.objects.order_by("created_at")
        )


class TestLoginView(TestCase):
    def setUp(self):

        User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.login_url = reverse(settings.LOGIN_URL)

    def test_success_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):

        data = {
            "username": "sample",
            "password": "testpassword",
        }
        response = self.client.post(self.login_url, data)
        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        data_not_exist = {
            "username": "not_exist_sample",
            "password": "testpassword",
        }
        response = self.client.post(self.login_url, data_not_exist)
        self.assertEquals(response.status_code, 200)
        self.assertFormError(
            response, "form", "", "正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        data_empty_password = {
            "username": "sample",
            "password": "",
        }
        response = self.client.post(self.login_url, data_empty_password)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "このフィールドは必須です。")
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.client.force_login(user)

    def test_success_get(self):
        response = self.client.get(reverse("accounts:logout"))
        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )

        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def test_success_get(self):
        pass


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="sample2", email="sample2@example.com", password="testpassword2"
        )
        self.client.force_login(self.user1)

    def test_success_post(self):
        self.assertEqual(FriendShip.objects.all().count(), 0)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user1.id])
        )
        self.assertEqual(response.context["followings_num"], 0)  # フォロー前はだれもフォローしていない
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": "sample2"}), None
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("accounts:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            FriendShip.objects.filter(
                following=self.user2, follower=self.user1
            ).exists()
        )
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user1.id])
        )
        self.assertEqual(
            response.context["followings_num"], 1
        )  # フォロー後はuser2一人をフォローしているので1
        self.assertEqual(FriendShip.objects.all().count(), 1)

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": "test"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.exists())

    def test_failure_post_with_self(self):
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": self.user1.username})
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FriendShip.objects.exists())
        messages = list(get_messages(response.wsgi_request))
        message = str(messages[0])
        self.assertEqual(message, "自分自身はフォローできません。")

    def test_failure_double_follow(self):
        # 複数のFriendShipを作成することができないことを確かめるテスト
        FriendShip.objects.create(following=self.user2, follower=self.user1)
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": "sample2"}), None
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user1.id])
        )
        self.assertEqual(
            response.context["followings_num"], 1
        )  # フォロー後はuser2一人をフォローしているので1
        self.assertEqual(FriendShip.objects.all().count(), 1)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="sample2", email="sample2@example.com", password="testpassword2"
        )
        FriendShip.objects.create(following=self.user2, follower=self.user1)
        self.client.force_login(self.user1)

    def test_success_post(self):
        self.assertEqual(FriendShip.objects.all().count(), 1)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user1.id])
        )
        self.assertEqual(response.context["followings_num"], 1)  # フォロー解除前はuser2一人をフォロー中
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        )
        self.assertRedirects(
            response,
            reverse("accounts:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(FriendShip.objects.exists())
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user1.id])
        )
        self.assertEqual(response.context["followings_num"], 0)  # 解除後は誰もフォローしていないので0
        self.assertEqual(FriendShip.objects.all().count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": "test"})
        )
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": self.user1.username})
        )
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        message = str(messages[0])
        self.assertEqual(message, "無効な操作です。")


class TestFollowingListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="sample2", email="sample2@example.com", password="testpassword2"
        )
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(
            reverse("accounts:following_list", kwargs={"username": "sample"})
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user.id])
        )
        self.assertEqual(response.context["followings_num"], 0)
        self.assertEqual(FriendShip.objects.all().count(), 0)
        FriendShip.objects.create(following=self.user, follower=self.user2)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user.id])
        )
        self.assertEqual(response.context["followers_num"], 1)
        self.assertEqual(FriendShip.objects.all().count(), 1)


class TestFollowerListView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="sample", email="sample@example.com", password="testpassword"
        )
        self.user2 = User.objects.create_user(
            username="sample2", email="sample2@example.com", password="testpassword2"
        )
        self.client.force_login(self.user)

    def test_success_get(self):
        response = self.client.get(
            reverse("accounts:follower_list", kwargs={"username": "sample"})
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user.id])
        )
        self.assertEqual(response.context["followers_num"], 0)
        self.assertEqual(FriendShip.objects.all().count(), 0)

        FriendShip.objects.create(following=self.user2, follower=self.user)
        response = self.client.get(
            path=reverse("accounts:user_profile", args=[self.user.id])
        )
        self.assertEqual(response.context["followings_num"], 1)
        self.assertEqual(FriendShip.objects.all().count(), 1)
