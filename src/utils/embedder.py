from sentence_transformers import SentenceTransformer

# embedder
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str):
    vec = _model.encode(text, show_progress_bar=False)
    return vec.tolist()  # list of floats (len = 384)
