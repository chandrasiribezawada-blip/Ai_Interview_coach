from langchain_groq import ChatGroq

from src.config.settings import Settings
from src.prompts.prompt import InterviewPrompt

from src.factories.llm_factory import LLMFactory
class Interviewer:

    def __init__(self):

        self.llm = LLMFactory.create_llm()

        self.prompt = InterviewPrompt().get_prompt()

    def generate_question(self, resume_context, job_description):

        chain = self.prompt | self.llm

        response = chain.invoke({
            "resume_context": resume_context,
            "job_description": job_description
        })

        return response.content