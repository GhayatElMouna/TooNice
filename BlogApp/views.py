from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.http import require_POST
from .models import Article
from .forms import ArticleForm

# Like / Dislike
@require_POST
def like_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.nb_likes += 1
    article.save()
    return redirect('article_list_view')

@require_POST
def dislike_article(request, pk):
    article = get_object_or_404(Article, pk=pk)
    article.nb_dislikes += 1
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

class ArticleDetailView(DetailView):
    model = Article

class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    fields = "__all__"
    success_url = reverse_lazy('article_list_view')

class ArticleUpdateView(UpdateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('article_list_view')

class ArticleDeleteView(DeleteView):
    model = Article
    success_url = reverse_lazy('article_list_view')
