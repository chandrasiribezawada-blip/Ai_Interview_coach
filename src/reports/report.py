from src.utils.helper import parse_json_response


class ReportGenerator:

    def generate(self, session):

        report = "\n"
        report += "=" * 60
        report += "\nFINAL INTERVIEW REPORT\n"
        report += "=" * 60

        report += f"\n\nQuestions Attempted : {len(session.questions)}"

        report += f"\nAverage Score      : {session.average_score()}/10"

        report += "\n\nDetailed Feedback"

        report += "\n" + "-" * 60

        for i in range(len(session.questions)):

            report += f"\n\nQuestion {i+1}\n"

            report += "-" * 30

            report += "\n"

            report += session.questions[i]

            report += "\n\n"

            report += session.feedback[i]

        return report

    def generate_voice(self, llm, topic, history):
        import json

        prompt = f"""
You are an interview coach. Produce a constructive final interview report.
Return only a JSON object containing integer overall_score, content_score, and
communication_score (each 0-100), string summary, array strengths, array weaknesses,
array missing_points, and string fluency_feedback.

Interview topic: {topic}
Interview history: {json.dumps(history, ensure_ascii=True)}
"""
        response = llm.invoke(prompt)
        result = parse_json_response(
            response,
            {
                "overall_score": 0,
                "content_score": 0,
                "communication_score": 0,
                "summary": "A report could not be generated from the model response.",
                "strengths": [],
                "weaknesses": [],
                "missing_points": [],
                "fluency_feedback": "Fluency feedback is unavailable.",
            },
        )
        report = {}
        for field in ("overall_score", "content_score", "communication_score"):
            try:
                report[field] = max(0, min(100, int(result.get(field, 0))))
            except (TypeError, ValueError):
                report[field] = 0

        for field in ("strengths", "weaknesses", "missing_points"):
            value = result.get(field)
            report[field] = [str(item) for item in value] if isinstance(value, list) else []

        for field in ("summary", "fluency_feedback"):
            report[field] = str(result.get(field, ""))

        if history:
            report["average_wpm"] = round(sum(item.get("wpm", 0) for item in history) / len(history))
            report["total_filler_words"] = sum(item.get("filler_count", 0) for item in history)
            report["average_duration_sec"] = round(
                sum(item.get("duration_sec", 0) for item in history) / len(history), 1
            )
        else:
            report.update(average_wpm=0, total_filler_words=0, average_duration_sec=0.0)
        return report