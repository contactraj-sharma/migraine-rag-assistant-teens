from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Tuple

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "migraine_articles.json"


class KnowledgeBase:
    def __init__(self, documents: List[dict]):
        self.documents = documents
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.document_texts = [doc["content"] for doc in documents]
        self.doc_vectors = self.vectorizer.fit_transform(self.document_texts)

    def query(self, question: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        question_vec = self.vectorizer.transform([question])
        similarities = cosine_similarity(question_vec, self.doc_vectors).flatten()
        ranked_indices = similarities.argsort()[::-1][:top_k]
        results: List[Tuple[dict, float]] = []
        for idx in ranked_indices:
            score = max(float(similarities[idx]), 0.0)
            results.append((self.documents[idx], score))
        return results


@lru_cache(maxsize=1)
def get_knowledge_base() -> KnowledgeBase:
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)
    return KnowledgeBase(documents)
