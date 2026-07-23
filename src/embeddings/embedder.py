from langchain_huggingface import HuggingFaceEmbeddings


class Embedder:
    """
    Creates an embedding model that converts text into dense vectors.
    """

    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

    def get_model(self):
        """
        Returns the embedding model.
        """
        return self.model