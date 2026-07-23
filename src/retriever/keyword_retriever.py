class KeywordRetriever:
    """
    Performs keyword-based retrieval.
    """

    def __init__(self, documents):
        self.documents = documents

    def retrieve(self, query):

        query_words = query.lower().split()

        results = []

        for doc in self.documents:

            text = doc.page_content.lower()

            if any(word in text for word in query_words):
                results.append(doc)

        return results