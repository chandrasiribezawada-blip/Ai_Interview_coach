class Reranker:
    """
    Simple keyword-overlap based reranker.

    Later this can be replaced by
    BGE Reranker
    Cohere Rerank
    Cross Encoder
    """

    def rerank(self, query, documents, top_k=3):

        query_words = set(query.lower().split())

        scored_docs = []

        for doc in documents:

            text_words = set(doc.page_content.lower().split())

            score = len(query_words.intersection(text_words))

            scored_docs.append((score, doc))

        scored_docs.sort(
            key=lambda x: x[0],
            reverse=True
        )

        return [doc for score, doc in scored_docs[:top_k]]