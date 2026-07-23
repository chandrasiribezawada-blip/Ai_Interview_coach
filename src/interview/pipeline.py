from src.loaders.pdf_loader import PDFLoader
from src.preprocess.cleaner import TextCleaner
from src.preprocess.chunker import TextChunker
from src.preprocess.metadata import MetadataGenerator

from src.embeddings.embedder import Embedder
from src.vectordb.faiss_db import FAISSDatabase
from src.retriever.retriever import ResumeRetriever
from src.interview.interview import Interviewer


class InterviewPipeline:

    def __init__(self):

        self.embedding_model = Embedder().get_model()

        self.faiss_db = FAISSDatabase(self.embedding_model)

        self.interviewer = Interviewer()

    def build_resume_vectorstore(self, resume_path):

        loader = PDFLoader(resume_path)

        documents = loader.load()

        documents = TextCleaner.clean(documents)

        chunker = TextChunker()

        chunks = chunker.split(documents)

        chunks = MetadataGenerator.enhance(
            chunks,
            document_type="resume"
        )

        vectorstore = self.faiss_db.create(chunks)

        self.faiss_db.save(vectorstore)

        return vectorstore

    def generate_first_question(self, vectorstore, job_description):

        retriever = ResumeRetriever(vectorstore)

        results = retriever.retrieve(
            query="Projects",
            k=3
        )

        resume_context = "\n\n".join(
            [doc.page_content for doc in results]
        )

        return self.interviewer.generate_question(
            resume_context,
            job_description
        )