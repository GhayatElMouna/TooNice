"""
Script pour s'assurer que seulement 2-3 logements ont le badge "Nouveau"
"""
import os
import sys
import django
from datetime import timedelta

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TooNice.settings')
django.setup()

from AccomodationApp.models import Accommodation
from django.utils import timezone
import random

def fix_recent_badges():
    """S'assure que seulement 2-3 logements sont très récents"""
    
    maintenant = timezone.now()
    date_limite = maintenant - timedelta(days=2)
    
    # Récupérer tous les logements actifs
    accommodations = list(Accommodation.objects.filter(est_actif=True))
    
    # Trier par date d'ajout
    accommodations.sort(key=lambda x: x.date_ajoutee, reverse=True)
    
    # Garder seulement 2-3 très récents (0-1 jours)
    tres_recents = random.sample(accommodations[:10], min(3, len(accommodations[:10])))
    
    updated = 0
    for acc in accommodations:
        if acc in tres_recents:
            # Très récent (0-1 jours) - aura badge "Nouveau"
            new_date = maintenant - timedelta(days=random.randint(0, 1))
            acc.date_ajoutee = new_date
            acc.save(update_fields=['date_ajoutee'])
            updated += 1
            print(f"✨ {acc.titre} - Très récent (badge 'Nouveau')")
        else:
            # Plus ancien (au moins 3 jours) - pas de badge
            if acc.date_ajoutee >= date_limite:
                new_date = maintenant - timedelta(days=random.randint(3, 60))
                acc.date_ajoutee = new_date
                acc.save(update_fields=['date_ajoutee'])
                updated += 1
                print(f"📅 {acc.titre} - Date mise à jour: {new_date.date()}")
    
    print(f"\n🎉 {updated} accommodation(s) mise(s) à jour!")
    
    # Statistiques finales
    total = Accommodation.objects.filter(est_actif=True).count()
    recents = Accommodation.objects.filter(
        est_actif=True,
        date_ajoutee__gte=date_limite
    ).count()
    
    print(f"\n📊 Statistiques finales:")
    print(f"   - Total: {total}")
    print(f"   - Logements récents (≤2 jours): {recents} (avec badge 'Nouveau')")
    print(f"   - Pages avec pagination de 9: {total // 9 + (1 if total % 9 > 0 else 0)}")

if __name__ == '__main__':
    fix_recent_badges()








