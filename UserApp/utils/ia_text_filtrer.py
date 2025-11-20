from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

TOXIC_EXAMPLES = [
    "insulte", "racisme", "harcèlement", "violence", "contenu sexuel"
]

toxic_embeddings = model.encode(TOXIC_EXAMPLES, convert_to_tensor=True)

def contains_inappropriate(text):
    text_emb = model.encode(text, convert_to_tensor=True)
    similarity = util.cos_sim(text_emb, toxic_embeddings)
    return float(similarity.max()) > 0.6  # seuil ajustable
