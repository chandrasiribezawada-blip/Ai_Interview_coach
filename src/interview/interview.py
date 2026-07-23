from langchain_groq import ChatGroq

from src.config.settings import Settings
from src.prompts.prompt import InterviewPrompt


class Interviewer:

    def __init__(self):

        self.llm = ChatGroq(
            api_key=Settings.GROQ_API_KEY,
            model=Settings.MODEL_NAME,
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS
        )

        self.prompt = InterviewPrompt().get_prompt()

    def generate_question(self, resume_context, job_description):

        chain = self.prompt | self.llm

        response = chain.invoke({
            "resume_context": resume_context,
            "job_description": job_description
        })

        return response.content