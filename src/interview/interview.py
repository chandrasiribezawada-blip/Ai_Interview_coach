import json

from src.factories.llm_factory import LLMFactory
from src.utils.helper import parse_json_response


class Interviewer:
    QUESTION_PLAN = ["coding", "cs_fundamentals", "project_rag", "adaptive", "adaptive"]
    VALID_CATEGORIES = {"coding", "cs_fundamentals", "project_rag", "adaptive"}
    VALID_DIFFICULTIES = {"easy", "medium", "hard"}

    def __init__(self):
        self.llm = LLMFactory.create_llm()

    @staticmethod
    def _question_key(question):
        return " ".join("".join(char.lower() if char.isalnum() else " " for char in str(question)).split())

    @staticmethod
    def _fallback_questions(category, focus_topic=""):
        questions = {
            "coding": [
                "Given an array of integers, find the longest consecutive sequence in O(n) time. Explain your approach.",
                "Given a sorted array, find two values that sum to a target in O(n) time. Explain the pointer invariant.",
                "How would you merge overlapping intervals, and what are the time and space complexities?",
            ],
            "cs_fundamentals": [
                "Explain the difference between a process and a thread, including when you would use each.",
                "What properties does a database transaction need to satisfy, and how does isolation affect concurrent updates?",
                "Describe what happens during a TCP connection handshake and why each step is needed.",
            ],
            "project_rag": [
                "Which project on your resume best matches this role, and what design trade-off did you make?",
                "Choose a project from your resume and explain how you tested that its main requirement was met.",
                "Which part of a project on your resume would you redesign for this job, and why?",
            ],
            "adaptive": [
                f"How would you diagnose and improve {focus_topic or 'a system'} when its performance degrades under load?",
                f"What trade-offs would you consider when designing a reliable solution for {focus_topic or 'a technical problem'}?",
                f"How would you test the correctness and edge cases of a solution involving {focus_topic or 'this technical area'}?",
            ],
        }
        return questions.get(category, questions["coding"])

    @classmethod
    def _avoid_repeated_question(cls, result, history, category, focus_topic=""):
        previous = {
            cls._question_key(item.get("question", ""))
            for item in history or []
            if isinstance(item, dict) and item.get("question")
        }
        if cls._question_key(result.get("question", "")) not in previous:
            return result

        for question in cls._fallback_questions(category, focus_topic):
            if cls._question_key(question) not in previous:
                result["question"] = question
                result["reason"] = "A non-repeated fallback was selected because the generated question matched interview history."
                return result
        result["question"] = cls._fallback_questions(category, focus_topic)[0]
        return result

    @staticmethod
    def build_question_plan():
        return list(Interviewer.QUESTION_PLAN)

    @staticmethod
    def validate_question_payload(payload, fallback_category="coding"):
        source = payload if isinstance(payload, dict) else {}
        question = str(source.get("question") or source.get("next_question") or "").strip()
        category = str(source.get("category") or source.get("type") or fallback_category).strip().lower()
        if category == "project":
            category = "project_rag"
        if category not in Interviewer.VALID_CATEGORIES:
            category = fallback_category

        difficulty = str(source.get("difficulty") or "medium").strip().lower()
        if difficulty not in Interviewer.VALID_DIFFICULTIES:
            difficulty = "medium"

        mode = str(source.get("mode") or "new_topic").strip() or "new_topic"
        reason = str(source.get("reason") or "").strip()
        if not question:
            question = Interviewer._fallback_questions(category)[0]

        return {
            "question": question,
            "category": category,
            "difficulty": difficulty,
            "mode": mode,
            "reason": reason or "Generated from the interview plan.",
        }

    def _clean_question_result(self, result, fallback_question, category, default_mode="new_topic"):
        normalized = self.validate_question_payload(result, fallback_category=category)
        normalized["mode"] = str(result.get("mode") or normalized.get("mode") or default_mode).strip() or default_mode
        normalized["question"] = normalized["question"] or fallback_question
        return normalized

    def generate_question(self, resume_context, job_description):
        prompt = f"""
You are an experienced technical interviewer for a placement/mock interview.
Return only a JSON object with:
- question: string
- category: one of coding, cs_fundamentals, project_rag, adaptive
- difficulty: easy|medium|hard
- mode: new_topic|follow_up
- reason: string

Resume context:
{resume_context}

Job description:
{job_description}

Ask exactly one high-quality technical question that is relevant to the role and candidate profile.
The first question must be a genuine coding/problem-solving question.
Do not ask a generic project question.
"""
        response = self.llm.invoke(prompt)
        result = parse_json_response(
            response,
            {
                "question": "Given an array of integers, find the longest consecutive sequence in O(n) time.",
                "category": "coding",
                "difficulty": "medium",
                "mode": "new_topic",
                "reason": "Core problem-solving question.",
            },
        )
        fallback = "Given an array of integers, find the longest consecutive sequence in O(n) time."
        return self._clean_question_result(result, fallback, "coding")

    def generate_question_for_category(self, category, resume_context, job_description, history=None, previous_question=None):
        category = "project_rag" if category == "project" else category
        history_text = json.dumps(history or [], ensure_ascii=True)
        previous_text = previous_question or ""

        prompt = f"""
You are an experienced technical interviewer.
Return only valid JSON with keys:
- question: string
- category: string
- difficulty: easy|medium|hard
- mode: follow_up|new_topic
- reason: string

Interview category request: {category}
Previous question: {previous_text}
Interview history: {history_text}
Resume context:
{resume_context}
Job description:
{job_description}

Rules:
1. Ask exactly one clear question.
2. For coding, ask a genuine coding/problem-solving question with algorithmic thinking and complexity.
3. For cs_fundamentals, ask a general CS or software engineering concept question.
4. For project_rag, ask one project/resume/job-related question using the provided context and retrieved details.
5. For adaptive, decide whether it should be a follow-up or a new topic based on performance history.
6. Do not include any extra explanation outside JSON.
"""
        response = self.llm.invoke(prompt)
        default = {
            "question": self._fallback_questions(category)[0],
            "category": category,
            "difficulty": "medium",
            "mode": "new_topic",
            "reason": "Fallback question generated from the interview plan.",
        }
        result = parse_json_response(response, default)
        fallback = default["question"]
        cleaned = self._clean_question_result(result, fallback, category, default_mode="new_topic")
        return self._avoid_repeated_question(cleaned, history, category)

    @staticmethod
    def derive_adaptive_context(history):
        previous_scores = []
        weak_signals = []
        for item in history or []:
            if not isinstance(item, dict):
                continue
            try:
                previous_scores.append(float(item.get("score", 0) or 0))
            except (TypeError, ValueError):
                pass

            for key in ("weaknesses", "missing_points", "recommended_topic"):
                values = item.get(key, []) or []
                if isinstance(values, str):
                    values = [values]
                for value in values:
                    if value:
                        weak_signals.append(str(value))

        avg_score = sum(previous_scores) / len(previous_scores) if previous_scores else 0
        focus_text = " ".join(weak_signals).lower()
        mode = "follow_up" if (weak_signals and avg_score < 7) or avg_score < 5 else "new_topic"

        focus_topic = "system design and scalability"
        reason = "Candidate performance indicates a need for deeper follow-up on a weak area."

        if any(token in focus_text for token in ["dbms", "sql", "normalization", "acid", "transaction"]):
            focus_topic = "DBMS and normalization"
            reason = "Candidate struggled with database fundamentals, so the follow-up targets normalization and ACID behavior."
        elif any(token in focus_text for token in ["os", "process", "thread", "scheduler", "memory"]):
            focus_topic = "Operating systems and process management"
            reason = "Candidate needs reinforcement on process/thread and scheduling concepts."
        elif any(token in focus_text for token in ["network", "tcp", "http", "socket", "protocol"]):
            focus_topic = "Computer networks and protocol design"
            reason = "Candidate needs a deeper look at networking fundamentals and request flow."
        elif any(token in focus_text for token in ["oop", "inheritance", "polymorphism", "encapsulation"]):
            focus_topic = "OOP and design principles"
            reason = "Candidate needs reinforcement on object-oriented design and abstraction."
        elif any(token in focus_text for token in ["algorithm", "array", "hash", "tree", "graph", "complexity"]):
            focus_topic = "Data structures and algorithmic complexity"
            reason = "Candidate needs a deeper algorithmic follow-up around complexity and data structures."

        if not weak_signals:
            focus_topic = "system design and scalability"
            mode = "new_topic" if avg_score >= 6 else "follow_up"
            reason = "No clear weak concept was identified, so the question targets a relevant technical area."

        return {
            "mode": mode,
            "focus_topic": focus_topic,
            "reason": reason,
        }

    def generate_adaptive_question(self, history, resume_context, job_description):
        adaptive_context = self.derive_adaptive_context(history)
        default_mode = adaptive_context["mode"]
        focus_topic = adaptive_context["focus_topic"]
        reason = adaptive_context["reason"]

        prompt = f"""
You are a professional interviewer generating the next adaptive technical question.
Return only valid JSON with keys:
- question: string
- category: adaptive
- mode: follow_up|new_topic
- difficulty: easy|medium|hard
- reason: string
- recommended_topic: string (optional)

Interview history: {json.dumps(history or [], ensure_ascii=True)}
Resume context: {resume_context}
Job description: {job_description}
Adaptive focus topic: {focus_topic}
Adaptive reason: {reason}

Decision rules:
- If the candidate showed weakness in {focus_topic}, ask a targeted follow-up question on that topic.
- If the candidate is performing well, ask a deeper but relevant new technical question.
- Keep it technical, job-relevant, and different from earlier Qs.
- Do not ask a repeated question.
- The final question must be a single, clear interview question.
"""
        response = self.llm.invoke(prompt)
        default = {
            "question": f"In a system with high write volume, how would you design a solution to preserve consistency and scalability while minimizing latency for {focus_topic}?",
            "category": "adaptive",
            "mode": default_mode,
            "difficulty": "medium",
            "reason": reason,
            "recommended_topic": focus_topic,
        }
        result = parse_json_response(response, default)
        cleaned = self._clean_question_result(result, default["question"], "adaptive", default_mode=default_mode)
        return self._avoid_repeated_question(cleaned, history, "adaptive", focus_topic)

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