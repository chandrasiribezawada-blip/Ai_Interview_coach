class SemanticRetriever:
    """
    Performs semantic search using the vector database.
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query, k=5):

        return self.vectorstore.similarity_search(
            query=query,
            k=k
        )