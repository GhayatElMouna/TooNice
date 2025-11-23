'''from sentence_transformers import SentenceTransformer, util
import torch

# Load English model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Toxic examples in English
TOXIC_EXAMPLES = [
    "insult",
    "racism",
    "harassment",
    "violence",
    "sexual content",
    "hate speech",
    "abusive language",
    "threat",
    "offensive words",
    "discrimination",
    # Insults
    "you are stupid",
    "you are an idiot",
    "you are dumb",
    "you are useless",
    "shut up",
    "go to hell",
    "stupid ",
    "idiot",
    "dumb",
    "useless",
    "shut up",
    "go to hell",
    "damn",

    # Hate & harassment
    "i hate you",
    "i will hurt you",
    "racism",
    "harassment",
    "discrimination",

    # Sexual content
    "sexual content",
    "explicit content",
    "porn",

    # Violence
    "i will kill you",
    "i want to hurt someone"
]

# Embed toxic examples
toxic_embeddings = model.encode(TOXIC_EXAMPLES, convert_to_tensor=True)

def contains_inappropriate(text: str, threshold: float = 0.60) -> bool:
    """
    Detect inappropriate English content using semantic similarity.
    """
    clean_text = text.lower().strip()
    text_emb = model.encode(clean_text, convert_to_tensor=True)
    similarity = util.cos_sim(text_emb, toxic_embeddings)
    return float(similarity.max()) > threshold'''
