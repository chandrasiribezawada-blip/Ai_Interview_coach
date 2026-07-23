import os

from langchain_community.vectorstores import FAISS


class FAISSDatabase:

    def __init__(self, embeddings):
        self.embeddings = embeddings

    def create(self, chunks):
        """
        Create a FAISS vector database from document chunks.
        """
        return FAISS.from_documents(chunks, self.embeddings)

    def save(self, vectorstore, path="data/vectordb"):
        """
        Save the FAISS database locally.
        """
        os.makedirs(path, exist_ok=True)
        vectorstore.save_local(path)

    def load(self, path="data/vectordb"):
        """
        Load an existing FAISS database.
        """
        return FAISS.load_local(
            path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )