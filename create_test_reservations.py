"""
Script pour créer des réservations de test pour tester le calendrier
"""
import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TooNice.settings')
django.setup()

from AccomodationApp.models import Accommodation, Chambre, Reservation
from UserApp.models import User
from decimal import Decimal

def create_test_reservations():
    """Crée des réservations de test"""
    
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
    
    # Récupérer la première accommodation avec des chambres
    try:
        accommodation = Accommodation.objects.filter(chambres__isnull=False).first()
        if not accommodation:
            print("❌ Aucune accommodation avec des chambres trouvée.")
            return
        print(f"✅ Accommodation trouvée: {accommodation.titre}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'accommodation: {e}")
        return
    
    # Récupérer une chambre
    chambre = accommodation.chambres.first()
    if not chambre:
        print("❌ Aucune chambre trouvée pour cette accommodation.")
        return
    print(f"✅ Chambre trouvée: {chambre.numero}")
    
    # Dates de test
    aujourdhui = date.today()
    
    # Créer plusieurs réservations de test
    reservations_test = [
        {
            'date_debut': aujourdhui + timedelta(days=5),
            'date_fin': aujourdhui + timedelta(days=7),
            'statut': 'confirmee',
            'description': 'Réservation test 1 - 2 nuits'
        },
        {
            'date_debut': aujourdhui + timedelta(days=10),
            'date_fin': aujourdhui + timedelta(days=12),
            'statut': 'confirmee',
            'description': 'Réservation test 2 - 3 nuits'
        },
        {
            'date_debut': aujourdhui + timedelta(days=20),
            'date_fin': aujourdhui + timedelta(days=25),
            'statut': 'en_attente',
            'description': 'Réservation test 3 - 6 nuits'
        },
    ]
    
    created_count = 0
    for res_data in reservations_test:
        try:
            # Calculer le prix total (nombre de nuits * prix par nuit)
            nombre_nuits = (res_data['date_fin'] - res_data['date_debut']).days
            prix_total = Decimal(str(nombre_nuits)) * chambre.prix_nuit
            
            reservation = Reservation.objects.create(
                chambre=chambre,
                utilisateur=user,
                date_debut=res_data['date_debut'],
                date_fin=res_data['date_fin'],
                nombre_personnes=2,
                prix_total=prix_total,
                statut=res_data['statut'],
                notes=res_data['description']
            )
            created_count += 1
            print(f"✅ Réservation créée: {res_data['date_debut']} au {res_data['date_fin']} ({res_data['statut']})")
        except Exception as e:
            print(f"❌ Erreur lors de la création de la réservation {res_data['description']}: {e}")
    
    print(f"\n🎉 {created_count} réservation(s) de test créée(s) avec succès!")
    print(f"\n📅 Dates occupées:")
    dates_occupees = accommodation.get_dates_occupees()
    for date_occ in dates_occupees[:10]:  # Afficher les 10 premières
        print(f"   - {date_occ}")
    if len(dates_occupees) > 10:
        print(f"   ... et {len(dates_occupees) - 10} autres dates")
    
    print(f"\n🌐 Pour tester le calendrier, visitez:")
    print(f"   http://127.0.0.1:8000/accommodations/{accommodation.id}/")

if __name__ == '__main__':
    create_test_reservations()


