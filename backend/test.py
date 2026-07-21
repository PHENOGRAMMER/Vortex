import requests
import numpy as np

texts = [
    "Hello world",
    "Artificial Intelligence",
    "Machine Learning",
]

vectors = []

for text in texts:
    r = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text",
            "prompt": text,
        },
    )

    embedding = r.json()["embedding"]
    vectors.append(embedding)

for i in range(len(vectors)):
    for j in range(i + 1, len(vectors)):
        print(
            f"{texts[i]} vs {texts[j]}",
            np.allclose(vectors[i], vectors[j]),
        )