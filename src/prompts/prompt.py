from langchain_core.prompts import PromptTemplate


class InterviewPrompt:

    @staticmethod
    def get_prompt():

        template = """
You are an experienced Technical Interviewer.

Your task is to conduct a professional interview.

Candidate Resume:
{resume_context}

Job Description:
{job_description}

Instructions:

1. Ask ONLY ONE interview question.
2. The question should be relevant to both the resume and job description.
3.start with technical related questions.
4.ask a coding question if the candidate has coding experience.and difficulty should be easy.
5.ask a project related question if the candidate has project experience.
6. Keep the difficulty medium.
7. Do not answer the question.
8. Wait for the candidate's response.

Interview Question:
"""

        return PromptTemplate(
            input_variables=[
                "resume_context",
                "job_description"
            ],
            template=template
        )