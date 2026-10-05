from src.reports.report import ReportGenerator
from src.evaluation.evaluator import AnswerEvaluator


class FakeLLM:
    def invoke(self, prompt):
        class Response:
            content = "This is not valid JSON at all."
        return Response()


def test_generate_voice_uses_history_scores_when_model_response_is_invalid():
    report = ReportGenerator().generate_voice(
        FakeLLM(),
        "Python",
        [
            {"score": 8, "wpm": 90, "filler_count": 1, "duration_sec": 45},
            {"score": 7, "wpm": 80, "filler_count": 3, "duration_sec": 50},
        ],
    )

    assert report["overall_score"] > 0
    assert report["content_score"] > 0
    assert report["communication_score"] > 0
    assert report["overall_score"] <= 100


def test_answer_evaluator_preserves_valid_parsed_model_result():
    class ValidEvaluationLLM:
        def invoke(self, prompt):
            class Response:
                content = '{"score": 8, "feedback": "Good explanation", "strengths": ["clear reasoning"], "weaknesses": [], "missing_points": [], "recommended_action": "new_topic", "recommended_topic": "graphs", "evaluation_failed": false}'

            return Response()

    evaluator = AnswerEvaluator.__new__(AnswerEvaluator)
    evaluator.llm = ValidEvaluationLLM()

    result = evaluator.evaluate("Explain a hash map.", "It maps keys to values.")

    assert result["score"] == 8
    assert result["feedback"] == "Good explanation"
    assert result["strengths"] == ["clear reasoning"]
    assert result["evaluation_failed"] is False


def test_answer_evaluator_extracts_score_from_plain_text():
    class PlainTextEvaluationLLM:
        def invoke(self, prompt):
            class Response:
                content = "Score: 7/10. The answer is mostly correct."

            return Response()

    evaluator = AnswerEvaluator.__new__(AnswerEvaluator)
    evaluator.llm = PlainTextEvaluationLLM()

    result = evaluator.evaluate("Explain a hash map.", "It maps keys to values.")

    assert result["score"] == 7
    assert result["evaluation_failed"] is False
