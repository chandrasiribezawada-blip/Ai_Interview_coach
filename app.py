from src.interview.pipeline import InterviewPipeline

pipeline = InterviewPipeline()

vectorstore = pipeline.build_resume_vectorstore(
    "data/resume/resume.pdf"
)

job_description = """
Looking for a Python Developer with experience in
LangChain, Django, REST APIs, RAG and LLMs.
"""

question = pipeline.generate_first_question(
    vectorstore,
    job_description
)

print("=" * 60)
print("Interview Question")
print("=" * 60)
print(question)