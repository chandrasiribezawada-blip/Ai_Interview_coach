from src.utils.helper import parse_json_response


def _clamp_int(value, minimum=0, maximum=100):
    try:
        return max(minimum, min(maximum, int(value)))
    except (TypeError, ValueError):
        return minimum


def _fallback_scores(history):
    if not history:
        return {
            "overall_score": 0,
            "content_score": 0,
            "communication_score": 0,
        }

    scores = []
    wpms = []
    filler_counts = []

    for item in history:
        if not isinstance(item, dict):
            continue
        try:
            scores.append(float(item.get("score", 0) or 0))
        except (TypeError, ValueError):
            pass
        try:
            wpms.append(float(item.get("wpm", 0) or 0))
        except (TypeError, ValueError):
            pass
        try:
            filler_counts.append(float(item.get("filler_count", 0) or 0))
        except (TypeError, ValueError):
            pass

    if not scores:
        avg_score_10 = 0.0
    else:
        avg_score_10 = sum(scores) / len(scores)

    overall = _clamp_int(round(avg_score_10 * 10), 0, 100)
    content = overall

    if wpms:
        avg_wpm = sum(wpms) / len(wpms)
    else:
        avg_wpm = 0

    if filler_counts:
        avg_fillers = sum(filler_counts) / len(filler_counts)
    else:
        avg_fillers = 0

    communication = 60 + min(25, max(0, avg_wpm - 50) / 2) - min(25, avg_fillers * 10)
    communication = max(0, min(100, round(communication)))

    return {
        "overall_score": overall,
        "content_score": content,
        "communication_score": communication,
    }


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
        default = {
            "overall_score": 0,
            "content_score": 0,
            "communication_score": 0,
            "summary": "A report could not be generated from the model response.",
            "strengths": [],
            "weaknesses": [],
            "missing_points": [],
            "fluency_feedback": "Fluency feedback is unavailable.",
        }
        result = parse_json_response(response, default)
        report = {}

        fallback_scores = _fallback_scores(history)
        for field in ("overall_score", "content_score", "communication_score"):
            value = result.get(field)
            if value is None:
                report[field] = fallback_scores[field]
            else:
                try:
                    report[field] = max(0, min(100, int(value)))
                except (TypeError, ValueError):
                    report[field] = fallback_scores[field]

        for field in ("strengths", "weaknesses", "missing_points"):
            value = result.get(field)
            report[field] = [str(item) for item in value] if isinstance(value, list) else []

        for field in ("summary", "fluency_feedback"):
            value = result.get(field)
            if value is None or str(value).strip() == "":
                report[field] = default[field]
            else:
                report[field] = str(value)

        if history:
            report["average_wpm"] = round(sum(item.get("wpm", 0) for item in history) / len(history))
            report["total_filler_words"] = sum(item.get("filler_count", 0) for item in history)
            report["average_duration_sec"] = round(
                sum(item.get("duration_sec", 0) for item in history) / len(history), 1
            )
        else:
            report.update(average_wpm=0, total_filler_words=0, average_duration_sec=0.0)

        if report["overall_score"] == 0 and report["content_score"] == 0 and report["communication_score"] == 0:
            fallback = _fallback_scores(history)
            report["overall_score"] = fallback["overall_score"]
            report["content_score"] = fallback["content_score"]
            report["communication_score"] = fallback["communication_score"]

        return report