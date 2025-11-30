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
from django.shortcuts import get_object_or_404
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from .ai_filtrer.toxicity_detector import contains_inappropriate  # ⚡ Corrige le nom exact du dossier






'''def check_message(request):
    if request.method == "POST":
        message = request.POST.get("message", "")

        if contains_inappropriate(message):
            return JsonResponse(
                {"error": "Your message contains inappropriate content"},
                status=400
            )

        return JsonResponse({"success": True})'''









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


def search_articles(request):
    """API endpoint for searching articles by title, description or author.
    Returns JSON with a small list of matches (id, title, snippet, url).
    """
    q = request.GET.get('q', '').strip()
    results = []
    if q:
        qs = Article.objects.filter(
            Q(titre__icontains=q) | Q(description__icontains=q) | Q(user__username__icontains=q)
        ).distinct()[:10]
        for a in qs:
            results.append({
                'id': a.pk,
                'title': a.titre,
                'snippet': (a.description[:120] + '...') if a.description and len(a.description) > 120 else (a.description or ''),
                'url': reverse('article_details_view', args=[a.pk])
            })

    return JsonResponse({'results': results})

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
    template_name = "BlogApp/article_detail.html"
    context_object_name = "article"

    def get(self, request, *args, **kwargs):
        article = self.get_object()

        # 🔥 Incrémenter les vues si c'est une vidéo
        if article.type_media == "video":
            article.nb_vues += 1
            article.save(update_fields=["nb_vues"])

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.get_object()

        # Build recommended article objects preserving stored order
        recs = []
        try:
            stored = article.recommendations or []
            ids = [r.get('id') for r in stored if r.get('id')]
            if ids:
                qs = Article.objects.filter(pk__in=ids)
                qs_map = {a.pk: a for a in qs}
                for i in ids:
                    a = qs_map.get(i)
                    if a:
                        recs.append(a)
            # Indicate source as stored when available
            recommendations_source = 'stored'
        except Exception:
            recs = []
            recommendations_source = None

        # If there are no stored recommendations, compute lightweight recommendations
        # on-the-fly so the site shows suggestions immediately for testing.
        if not recs:
            try:
                # Try to use scikit-learn TF-IDF for a quick similarity computation
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import linear_kernel

                # Limit candidate pool to recent N articles to avoid heavy work
                CANDIDATE_LIMIT = 500
                candidates = list(Article.objects.exclude(pk=article.pk).order_by('-date_publication')[:CANDIDATE_LIMIT])
                if candidates:
                    corpus = [ (article.titre or '') + ' ' + (article.description or '') ] + [ (c.titre or '') + ' ' + (c.description or '') for c in candidates ]
                    vect = TfidfVectorizer(stop_words=None, ngram_range=(1,2), max_df=0.85, min_df=1)
                    X = vect.fit_transform(corpus)
                    # similarity of first vector (article) against others
                    sim = linear_kernel(X[0:1], X[1:]).flatten()
                    indexed = list(enumerate(sim))
                    indexed.sort(key=lambda x: x[1], reverse=True)
                    top_k = 5
                    recs = []
                    for idx, score in indexed[:top_k]:
                        if score <= 0:
                            continue
                        recs.append(candidates[idx])
                    recommendations_source = 'computed'
            except Exception:
                # Fallback: simple icontains search on title/description/author
                terms = (article.titre or '')[:200].split()
                q = Q()
                for t in terms[:5]:
                    q |= Q(titre__icontains=t) | Q(description__icontains=t) | Q(user__username__icontains=t)
                qs_fb = Article.objects.filter(q).exclude(pk=article.pk).distinct()[:5]
                recs = list(qs_fb)
                recommendations_source = 'fallback'

        ctx['recommended_articles'] = recs
        ctx['recommendations_source'] = recommendations_source if 'recommendations_source' in locals() else None
        return ctx

  # IA ⚡


class ArticleCreateView(LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('article_list_view')

    def form_valid(self, form):
        # Associer l'utilisateur à l'article
        form.instance.user = self.request.user

        # Profil utilisateur (pour blocage)
        profile = self.request.user.userprofile

        # 1️⃣ Vérifier si l'utilisateur est déjà bloqué
        if profile.is_blocked():
            messages.error(
                self.request,
                f"🚫 Vous êtes bloqué jusqu'au {profile.blocked_until.strftime('%d/%m/%Y %H:%M')}."
            )
            return redirect('article_list_view')

        # 2️⃣ Vérification IA sur titre + description
        title = form.cleaned_data.get("titre", "")
        description = form.cleaned_data.get("description", "")

        if contains_inappropriate(title) or contains_inappropriate(description):
            # Compter les tentatives
            profile.bad_post_attempts += 1
            profile.save()

            # Bloquer si 2 tentatives
            if profile.bad_post_attempts >= 2:
                profile.block_for_two_days()
                messages.error(
                    self.request,
                    "🚫 Vous avez été bloqué pendant 2 jours pour avoir tenté de publier du contenu inapproprié."
                )
                return redirect('article_list_view')

            # Première tentative → simple avertissement
            messages.warning(
                self.request,
                "⚠ Contenu inapproprié détecté par l'IA. Votre article n'a pas été publié."
            )
            return redirect('article_list_view')

        # 3️⃣ Si tout est propre → publier l'article
        response = super().form_valid(form)

        # Réinitialiser les mauvaises tentatives si OK
        profile.bad_post_attempts = 0
        profile.save()

        return response






class ArticleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    success_url = reverse_lazy('article_list_view')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def form_valid(self, form):
        obj = form.instance
        profile = self.request.user.userprofile

        # Vérification du contenu via IA
        if contains_inappropriate(form.instance.description):
            profile.bad_post_attempts += 1
            profile.save()

            if profile.bad_post_attempts >= 2:
                profile.block_for_two_days()
                messages.error(
                    self.request,
                    "🚫 Vous avez été bloqué pendant 2 jours pour contenu inapproprié."
                )
                return redirect('article_list_view')

            messages.warning(self.request, "⚠ Contenu inapproprié détecté par IA !")
            return redirect('article_list_view')

        # Gestion propre du fichier média
        try:
            old = Article.objects.get(pk=obj.pk)
        except Article.DoesNotExist:
            old = None

        new_file = form.cleaned_data.get('chemin_media')

        response = super().form_valid(form)

        if new_file and old and old.chemin_media and old.chemin_media.name != obj.chemin_media.name:
            try:
                old.chemin_media.delete(save=False)
            except Exception:
                pass

        messages.success(self.request, 'Article mis à jour avec succès.')
        
        # Réinitialiser le compteur si tout va bien
        profile.bad_post_attempts = 0
        profile.save()

        return response

class ArticleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Article
    success_url = reverse_lazy('article_list_view')

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user
