from src.interview.interview import Interviewer


class FakeLLM:
    def __init__(self, content):
        self.content = content

    def invoke(self, prompt):
        class Response:
            pass

        response = Response()
        response.content = self.content
        return response


def test_question_plan_follows_required_sequence():
    plan = Interviewer.build_question_plan()
    assert plan == [
        "coding",
        "cs_fundamentals",
        "project_rag",
        "adaptive",
        "adaptive",
    ]


def test_question_payload_is_valid_and_non_empty():
    payload = {
        "question": "Given an array of integers, find the longest consecutive sequence in O(n) time.",
        "category": "coding",
        "difficulty": "medium",
        "mode": "new_topic",
        "reason": "Core problem-solving question",
    }

    validated = Interviewer.validate_question_payload(payload, fallback_category="coding")
    assert validated["question"]
    assert validated["category"] == "coding"
    assert validated["difficulty"] in {"easy", "medium", "hard"}
    assert validated["mode"]


def test_adaptive_focus_targets_weak_area_from_history():
    history = [
        {"category": "cs_fundamentals", "score": 2.0, "weaknesses": ["DBMS normalization", "ACID properties"]},
        {"category": "coding", "score": 8.0, "strengths": ["Strong arrays and recursion"]},
    ]

    adaptive_context = Interviewer.derive_adaptive_context(history)
    assert adaptive_context["mode"] == "follow_up"
    assert adaptive_context["focus_topic"]
    assert "dbms" in adaptive_context["focus_topic"].lower() or "normalization" in adaptive_context["focus_topic"].lower()


def test_malformed_question_output_uses_category_fallback():
    interviewer = Interviewer.__new__(Interviewer)
    interviewer.llm = FakeLLM("not valid JSON")

    result = interviewer.generate_question_for_category(
        "cs_fundamentals", "context", "job description", history=[]
    )

    assert result["category"] == "cs_fundamentals"
    assert "process" in result["question"].lower() or "transaction" in result["question"].lower() or "tcp" in result["question"].lower()
    assert "technical concept you are confident" not in result["question"].lower()


def test_repeated_question_output_uses_an_unused_fallback():
    repeated = "Explain the difference between a process and a thread."
    interviewer = Interviewer.__new__(Interviewer)
    interviewer.llm = FakeLLM(
        '{"question": "Explain the difference between a process and a thread.", '
        '"category": "cs_fundamentals", "difficulty": "medium", "mode": "new_topic"}'
    )

    result = interviewer.generate_question_for_category(
        "cs_fundamentals",
        "context",
        "job description",
        history=[{"question": repeated, "score": 5}],
    )

    assert result["question"] != repeated
