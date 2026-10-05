import json
import logging
import math
import re

from src.config.settings import Settings
from src.factories.llm_factory import LLMFactory
from src.utils.helper import parse_json_response

logger = logging.getLogger(__name__)


class AnswerEvaluator:

    def __init__(self):
        self.llm = LLMFactory.create_llm(max_tokens=1200)

    def _normalize_score(self, value, default=None):
        try:
            score = float(value)
        except (TypeError, ValueError):
            return default
        if not math.isfinite(score) or not 0 <= score <= 10:
            return default
        return score

    def _string_list(self, value):
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, tuple):
            return [str(item) for item in value]
        return []

    def _extract_numeric_score(self, text, default=None):
        if text is None:
            return default
        patterns = [
            r"score\s*[:=]\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            r"overall\s*[:=]\s*(\d+(?:\.\d+)?)\s*(?:/\s*10)?",
            r"(\d+(?:\.\d+)?)\s*/\s*10",
        ]
        for pattern in patterns:
            match = re.search(pattern, str(text), re.IGNORECASE)
            if match:
                return self._normalize_score(match.group(1), default)
        return default

    def _build_result(self, parsed):
        score = self._normalize_score(parsed.get("score"))
        evaluation_failed = score is None
        return {
            "score": round(score, 2) if score is not None else None,
            "correctness": self._normalize_score(parsed.get("correctness")),
            "relevance": self._normalize_score(parsed.get("relevance")),
            "technical_depth": self._normalize_score(parsed.get("technical_depth")),
            "completeness": self._normalize_score(parsed.get("completeness")),
            "feedback": str(parsed.get("feedback") or "Evaluation could not be parsed. Please retry."),
            "strengths": self._string_list(parsed.get("strengths")),
            "weaknesses": self._string_list(parsed.get("weaknesses")),
            "missing_points": self._string_list(parsed.get("missing_points")),
            "recommended_action": str(parsed.get("recommended_action") or "follow_up"),
            "recommended_topic": str(parsed.get("recommended_topic") or "General technical discussion"),
            "evaluation_failed": evaluation_failed,
        }

    @staticmethod
    def _failure(error, raw_response="", diagnostics=None):
        result = {
            "score": None,
            "correctness": None,
            "relevance": None,
            "technical_depth": None,
            "completeness": None,
            "feedback": "The answer could not be evaluated. Your answer was preserved; retry evaluation.",
            "strengths": [],
            "weaknesses": [],
            "missing_points": [],
            "recommended_action": "follow_up",
            "recommended_topic": "General technical discussion",
            "evaluation_failed": True,
            "error": error,
        }
        if diagnostics:
            result["diagnostics"] = diagnostics
        if raw_response:
            result["raw_response"] = raw_response[:4000]
        return result

    @staticmethod
    def _safe_error_message(error):
        message = str(error)
        api_key = Settings.GROQ_API_KEY
        if api_key:
            message = message.replace(api_key, "[REDACTED]")
        return message[:1000]

    def evaluate(
        self,
        question,
        candidate_answer,
        category="technical",
        context="",
    ):
        prompt = self._evaluation_prompt(question, candidate_answer, category, context)
        raw_response = ""
        diagnostics = {}
        for attempt in (1, 2):
            logger.info("Starting Groq answer evaluation (attempt %d, category=%s)", attempt, category)
            try:
                response = self.llm.invoke(prompt)
            except Exception as error:
                safe_error = self._safe_error_message(error)
                logger.error("Groq answer evaluation request failed (%s): %s", type(error).__name__, safe_error)
                return self._failure(
                    f"Groq request failed ({type(error).__name__}): {safe_error}",
                    raw_response,
                    diagnostics,
                )

            raw_response = str(getattr(response, "content", response))
            metadata = getattr(response, "response_metadata", {}) or {}
            diagnostics = {
                "status": "response_received",
                "model": metadata.get("model_name", "unknown"),
                "finish_reason": metadata.get("finish_reason", "unknown"),
                "attempt": attempt,
            }
            logger.info(
                "Groq evaluation response received (model=%s, finish_reason=%s)",
                diagnostics["model"],
                diagnostics["finish_reason"],
            )
            logger.debug("Raw Groq evaluation response (attempt %d): %s", attempt, raw_response[:4000])

            parsed = parse_json_response(response, {"__invalid_json__": True})
            logger.debug("Parsed Groq evaluation JSON (attempt %d): %s", attempt, json.dumps(parsed, default=str))
            score = self._normalize_score(parsed.get("score")) if not parsed.get("__invalid_json__") else None
            logger.info("Groq evaluation extracted score (attempt %d): %s", attempt, score)
            diagnostics["parsed"] = parsed
            diagnostics["extracted_score"] = score

            if score is not None:
                return self._build_result(parsed)

            if attempt == 1:
                prompt = self._evaluation_prompt(question, candidate_answer, category, context, retry=True)
                continue

            finish_reason = diagnostics.get("finish_reason")
            if parsed.get("__invalid_json__"):
                if not raw_response.lstrip().startswith("{"):
                    extracted_score = self._extract_numeric_score(raw_response)
                    if extracted_score is not None:
                        logger.info("Recovered explicit plain-text evaluation score: %s", extracted_score)
                        return self._build_result(
                            {
                                "score": extracted_score,
                                "feedback": raw_response.strip(),
                                "strengths": [],
                                "weaknesses": [],
                                "missing_points": [],
                                "recommended_action": "follow_up",
                                "recommended_topic": "General technical discussion",
                                "evaluation_failed": False,
                            }
                        )
                error_message = (
                    f"Groq returned malformed or truncated JSON (finish_reason={finish_reason}) after 2 attempts."
                )
            else:
                error_message = "Groq returned a missing or invalid score; expected a number from 0 to 10."
            logger.error("Answer evaluation failed: %s", error_message)
            return self._failure(error_message, raw_response, diagnostics)

        return self._failure("Evaluation did not complete.", raw_response, diagnostics)

    @staticmethod
    def _evaluation_prompt(question, candidate_answer, category, context, retry=False):
        retry_instruction = "This is a retry. Keep the JSON compact and complete." if retry else ""
        coding_rubric = ""
        if category == "coding":
            coding_rubric = "For coding, assess problem understanding, algorithm, correctness, time and space complexity, and edge cases. "
        return f"""
You are an experienced technical interviewer. Judge answer correctness separately from evaluation validity.
An incorrect or weak answer is a successful evaluation and must receive a low score with constructive feedback.
Never mark evaluation_failed true because the candidate is wrong.
{coding_rubric}{retry_instruction}
Return ONLY valid JSON. Do not include markdown fences or additional text.
Use exactly these keys: score (number 0-10), correctness (number 0-10), relevance (number 0-10),
technical_depth (number 0-10), completeness (number 0-10), feedback (string), strengths (array of strings),
weaknesses (array of strings), missing_points (array of strings), recommended_action (follow_up or new_topic),
recommended_topic (string), evaluation_failed (boolean). Set evaluation_failed to false when you return a valid score.

Interview category: {category}
Interview question: {question}
Candidate answer: {candidate_answer}
Additional context: {context or "No additional context provided."}
"""

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
            {"score": None, "feedback": "Evaluation could not be parsed.", "missing_points": [], "strengths": [], "evaluation_failed": True},
        )
        score = None
        if result.get("score") is not None:
            try:
                score = max(0, min(10, float(result.get("score"))))
            except (TypeError, ValueError):
                score = None
        if score is None and isinstance(getattr(response, "content", response), str):
            score = self._extract_numeric_score(getattr(response, "content", response), default=None)
        if score is not None:
            score = max(0, min(10, score))

        return {
            "score": round(score, 2) if score is not None else None,
            "feedback": str(result.get("feedback", "")) or "Evaluation could not be parsed; please retry.",
            "missing_points": self._string_list(result.get("missing_points")),
            "strengths": self._string_list(result.get("strengths")),
            "evaluation_failed": bool(result.get("evaluation_failed", score is None)),
        }