class PromptBuilder:
    """
    Builds prompts for different AI tasks.
    """

    @staticmethod
    def build_interview_prompt(resume_context, job_description):

        return f"""
You are an experienced Technical Interviewer.

Candidate Resume:

{resume_context}

Job Description:

{job_description}

Your task:

1. Analyze the resume.
2. Analyze the job description.
3. Ask ONE technical interview question.
4. Focus on practical knowledge.
5. Do not provide the answer.
6. Ask only one question.
"""