import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .knowledge_base import load_chunks


STOPWORDS = {
    "qual", "quais", "como", "quando", "onde", "quem",
    "porque", "por que", "o", "a", "os", "as", "um",
    "uma", "de", "do", "da", "dos", "das", "e", "ou",
    "é", "ser", "são", "foi", "para", "por", "com",
    "no", "na", "nos", "nas", "ao", "aos", "se",
    "que", "principal", "sobre", "me", "explique"
}


def normalize(text):
    text = text.lower()
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[^a-zA-ZÀ-ÿ0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def important_terms(text):
    return {
        word
        for word in normalize(text).split()
        if len(word) > 2 and word not in STOPWORDS
    }


class Retriever:
    def __init__(self):
        self.chunks = load_chunks()

        documents = [
            normalize(chunk.text)
            for chunk in self.chunks
        ]

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            strip_accents="unicode",
            ngram_range=(1, 2),
            sublinear_tf=True
        )

        self.matrix = (
            self.vectorizer.fit_transform(documents)
            if documents else None
        )

    def search(self, query, k=3):
        if not self.chunks or self.matrix is None:
            return []

        normalized_query = normalize(query)
        query_terms = important_terms(query)

        scores = cosine_similarity(
            self.vectorizer.transform([normalized_query]),
            self.matrix
        ).ravel()

        ranked = []

        for index, score in enumerate(scores):
            document_terms = important_terms(
                self.chunks[index].text
            )

            if query_terms:
                overlap = len(
                    query_terms.intersection(document_terms)
                ) / len(query_terms)
            else:
                overlap = 0.0

            # Combina similaridade textual e cobertura dos termos.
            final_score = (0.65 * float(score)) + (0.35 * overlap)

            ranked.append((index, final_score))

        ranked.sort(key=lambda item: item[1], reverse=True)

        return [
            {
                "chunk_id": self.chunks[index].chunk_id,
                "source_id": self.chunks[index].source_id,
                "source": self.chunks[index].source_name,
                "text": self.chunks[index].text,
                "score": float(score)
            }
            for index, score in ranked[:k]
        ]
