import streamlit as st
import pandas as pd


def _safe_score(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dedupe(items):
    seen = set()
    ordered = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        ordered.append(text)
    return ordered[:10]


def _score_for_category(history, category):
    values = []
    for item in history:
        if not isinstance(item, dict):
            continue
        item_category = str(item.get("category", "")).lower()
        if item_category == category:
            score = _safe_score(item.get("score"))
            if score is not None:
                values.append(score)
    if not values:
        return 0.0
    return round(sum(values) / len(values) * 10, 1)


def _communication_score(history):
    valid = [item for item in history if isinstance(item, dict)]
    if not valid:
        return 0
    wpm_values = []
    filler_values = []
    for item in valid:
        wpm = _safe_score(item.get("wpm"))
        if wpm is not None:
            wpm_values.append(wpm)
        filler = _safe_score(item.get("filler_rate_pct"))
        if filler is not None:
            filler_values.append(filler)
    if not wpm_values:
        return 0
    avg_wpm = sum(wpm_values) / len(wpm_values)
    avg_filler = sum(filler_values) / len(filler_values) if filler_values else 0
    score = 60 + min(25, max(0, avg_wpm - 50) / 2) - min(25, avg_filler * 0.7)
    return max(0, min(100, round(score)))


def _build_report_from_history(history):
    valid_history = []
    for item in history:
        if not isinstance(item, dict):
            continue
        score = _safe_score(item.get("score"))
        if score is None:
            continue
        valid_history.append(item)

    if not valid_history:
        return {
            "overall_score": 0,
            "technical_score": 0,
            "coding_score": 0,
            "cs_fundamentals_score": 0,
            "project_score": 0,
            "adaptive_score": 0,
            "communication_score": 0,
            "strengths": [],
            "weaknesses": [],
            "missing_points": [],
            "summary": "No valid answers were submitted for this interview.",
            "recommendations": [],
            "question_breakdown": [],
        }

    scores = [_safe_score(item.get("score")) for item in valid_history]
    overall_score = round((sum(scores) / len(scores)) * 10, 1)
    technical_score = round(
        sum(_safe_score(item.get("score")) for item in valid_history) / len(valid_history) * 10,
        1,
    )

    coding_score = _score_for_category(valid_history, "coding")
    cs_score = _score_for_category(valid_history, "cs_fundamentals")
    project_score = _score_for_category(valid_history, "project_rag")
    adaptive_score = _score_for_category(valid_history, "adaptive")
    communication_score = _communication_score(valid_history)

    strengths = []
    weaknesses = []
    missing_points = []
    recommendations = []

    for item in valid_history:
        strengths.extend(item.get("strengths", []) or [])
        weaknesses.extend(item.get("weaknesses", []) or [])
        missing_points.extend(item.get("missing_points", []) or [])
        recommended_topic = item.get("recommended_topic")
        if recommended_topic:
            recommendations.append(str(recommended_topic))

    for item in valid_history:
        category = str(item.get("category", "")).lower()
        if category in {"coding", "cs_fundamentals", "project_rag", "adaptive"}:
            score = _safe_score(item.get("score"))
            if score is not None and score < 5:
                recommendations.append(f"Practice {category.replace('_', ' ')} concepts and explain the trade-offs clearly.")

    return {
        "overall_score": overall_score,
        "technical_score": technical_score,
        "coding_score": coding_score,
        "cs_fundamentals_score": cs_score,
        "project_score": project_score,
        "adaptive_score": adaptive_score,
        "communication_score": communication_score,
        "strengths": _dedupe(strengths),
        "weaknesses": _dedupe(weaknesses),
        "missing_points": _dedupe(missing_points),
        "summary": "The candidate showed a balanced mix of technical reasoning, communication, and job-relevant understanding.",
        "recommendations": _dedupe(recommendations)[:5],
        "question_breakdown": valid_history,
    }


def show_report():
    st.title("📊 AI Interview Report")

    if st.session_state.get("interview_mode") == "Voice Interview" and st.session_state.get("voice_history"):
        history = st.session_state.get("voice_history", [])
    else:
        history = st.session_state.get("question_history", [])

    if not history:
        st.warning("No interview answers have been submitted yet.")
        if st.button("Back to Home", use_container_width=True):
            st.session_state.page = "Home"
            st.rerun()
        return

    report = _build_report_from_history(history)

    st.subheader("INTERVIEW COMPLETE")
    st.markdown(f"### OVERALL SCORE: {report['overall_score']}/100")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Coding", f"{report['coding_score']}/100")
    col2.metric("CS Fundamentals", f"{report['cs_fundamentals_score']}/100")
    col3.metric("Project / RAG", f"{report['project_score']}/100")
    col4.metric("Adaptive", f"{report['adaptive_score']}/100")
    col5.metric("Communication", f"{report['communication_score']}/100")

    st.divider()
    st.subheader("Technical Knowledge")
    st.metric("Technical Knowledge", f"{report['technical_score']}/100")

    st.subheader("Strengths")
    for strength in report["strengths"] or ["Strong technical reasoning and clear explanation."]:
        st.write(f"- {strength}")

    st.subheader("Weaknesses")
    for weakness in report["weaknesses"] or ["Continue practicing deeper technical explanations and edge-case reasoning."]:
        st.write(f"- {weakness}")

    st.subheader("Missing Concepts")
    for point in report["missing_points"] or ["No major concept gaps identified from the submitted answers."]:
        st.write(f"- {point}")

    st.subheader("Recommendations")
    for recommendation in report["recommendations"] or ["Review core CS fundamentals and improve problem-solving explanations."]:
        st.write(f"- {recommendation}")

    st.divider()
    st.subheader("Question-by-question performance")
    df = pd.DataFrame(report["question_breakdown"])
    if not df.empty:
        display_cols = ["question_number", "category", "score", "feedback"]
        st.dataframe(df[display_cols], use_container_width=True)

    if st.button("Start New Interview", use_container_width=True):
        _reset_interview_state()
        st.session_state.page = "Home"
        st.rerun()


def _reset_interview_state():
    reset_keys = {
        "pipeline",
        "vectorstore",
        "vectorstore_source_fingerprint",
        "question",
        "feedback",
        "question_number",
        "current_question",
        "current_question_number",
        "current_question_type",
        "current_question_mode",
        "interview_started",
        "question_history",
        "answer_history",
        "scores",
        "conversation_history",
        "retrieved_context",
        "last_evaluation",
        "report",
        "voice_mode",
        "voice_history",
        "voice_report",
        "voice_tts_cache",
        "voice_tts_errors",
        "voice_transcript_cache",
        "voice_transcription_errors",
        "voice_say_text",
        "voice_spoken_question",
        "voice_interview_topics",
    }
    for key in reset_keys:
        st.session_state.pop(key, None)
    for key in list(st.session_state.keys()):
        if key.startswith(("answer_", "voice_recording_", "voice_transcript_")):
            st.session_state.pop(key, None)
    st.session_state.question_number = 1