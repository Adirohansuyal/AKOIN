from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    def __init__(self, doc_path):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = self.load_docs(doc_path)
        self.index = self.build_index(self.texts)

    def load_docs(self, path):
        with open(path, "r") as f:
            data = f.read()
        return data.split("\n---\n")

    def build_index(self, texts):
        embeddings = self.model.encode(texts)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(np.array(embeddings))
        return index

    def retrieve(self, query, k=2):
        q_emb = self.model.encode([query])
        distances, indices = self.index.search(np.array(q_emb), k)
        return [self.texts[i] for i in indices[0]]
