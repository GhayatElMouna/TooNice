from django.core.management.base import BaseCommand
from BlogApp.models import Article

def chunked(iterable, size):
    it = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(size):
                chunk.append(next(it))
        except StopIteration:
            if chunk:
                yield chunk
            break
        yield chunk


class Command(BaseCommand):
    help = 'Compute content-based recommendations for articles using TF-IDF (requires scikit-learn)'

    def add_arguments(self, parser):
        parser.add_argument('--top', type=int, default=5, help='Number of recommendations to store per article')

    def handle(self, *args, **options):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import linear_kernel
        except Exception as e:
            self.stderr.write('scikit-learn is required: pip install scikit-learn')
            raise e

        top_k = options.get('top', 5)

        qs = Article.objects.all().only('id_article', 'titre', 'description')
        articles = list(qs)
        if not articles:
            self.stdout.write('No articles found.')
            return

        # Build corpus
        corpus = []
        id_map = []
        for a in articles:
            text = (a.titre or '') + ' ' + (a.description or '')
            corpus.append(text)
            id_map.append(a.pk)

        # Compute TF-IDF
        vect = TfidfVectorizer(stop_words='english', max_df=0.85)
        X = vect.fit_transform(corpus)

        # Cosine similarities
        sim_matrix = linear_kernel(X, X)

        # For each article compute top-k similar articles
        for idx, a in enumerate(articles):
            row = sim_matrix[idx]
            # get indices sorted by similarity (descending) excluding itself
            similar_indices = row.argsort()[::-1]
            recs = []
            for j in similar_indices:
                if j == idx:
                    continue
                score = float(row[j])
                if score <= 0:
                    continue
                recs.append({'id': id_map[j], 'score': round(score, 5)})
                if len(recs) >= top_k:
                    break

            a.recommendations = recs
            a.save(update_fields=['recommendations'])

        self.stdout.write(self.style.SUCCESS('Recommendations computed and stored.'))
