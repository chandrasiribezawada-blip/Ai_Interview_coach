import json

from langchain_groq import ChatGroq

from src.config.settings import Settings
from src.prompts.prompt import InterviewPrompt

from src.factories.llm_factory import LLMFactory
from src.utils.helper import parse_json_response


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

    def generate_follow_up(
        self,
        next_topic,
        current_question,
        candidate_answer,
        history,
        retrieved_context,
    ):
        prompt = f"""
You are a professional interviewer conducting a multi-round interview.
Return only a JSON object with string fields acknowledgement and next_question.
Ask exactly one concise question for the next round topic, grounded in the candidate's answer,
the prior interview history, and the retrieved resume/job-description context.

Next round topic: {next_topic}
Current question: {current_question}
Candidate answer: {candidate_answer}
Prior interview history: {json.dumps(history, ensure_ascii=True)}
Retrieved resume and job-description context: {retrieved_context}
"""
        response = self.llm.invoke(prompt)
        result = parse_json_response(
            response,
            {"acknowledgement": "Thank you for your answer.", "next_question": ""},
        )
        return {
            "acknowledgement": str(result.get("acknowledgement") or "Thank you for your answer."),
            "next_question": str(result.get("next_question") or ""),
        }