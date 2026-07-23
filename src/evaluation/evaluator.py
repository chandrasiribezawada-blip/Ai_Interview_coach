from langchain_groq import ChatGroq

from factories.llm_factory import LLMFactory
from src.config.settings import Settings

from src.factories.llm_factory import LLMFactory
class AnswerEvaluator:

    def __init__(self):

        self.llm = LLMFactory.create_llm()

    def evaluate(
        self,
        question,
        candidate_answer
    ):

        prompt = f"""
You are an experienced Technical Interviewer.

Evaluate the candidate's answer.

Interview Question:
{question}

Candidate Answer:
{candidate_answer}

Give the response in the following format.

Score: X/10

Strengths:
- ...

Weaknesses:
- ...

Suggestions:
- ...

Overall Feedback:
...
"""

        response = self.llm.invoke(prompt)

        return response.content