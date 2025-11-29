"""
Script pour mettre à jour les dates de quelques accommodations pour avoir une meilleure variété
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

def update_dates():
    """Met à jour les dates de quelques accommodations"""
    
    accommodations = Accommodation.objects.filter(est_actif=True).order_by('?')[:30]
    
    updated = 0
    maintenant = timezone.now()
    
    for i, acc in enumerate(accommodations):
        # Varier les dates : certains très récents, d'autres plus anciens
        if i < 2:  # 2 très récents (0-1 jours) - auront badge "Nouveau"
            new_date = maintenant - timedelta(days=random.randint(0, 1))
        elif i < 5:  # 3 récents (3-5 jours) - pas de badge
            new_date = maintenant - timedelta(days=random.randint(3, 5))
        elif i < 10:  # 5 moyens (7-15 jours)
            new_date = maintenant - timedelta(days=random.randint(7, 15))
        else:  # Les autres plus anciens (20-60 jours)
            new_date = maintenant - timedelta(days=random.randint(20, 60))
        
        acc.date_ajoutee = new_date
        acc.save(update_fields=['date_ajoutee'])
        updated += 1
        print(f"✅ {acc.titre} - Date mise à jour: {new_date.date()}")
    
    print(f"\n🎉 {updated} accommodation(s) mise(s) à jour!")
    
    # Statistiques
    total = Accommodation.objects.filter(est_actif=True).count()
    date_limite = timezone.now() - timedelta(days=2)
    recents = Accommodation.objects.filter(
        est_actif=True,
        date_ajoutee__gte=date_limite
    ).count()
    
    print(f"\n📊 Statistiques:")
    print(f"   - Total: {total}")
    print(f"   - Logements récents (≤2 jours): {recents} (avec badge 'Nouveau')")

if __name__ == '__main__':
    update_dates()








