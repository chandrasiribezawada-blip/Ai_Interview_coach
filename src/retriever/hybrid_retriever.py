from src.retriever.semantic_retriever import SemanticRetriever
from src.retriever.keyword_retriever import KeywordRetriever


class HybridRetriever:

    def __init__(self, vectorstore, documents):

        self.semantic = SemanticRetriever(vectorstore)

        self.keyword = KeywordRetriever(documents)

    def retrieve(self, query, k=5):

        semantic_results = self.semantic.retrieve(query, k)

        keyword_results = self.keyword.retrieve(query)

        combined = []

        seen = set()

        for doc in semantic_results + keyword_results:

            if doc.page_content not in seen:

                combined.append(doc)

                seen.add(doc.page_content)

        return combined[:k]