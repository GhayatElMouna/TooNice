"""
Script pour tester l'API du calendrier
"""
import os
import sys
import django
import json

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TooNice.settings')
django.setup()

from AccomodationApp.models import Accommodation
from django.test import Client

def test_calendrier_api():
    """Test l'API du calendrier"""
    
    # Récupérer une accommodation avec des réservations
    accommodation = Accommodation.objects.filter(chambres__reservations__isnull=False).first()
    
    if not accommodation:
        print("❌ Aucune accommodation avec des réservations trouvée.")
        return
    
    print(f"✅ Test de l'API pour l'accommodation: {accommodation.titre} (ID: {accommodation.id})")
    
    # Créer un client de test
    client = Client()
    
    # Tester l'endpoint
    url = f'/accommodations/{accommodation.id}/disponibilites/'
    print(f"\n📡 Test de l'endpoint: {url}")
    
    try:
        response = client.get(url)
        print(f"✅ Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content)
            print(f"\n📊 Données reçues:")
            print(f"   - Nombre de dates occupées: {len(data.get('dates_occupees', []))}")
            print(f"   - Dates occupées (premières 10):")
            for date_occ in data.get('dates_occupees', [])[:10]:
                print(f"     • {date_occ}")
            if len(data.get('dates_occupees', [])) > 10:
                print(f"     ... et {len(data.get('dates_occupees', [])) - 10} autres")
            
            print(f"\n   - Réservations par chambre: {len(data.get('reservations_by_chambre', {}))} chambre(s)")
            for chambre_id, reservations in data.get('reservations_by_chambre', {}).items():
                print(f"     • Chambre {chambre_id}: {len(reservations)} réservation(s)")
        else:
            print(f"❌ Erreur: {response.status_code}")
            print(f"   Contenu: {response.content}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
    
    # Vérifier les méthodes du modèle
    print(f"\n🔍 Test des méthodes du modèle:")
    dates_occupees = accommodation.get_dates_occupees()
    print(f"   - get_dates_occupees(): {len(dates_occupees)} dates")
    
    from datetime import date, timedelta
    aujourdhui = date.today()
    date_test_debut = aujourdhui + timedelta(days=1)
    date_test_fin = aujourdhui + timedelta(days=3)
    is_dispo = accommodation.is_disponible(date_test_debut, date_test_fin)
    print(f"   - is_disponible({date_test_debut}, {date_test_fin}): {is_dispo}")

if __name__ == '__main__':
    test_calendrier_api()


