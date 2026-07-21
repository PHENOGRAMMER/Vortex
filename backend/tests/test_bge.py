from sentence_transformers import SentenceTransformer

print("Loading model...")

model = SentenceTransformer(
    "BAAI/bge-m3",
    device="cpu",   # we'll test CPU first
)

print("Encoding...")

embedding = model.encode(
    "What programming languages does Aryan know?",
    normalize_embeddings=True,
)

print("Dimension:", len(embedding))
print(embedding[:10])