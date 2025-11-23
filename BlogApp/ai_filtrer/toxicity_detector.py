from sentence_transformers import SentenceTransformer, util

# Charger le modèle en anglais
model = SentenceTransformer('all-MiniLM-L6-v2')

# Liste des exemples toxiques (plus complète)
TOXIC_EXAMPLES = [
    "you are stupid",
    "you are an idiot",
    "you are dumb",
    "you are useless",
    "shut up",
    "go to hell",
    "damn",
    "i hate you",
    "i will hurt you",
    "kill you",
    "sexual content",
    "porn",
    "explicit content",
    "racism",
    "harassment",
    "discrimination",
    "offensive words",
    "threat",
    "abusive language",
]

# Encoder les exemples toxiques
toxic_embeddings = model.encode([ex.lower() for ex in TOXIC_EXAMPLES], convert_to_tensor=True)

def contains_inappropriate(text: str, threshold: float = 0.50) -> bool:
    """
    Détecte le contenu inapproprié en anglais via la similarité sémantique.
    Le seuil par défaut est abaissé à 0.50 pour capter les phrases courtes.
    """
    if not text:
        return False

    # Prétraitement simple
    text_clean = text.lower().strip()

    # Encodage
    text_emb = model.encode(text_clean, convert_to_tensor=True)

    # Similarité cosinus
    similarity = util.cos_sim(text_emb, toxic_embeddings)

    # Affichage debug (optionnel)
    # print(similarity)

    return float(similarity.max()) >= threshold
