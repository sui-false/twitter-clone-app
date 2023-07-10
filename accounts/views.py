from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from tweets.models import Tweet

from .forms import SignupForm
from .models import FriendShip, User


class SignupView(CreateView):

    form_class = SignupForm

    template_name = "accounts/signup.html"

    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):
        response = super().form_valid(form)

        user = self.object
        login(self.request, user)
        return response


class HomeView(ListView):
    template_name = "accounts/home.html"
    context_object_name = "tweets"
    model = Tweet
    # queryset = Tweet.objects.select_related("user").order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = self.request.user.like_set.values_list(
            "target_tweet", flat=True
        )  # fllatでリスト化している
        return context


class WelcomeView(TemplateView):
    template_name = "welcome/index.html"


class FollowView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/follow.html"
    model = FriendShip

    def post(self, request, *args, **kwargs):

        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if following == follower:
            messages.warning(request, "自分自身はフォローできません。")
            return render(request, "accounts/follow.html")
        elif FriendShip.objects.filter(following=following, follower=follower).exists():
            messages.warning(request, "すでにフォローしています。")
            return render(request, "accounts/follow.html")

        created = FriendShip.objects.create(following=following, follower=follower)
        if not created:
            messages.warning(request, "すでにフォローしています。")
        return HttpResponseRedirect(reverse_lazy("accounts:home"))


class UnFollowView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/unfollow.html"

    def post(self, request, *args, **kwargs):

        follower = User.objects.get(username=request.user.username)
        following = get_object_or_404(User, username=self.kwargs["username"])
        deleted = FriendShip.objects.filter(
            following=following, follower=follower
        ).delete()

        if deleted[1].get("accounts.FriendShip") == 1:
            return HttpResponseRedirect(reverse_lazy("accounts:home"))
        messages.warning(request, "無効な操作です。")
        return render(request, "accounts/unfollow.html")


class FollowingListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["my_followings"] = FriendShip.objects.select_related("following").filter(
            follower__username=self.kwargs["username"]
        )
        # 自分のフォローしている人を取得
        return ctx


class FollowerListView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["my_followers"] = FriendShip.objects.select_related("follower").filter(
            following__username=self.kwargs["username"]
        )
        return ctx


class UserProfileView(LoginRequiredMixin, DetailView):
    template_name = "accounts/profile.html"
    model = User
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        user = self.object

        ctx = super().get_context_data(**kwargs)
        ctx["tweets"] = (
            Tweet.objects.select_related("user")
            .filter(user=user)
            .order_by("-created_at")
        )
        ctx["followings_num"] = FriendShip.objects.filter(follower=user).count()
        ctx["followers_num"] = FriendShip.objects.filter(following=user).count()
        ctx["connected"] = FriendShip.objects.filter(
            following=user, follower=self.request.user
        ).exists()

        return ctx
