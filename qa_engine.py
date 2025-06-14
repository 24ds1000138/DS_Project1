import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class QAEngine:
    def __init__(self, data_paths=["discourse_data.json", "tds_landing_content.json"]):
        self.data = []
        for path in data_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                    for item in items:
                        # Normalize: use 'text' as 'answer' if 'answer' not present
                        answer = item.get("answer") or item.get("text")
                        if answer:
                            self.data.append({
                                "answer": answer,
                                "links": item.get("links", [])
                            })
            except Exception as e:
                print(f"⚠️ Could not load {path}: {e}")

        self.texts = [item["answer"] for item in self.data]
        self.vectorizer = TfidfVectorizer().fit(self.texts)
        self.vectors = self.vectorizer.transform(self.texts)

    def search(self, user_question: str, top_k: int = 3):
        query_vec = self.vectorizer.transform([user_question])
        sims = cosine_similarity(query_vec, self.vectors).flatten()
        top_indices = sims.argsort()[-top_k:][::-1]
        return [self.data[i] for i in top_indices]
