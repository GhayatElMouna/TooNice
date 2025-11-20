from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Article
from .forms import ArticleForm
from django.views.generic import TemplateView
from django.contrib import messages

# Like / Dislike
@login_required
@require_POST
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    user = request.user

    # If user already liked -> remove like
    if article.liked_by.filter(pk=user.pk).exists():
        article.liked_by.remove(user)
    else:
        # If user had disliked before, remove that dislike
        if article.disliked_by.filter(pk=user.pk).exists():
            article.disliked_by.remove(user)
        article.liked_by.add(user)

    # Update counters from relations
    article.nb_likes = article.liked_by.count()
    article.nb_dislikes = article.disliked_by.count()
    article.save()
    return redirect('article_list_view')

@login_required
@require_POST
def dislike_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    user = request.user

    # If user already disliked -> remove dislike
    if article.disliked_by.filter(pk=user.pk).exists():
        article.disliked_by.remove(user)
    else:
        # If user had liked before, remove that like
        if article.liked_by.filter(pk=user.pk).exists():
            article.liked_by.remove(user)
        article.disliked_by.add(user)

    # Update counters from relations
    article.nb_likes = article.liked_by.count()
    article.nb_dislikes = article.disliked_by.count()
    article.save()
    return redirect('article_list_view')

# Home view
def home_view(request):
    return render(request, 'BlogApp/home.html')

# List simple view
def listArticles(request):
    articles = Article.objects.all()
    return render(request, 'BlogApp/list.html', {'articles': articles})

# Class-based views
class ArticleListView(ListView):
    model = Article
    template_name = 'BlogApp/list.html'
    context_object_name = 'articles'
    # public list: any user can view all articles


class MyArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'BlogApp/list.html'
    context_object_name = 'articles'

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['page_title'] = 'My Articles'
        ctx['page_subtitle'] = 'Articles you created'
        return ctx


def blog_index(request):
    return render(request, 'BlogApp/blog_home.html')

class ArticleDetailView(DetailView):
    model = Article

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    # don't expose the user field in the form; attach it from request.user
    fields = ['titre', 'description', 'type_media', 'chemin_media']
    success_url = reverse_lazy('article_list_view')

    def form_valid(self, form):
        # set the current authenticated user as the article owner
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.instance.user = self.request.user
        return form

from django.contrib.auth.mixins import UserPassesTestMixin


class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('article_list_view')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def form_valid(self, form):
        # Preserve/replace media file cleanly: if a new file is uploaded, remove the old file
        obj = form.instance
        try:
            old = Article.objects.get(pk=obj.pk)
        except Article.DoesNotExist:
            old = None

        new_file = form.cleaned_data.get('chemin_media')

        response = super().form_valid(form)

        # After saving, if a new file was uploaded and an old file existed, delete the old file
        if new_file and old and old.chemin_media and old.chemin_media.name != obj.chemin_media.name:
            try:
                old.chemin_media.delete(save=False)
            except Exception:
                pass

        messages.success(self.request, 'Article mis à jour avec succès.')
        return response

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('article_list_view')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user
