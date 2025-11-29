"""
Script pour créer des accommodations réalistes et personnalisées
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TooNice.settings')
django.setup()

from AccomodationApp.models import Accommodation, Chambre
from UserApp.models import User
from decimal import Decimal
from django.utils import timezone

# Données réalistes pour créer des logements variés
NOMS_RIADS = [
    "Dar El Medina", "Riad Sidi Bou Said", "Dar Zaghouan", "Riad El Andalous", 
    "Dar Carthage", "Riad La Kasbah", "Dar Hammamet", "Riad El Kairouan",
    "Dar Sidi Bouzid", "Riad El Medina", "Dar Tozeur", "Riad El Djerba"
]

NOMS_HOTELS = [
    "Hôtel Les Palmiers", "Hôtel La Corniche", "Hôtel El Medina", "Hôtel Les Dunes",
    "Hôtel Le Phare", "Hôtel La Plage", "Hôtel El Ksar", "Hôtel Les Jardins"
]

NOMS_MAISONS = [
    "Maison d'hôte El Amel", "Maison d'hôte Dar El Hana", "Maison d'hôte La Rose",
    "Maison d'hôte El Wafa", "Maison d'hôte Dar El Salam", "Maison d'hôte La Perle"
]

NOMS_GITES = [
    "Gîte Rural El Khayma", "Gîte Les Oliviers", "Gîte El Oued", "Gîte La Montagne",
    "Gîte El Jebel", "Gîte Les Sources"
]

DESCRIPTIONS = [
    "Magnifique hébergement au cœur de la médina, offrant une vue imprenable sur la mer. Décoration traditionnelle authentique avec tout le confort moderne.",
    "Charmant logement situé dans un quartier calme, à proximité des sites historiques. Terrasse panoramique et jardin luxuriant.",
    "Hébergement de charme alliant tradition et modernité. Piscine, spa et restaurant sur place. Idéal pour un séjour de détente.",
    "Authentique maison tunisienne restaurée avec goût. Cour intérieure fleurie, chambres spacieuses et accueil chaleureux.",
    "Logement moderne dans un cadre verdoyant. Proche des plages et des activités nautiques. Parfait pour les familles.",
    "Belle demeure historique transformée en hébergement de prestige. Architecture typique, mobilier d'époque et services haut de gamme.",
    "Hébergement écologique au milieu de la nature. Énergie solaire, produits locaux et activités de plein air.",
    "Charmant logement avec vue sur les montagnes. Randonnées, observation des étoiles et cuisine locale au programme.",
    "Maison traditionnelle au style andalou. Patio ombragé, fontaine centrale et chambres climatisées.",
    "Hébergement de luxe face à la mer. Plage privée, spa, restaurant gastronomique et service de conciergerie.",
    "Logement rustique et authentique. Expérience immersive dans la culture locale avec cours de cuisine et visites guidées.",
    "Belle villa avec piscine et jardin. Idéale pour les groupes et familles. Barbecue et espace détente disponibles."
]

ADRESSES = [
    "Rue de la Médina, Tunis", "Avenue Habib Bourguiba, Sousse", "Route de la Corniche, Hammamet",
    "Place de la Kasbah, Kairouan", "Rue des Andalous, Sidi Bou Said", "Avenue de la République, Monastir",
    "Route des Plages, Djerba", "Rue El Medina, Sfax", "Avenue de la Liberté, Nabeul",
    "Route de la Montagne, Zaghouan", "Rue des Palmiers, Tozeur", "Avenue du 14 Janvier, Bizerte",
    "Rue de la Mer, Mahdia", "Route des Oasis, Gabès", "Avenue de l'Indépendance, Béja"
]

def create_realistic_accommodations():
    """Crée des accommodations réalistes et variées"""
    
    # Récupérer un utilisateur
    try:
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Veuillez d'abord créer un utilisateur.")
            return
        print(f"✅ Utilisateur trouvé: {user.username}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return
    
    # Supprimer les anciens logements de test
    Accommodation.objects.filter(titre__startswith="Logement de test").delete()
    print("🧹 Anciens logements de test supprimés")
    
    # Types et gouvernorats
    types_config = {
        "riad": {"noms": NOMS_RIADS, "gouvernorats": ["tunis", "sousse", "kairouan", "sfax"], "prix_base": 80},
        "hotel": {"noms": NOMS_HOTELS, "gouvernorats": ["tunis", "sousse", "monastir", "nabeul", "djerba"], "prix_base": 120},
        "maison_dhote": {"noms": NOMS_MAISONS, "gouvernorats": ["tunis", "nabeul", "zaghouan", "bizerte"], "prix_base": 60},
        "gite_rural": {"noms": NOMS_GITES, "gouvernorats": ["zaghouan", "kef", "siliana", "beja"], "prix_base": 45},
    }
    
    created_count = 0
    aujourdhui = date.today()
    
    # Créer des logements variés avec des dates différentes
    for i in range(20):
        try:
            # Choisir un type aléatoire
            type_accommodation = random.choice(list(types_config.keys()))
            config = types_config[type_accommodation]
            
            # Choisir un nom qui n'a pas encore été utilisé
            noms_disponibles = [n for n in config["noms"] 
                               if not Accommodation.objects.filter(titre=n).exists()]
            if not noms_disponibles:
                nom = f"{random.choice(config['noms'])} {i+1}"
            else:
                nom = random.choice(noms_disponibles)
            
            # Date d'ajout variée (certains récents, d'autres plus anciens)
            if i < 2:  # 2 très récents (hier et aujourd'hui) - auront le badge "Nouveau"
                date_ajoutee = timezone.now() - timedelta(days=random.randint(0, 1))
            elif i < 5:  # 3 récents (3-5 jours) - pas de badge
                date_ajoutee = timezone.now() - timedelta(days=random.randint(3, 5))
            else:  # Les autres plus anciens
                date_ajoutee = timezone.now() - timedelta(days=random.randint(10, 60))
            
            # Créer l'accommodation
            accommodation = Accommodation.objects.create(
                titre=nom,
                description=random.choice(DESCRIPTIONS),
                type=type_accommodation,
                gouvernorat=random.choice(config["gouvernorats"]),
                prix=Decimal(str(config["prix_base"] + random.randint(-10, 30))),
                adresse=random.choice(ADRESSES),
                est_actif=True,
                date_ajoutee=date_ajoutee
            )
            
            # Ajouter l'utilisateur
            accommodation.utilisateurs.add(user)
            
            # Créer 1-3 chambres variées
            nb_chambres = random.randint(1, 3)
            types_chambres = ["simple", "double", "triple", "suite", "familiale"]
            
            for j in range(nb_chambres):
                type_chambre = random.choice(types_chambres)
                prix_chambre = accommodation.prix * Decimal(str(random.uniform(0.8, 1.5)))
                
                Chambre.objects.create(
                    accommodation=accommodation,
                    numero=f"{accommodation.titre[:2].upper()}{j+1:02d}",
                    type_chambre=type_chambre,
                    description=f"Chambre {type_chambre} confortable et bien équipée",
                    nombre_lits=random.randint(1, 4),
                    prix_nuit=prix_chambre
                )
            
            created_count += 1
            print(f"✅ {nom} ({type_accommodation}) - Ajouté le {date_ajoutee}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la création {i+1}: {e}")
    
    print(f"\n🎉 {created_count} accommodation(s) réaliste(s) créée(s) avec succès!")
    
    # Statistiques
    total = Accommodation.objects.filter(est_actif=True).count()
    date_limite = timezone.now() - timedelta(days=2)
    recents = Accommodation.objects.filter(
        est_actif=True,
        date_ajoutee__gte=date_limite
    ).count()
    
    print(f"\n📊 Statistiques:")
    print(f"   - Total d'accommodations actives: {total}")
    print(f"   - Logements récents (≤2 jours): {recents} (avec badge 'Nouveau')")
    print(f"   - Pages avec pagination de 9: {total // 9 + (1 if total % 9 > 0 else 0)}")
    
    print(f"\n🌐 Pour voir les résultats:")
    print(f"   http://127.0.0.1:8000/accommodations/")

if __name__ == '__main__':
    create_realistic_accommodations()

