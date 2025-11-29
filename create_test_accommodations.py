"""
Script pour créer des accommodations de test pour tester la pagination
"""
import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TooNice.settings')
django.setup()

from AccomodationApp.models import Accommodation, Chambre
from UserApp.models import User
from decimal import Decimal

def create_test_accommodations():
    """Crée des accommodations de test"""
    
    # Récupérer ou créer un utilisateur de test
    try:
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Veuillez d'abord créer un utilisateur.")
            return
        print(f"✅ Utilisateur trouvé: {user.username}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'utilisateur: {e}")
        return
    
    # Types et gouvernorats pour varier
    types = ["maison_dhote", "hotel", "riad", "gite_rural"]
    gouvernorats = ["tunis", "sousse", "nabeul", "sfax", "monastir"]
    
    # Créer 15 accommodations de test
    created_count = 0
    aujourdhui = date.today()
    
    for i in range(1, 16):
        try:
            # Varier les dates pour tester le tri
            date_ajoutee = aujourdhui - timedelta(days=i*2)
            
            accommodation = Accommodation.objects.create(
                titre=f"Logement de test {i}",
                description=f"Description du logement de test numéro {i}. Un magnifique hébergement pour vos vacances.",
                type=types[i % len(types)],
                gouvernorat=gouvernorats[i % len(gouvernorats)],
                prix=Decimal('50.00') + Decimal(str(i * 10)),
                adresse=f"Adresse {i}, Rue Principale",
                est_actif=True,
                date_ajoutee=date_ajoutee
            )
            
            # Ajouter l'utilisateur
            accommodation.utilisateurs.add(user)
            
            # Créer une chambre pour chaque accommodation
            Chambre.objects.create(
                accommodation=accommodation,
                numero=f"CH{i}",
                type_chambre="double",
                description=f"Chambre confortable pour le logement {i}",
                nombre_lits=2,
                prix_nuit=accommodation.prix
            )
            
            created_count += 1
            print(f"✅ Accommodation créée: {accommodation.titre} (ajoutée le {date_ajoutee})")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création de l'accommodation {i}: {e}")
    
    print(f"\n🎉 {created_count} accommodation(s) de test créée(s) avec succès!")
    
    # Afficher le total
    total = Accommodation.objects.filter(est_actif=True).count()
    print(f"\n📊 Total d'accommodations actives: {total}")
    print(f"📄 Avec pagination de 12 par page, cela fait {total // 12 + (1 if total % 12 > 0 else 0)} page(s)")
    
    print(f"\n🌐 Pour tester la pagination, visitez:")
    print(f"   http://127.0.0.1:8000/accommodations/")

if __name__ == '__main__':
    create_test_accommodations()


