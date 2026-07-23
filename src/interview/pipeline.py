from src.loaders.pdf_loader import PDFLoader
from src.preprocess.cleaner import TextCleaner
from src.preprocess.chunker import TextChunker
from src.preprocess.metadata import MetadataGenerator

from src.embeddings.embedder import Embedder
from src.vectordb.faiss_db import FAISSDatabase

from src.rewrite.query_rewriter import QueryRewriter

from src.retriever.hybrid_retriever import HybridRetriever

from src.reranker.reranker import Reranker

from src.refine.context_refine import ContextRefiner

from src.interview.interview import Interviewer

from src.evaluation.evaluator import AnswerEvaluator

from src.interview.session import InterviewSession

from src.reports.report import ReportGenerator

from src.factories.embedding_factory import EmbeddingFactory

class InterviewPipeline:
    """
    Main pipeline that orchestrates the complete
    AI Interview Workflow.
    """

    def __init__(self):

        # Embedding Model
        self.embedding_model = EmbeddingFactory.create_embedding()
        # Vector Database
        self.faiss_db = FAISSDatabase(self.embedding_model)

        # Query Rewriter
        self.rewriter = QueryRewriter()

        # Reranker
        self.reranker = Reranker()

        # Context Refiner
        self.refiner = ContextRefiner()

        # LLM Modules
        self.interviewer = Interviewer()
        self.evaluator = AnswerEvaluator()

        # Interview Session
        self.session = InterviewSession()

        # Report Generator
        self.report = ReportGenerator()

        # Store processed documents
        self.documents = []

    # --------------------------------------------------------

    def build_resume_vectorstore(self, resume_path):
        """
        Loads, preprocesses and indexes the resume.
        """

        loader = PDFLoader(resume_path)

        documents = loader.load()

        documents = TextCleaner.clean(documents)

        chunker = TextChunker()

        chunks = chunker.split(documents)

        chunks = MetadataGenerator.enhance(
            chunks,
            document_type="resume"
        )

        self.documents = chunks

        vectorstore = self.faiss_db.create(chunks)

        self.faiss_db.save(vectorstore)

        return vectorstore

    # --------------------------------------------------------

    def generate_first_question(
        self,
        vectorstore,
        job_description,
        topic
    ):
        """
        Complete RAG Pipeline

        Rewrite
            ↓
        Hybrid Retrieval
            ↓
        Reranking
            ↓
        Context Refinement
            ↓
        Prompt
            ↓
        LLM
        """

        # Rewrite Query
        rewritten_query = self.rewriter.rewrite(topic)

        print("\n" + "=" * 60)
        print("Rewritten Query")
        print("=" * 60)
        print(rewritten_query)

        # Hybrid Retrieval
        retriever = HybridRetriever(
            vectorstore,
            self.documents
        )

        results = retriever.retrieve(
            rewritten_query,
            k=5
        )

        # Reranking
        results = self.reranker.rerank(
            rewritten_query,
            results,
            top_k=3
        )

        # Context Refinement
        resume_context = self.refiner.refine(results)

        # Generate Interview Question
        question = self.interviewer.generate_question(
            resume_context,
            job_description
        )

        return question

    # --------------------------------------------------------

    def evaluate_answer(
        self,
        question,
        candidate_answer
    ):

        return self.evaluator.evaluate(
            question,
            candidate_answer
        )

    # --------------------------------------------------------

    def save_round(
        self,
        question,
        answer,
        feedback
    ):

        self.session.add_round(
            question,
            answer,
            feedback
        )

    # --------------------------------------------------------

    def generate_report(self):

        return self.report.generate(
            self.session
        )