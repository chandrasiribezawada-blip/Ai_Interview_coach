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
3. Start with project-related questions.
4. Keep the difficulty medium.
5. Do not answer the question.
6. Wait for the candidate's response.

Interview Question:
"""

        return PromptTemplate(
            input_variables=[
                "resume_context",
                "job_description"
            ],
            template=template
        )