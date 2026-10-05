import os

from src.loaders.pdf_loader import PDFLoader
from src.loaders.text_loader import TextLoader
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
        chunker = TextChunker()
        resume_chunks = chunker.split(TextCleaner.clean(documents))
        resume_chunks = MetadataGenerator.enhance(
            resume_chunks,
            document_type="resume"
        )

        jd_chunks = []
        jd_path = "data/jd/job_description.txt"
        if os.path.isfile(jd_path):
            jd_documents = TextCleaner.clean(TextLoader(jd_path).load())
            if any(document.page_content for document in jd_documents):
                jd_chunks = chunker.split(jd_documents)
                jd_chunks = MetadataGenerator.enhance(
                    jd_chunks,
                    document_type="job_description"
                )

        chunks = resume_chunks + jd_chunks
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

        resume_context = self.retrieve_context(vectorstore, topic)

        # Generate Interview Question
        question = self.interviewer.generate_question(
            resume_context,
            job_description
        )

        return question

    def retrieve_context(self, vectorstore, query):
        rewritten_query = self.rewriter.rewrite(query)

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

        if not results:
            results = self.documents[:3]
        if not results:
            raise RuntimeError("No resume or job-description chunks are available for retrieval.")

        # Reranking
        results = self.reranker.rerank(
            rewritten_query,
            results,
            top_k=3
        )

        # Context Refinement
        resume_context = self.refiner.refine(results)

        return resume_context

    def evaluate_voice_answer(self, question, candidate_answer, vectorstore):
        retrieved_context = self.retrieve_context(
            vectorstore,
            f"{question}\n{candidate_answer}",
        )
        evaluation = self.evaluator.evaluate_voice(question, candidate_answer, retrieved_context)
        evaluation["_retrieved_context"] = retrieved_context
        return evaluation

    def generate_voice_follow_up(
        self, next_topic, question, candidate_answer, history, vectorstore, retrieved_context=None
    ):
        if retrieved_context is None:
            retrieved_context = self.retrieve_context(
                vectorstore,
                f"{question}\n{candidate_answer}",
            )
        return self.interviewer.generate_follow_up(
            next_topic,
            question,
            candidate_answer,
            history,
            retrieved_context,
        )

    def generate_voice_report(self, topic, history):
        return self.report.generate_voice(self.interviewer.llm, topic, history)

    # --------------------------------------------------------

    def evaluate_answer(
        self,
        question,
        candidate_answer,
        category="technical",
        context="",
    ):

        return self.evaluator.evaluate(
            question,
            candidate_answer,
            category=category,
            context=context,
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