from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView

from .forms import TweetForm
from .models import Like, Tweet


class TweetCreateView(LoginRequiredMixin, CreateView):
    template_name = "tweets/tweets_create.html"
    form_class = TweetForm
    success_url = reverse_lazy("accounts:home")

    def form_valid(self, form):  # これで投稿者を紐づけてる
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(DetailView):
    template_name = "tweets/tweet_detail.html"
    model = Tweet
    context_object_name = "tweet"
    # その場で入力されたオブジェクトの名前をつけて、詳細表示できるようにしている

    # 以下、tweet_detailでいいねの県巣を管理できるようにデータをとってきている
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["liked_list"] = self.request.user.like_set.values_list(
            "target_tweet", flat=True
        )  # fllatでリスト化している
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    template_name = "tweets/tweet_delete.html"
    model = Tweet
    success_url = reverse_lazy("accounts:home")

    def test_func(self):
        current_user = self.request.user
        tweet_user = self.get_object().user
        return current_user.pk == tweet_user.pk


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *arg, **kwargs):
        user = request.user
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.get_or_create(user=user, target_tweet=tweet)
        context = {
            "like_count": tweet.like_set.count(),
            "tweet_pk": tweet.pk,
        }

        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *arg, **kwargs):
        user = request.user
        tweet = get_object_or_404(Tweet, pk=kwargs["pk"])
        Like.objects.filter(target_tweet=tweet, user=user).delete()
        context = {
            "like_count": tweet.like_set.count(),
            "tweet_pk": tweet.pk,
        }
        return JsonResponse(context)
