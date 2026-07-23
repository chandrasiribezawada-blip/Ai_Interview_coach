from src.embeddings.embedder import Embedder


class EmbeddingFactory:
    """
    Factory for creating embedding models.
    """

    @staticmethod
    def create_embedding():

        return Embedder().get_model()