from langchain_groq import ChatGroq

from factories.llm_factory import LLMFactory
from src.config.settings import Settings


class QueryRewriter:

    def __init__(self):

        self.llm = LLMFactory.create_llm()
    def rewrite(self, query):

        prompt = f"""
You are a Query Rewriter for a Resume Retrieval System.

Your task is to rewrite the user's query into a richer semantic search query.

Rules:

1. Preserve the original intent.
2. Expand technical abbreviations.
3. Include likely technologies.
4. Generate keywords instead of sentences.
5. Output only comma-separated keywords.

Example

Input:
Projects

Output:
Projects, Software Development, Python, Django, LangChain,
Large Language Models, Retrieval-Augmented Generation,
AI Applications

User Query:

{query}
"""

        response = self.llm.invoke(prompt)

        return response.content.strip()