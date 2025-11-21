import os
import pickle
from typing import List, Dict, Any, Optional

import numpy as np


class SimpleVectorStore:
    """
    Minimal vector store:
    - Stores embeddings (numpy array)
    - Stores texts and metadatas lists
    - Persists to a pickle file
    """

    def __init__(self, path: str = "kb_store.pkl"):
        self.path = path
        self.embeddings: Optional[np.ndarray] = None
        self.texts: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.html_full: str = ""

        if os.path.exists(self.path):
            self._load()

    def _load(self):
        with open(self.path, "rb") as f:
            data = pickle.load(f)
        self.embeddings = data["embeddings"]
        self.texts = data["texts"]
        self.metadatas = data["metadatas"]
        self.html_full = data.get("html_full", "")

    def _save(self):
        data = {
            "embeddings": self.embeddings,
            "texts": self.texts,
            "metadatas": self.metadatas,
            "html_full": self.html_full,
        }
        with open(self.path, "wb") as f:
            pickle.dump(data, f)

    def reset(self):
        self.embeddings = None
        self.texts = []
        self.metadatas = []
        self.html_full = ""
        self._save()

    def add_documents(
        self,
        embeddings: np.ndarray,
        texts: List[str],
        metadatas: List[Dict[str, Any]],
        html_full: str,
    ):
        if self.embeddings is None:
            self.embeddings = embeddings
            self.texts = texts
            self.metadatas = metadatas
        else:
            self.embeddings = np.vstack([self.embeddings, embeddings])
            self.texts.extend(texts)
            self.metadatas.extend(metadatas)
        if html_full:
            self.html_full = html_full
        self._save()

    def is_empty(self) -> bool:
        return self.embeddings is None or len(self.texts) == 0

    def similarity_search(self, query_embedding: np.ndarray, top_k: int = 5):
        """
        Returns list of (text, metadata, score) sorted by similarity.
        """
        if self.is_empty():
            return []

        # normalize
        emb = self.embeddings
        q = query_embedding.reshape(1, -1)

        emb_norm = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-10)
        q_norm = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-10)

        scores = np.dot(emb_norm, q_norm.T).reshape(-1)  # cosine similarity

        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append(
                {
                    "text": self.texts[idx],
                    "metadata": self.metadatas[idx],
                    "score": float(scores[idx]),
                }
            )
        return results
