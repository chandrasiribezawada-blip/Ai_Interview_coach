from src.factories.llm_factory import LLMFactory
from src.utils.helper import parse_json_response


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

    def evaluate_voice(self, question, candidate_answer, retrieved_context):
        prompt = f"""
You are an experienced interviewer and interview coach. Evaluate only the candidate's
answer to the question, using the retrieved material to assess relevance and missing points.
Return only a JSON object with integer score from 0 to 10, string feedback,
array of string missing_points, and array of string strengths.

Interview question: {question}
Candidate answer: {candidate_answer}
Retrieved resume and job-description context: {retrieved_context}
"""
        response = self.llm.invoke(prompt)
        result = parse_json_response(
            response,
            {"score": 0, "feedback": "Evaluation could not be parsed.", "missing_points": [], "strengths": []},
        )
        try:
            score = max(0, min(10, int(result.get("score", 0))))
        except (TypeError, ValueError):
            score = 0

        def string_list(value):
            return [str(item) for item in value] if isinstance(value, list) else []

        return {
            "score": score,
            "feedback": str(result.get("feedback", "")),
            "missing_points": string_list(result.get("missing_points")),
            "strengths": string_list(result.get("strengths")),
        }