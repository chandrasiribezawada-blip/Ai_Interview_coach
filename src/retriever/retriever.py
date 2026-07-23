class ResumeRetriever:
    """
    Retrieves the most relevant chunks from the vector database.
    """

    def __init__(self, vectorstore):
        self.vectorstore = vectorstore

    def retrieve(self, query, k=3):
        """
        Returns the top-k most relevant document chunks.
        """
        return self.vectorstore.similarity_search(
            query=query,
            k=k
        )