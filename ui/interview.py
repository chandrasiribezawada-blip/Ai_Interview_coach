import hashlib
import html
import logging

import streamlit as st
from src.interview.pipeline import InterviewPipeline
from src.interview.voice import analyze_speech, audio_seconds, text_to_speech, transcribe

logger = logging.getLogger(__name__)


def _safe_score(value, default=None):
    try:
        score = float(value)
        return score
    except (TypeError, ValueError):
        return default


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
        "evaluation_pending_advance",
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
    st.session_state.current_question_number = 1
    st.session_state.interview_started = False


def _ensure_interview_state():
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = InterviewPipeline()
    if "question_history" not in st.session_state:
        st.session_state.question_history = []
    if "answer_history" not in st.session_state:
        st.session_state.answer_history = []
    if "scores" not in st.session_state:
        st.session_state.scores = []
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "current_question_number" not in st.session_state:
        st.session_state.current_question_number = 1
    if "current_question_slot" not in st.session_state:
        st.session_state.current_question_slot = 0
    if "current_question_type" not in st.session_state:
        st.session_state.current_question_type = "coding"
    if "current_question_mode" not in st.session_state:
        st.session_state.current_question_mode = "new_topic"
    if "interview_started" not in st.session_state:
        st.session_state.interview_started = False
    if "evaluation_pending_advance" not in st.session_state:
        st.session_state.evaluation_pending_advance = False
    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []
    if "voice_mode" not in st.session_state:
        st.session_state.voice_mode = "Text Interview"


def _generate_question_for_slot(vectorstore, job_description):
    pipeline = st.session_state.pipeline
    current_number = st.session_state.current_question_number
    if st.session_state.get("current_question") and st.session_state.get("current_question_slot") == current_number and st.session_state.get("interview_started"):
        return {
            "question": st.session_state.current_question,
            "category": st.session_state.current_question_type,
            "mode": st.session_state.current_question_mode,
            "difficulty": "medium",
        }

    history = st.session_state.question_history
    plan = pipeline.interviewer.build_question_plan()
    category = plan[current_number - 1] if current_number - 1 < len(plan) else "adaptive"

    if category == "project_rag":
        resume_context = pipeline.retrieve_context(vectorstore, job_description)
    else:
        resume_context = pipeline.retrieve_context(vectorstore, f"{job_description} {category}")

    if category == "adaptive":
        result = pipeline.interviewer.generate_adaptive_question(history, resume_context, job_description)
    else:
        result = pipeline.interviewer.generate_question_for_category(
            category,
            resume_context,
            job_description,
            history=history,
            previous_question=st.session_state.get("current_question", ""),
        )

    st.session_state.current_question = result["question"]
    st.session_state.current_question_type = result.get("category", category)
    st.session_state.current_question_mode = result.get("mode", "new_topic")
    st.session_state.current_question_slot = current_number
    st.session_state.interview_started = True
    return result


def _render_voice_question(vectorstore, job_description):
    question_number = st.session_state.current_question_number
    voice_history = st.session_state.voice_history
    st.progress(len(voice_history) / 5, text=f"Question {question_number} of 5")

    question_key = hashlib.sha256(f"{question_number}:{st.session_state.current_question}".encode("utf-8")).hexdigest()[:16]
    tts_cache = st.session_state.setdefault("voice_tts_cache", {})
    tts_errors = st.session_state.setdefault("voice_tts_errors", {})
    if question_key not in tts_cache and question_key not in tts_errors:
        try:
            tts_cache[question_key] = text_to_speech(st.session_state.current_question)
        except Exception as error:
            tts_errors[question_key] = str(error)

    if question_key in tts_errors:
        st.warning("Voice playback unavailable. You can continue with the text question.")
        if st.button("Retry Audio", key=f"retry_tts_{question_key}"):
            del tts_errors[question_key]
            st.rerun()
        if st.button("Continue with Text", key=f"continue_text_{question_key}"):
            st.session_state.voice_mode = "Text Interview"
            st.rerun()
    elif question_key in tts_cache:
        st.audio(tts_cache[question_key], format="audio/mp3", autoplay=True)
        if st.button("🔁 Replay question", key=f"replay_{question_key}"):
            st.audio(tts_cache[question_key], format="audio/mp3", autoplay=True)

    audio = st.audio_input("Record your answer", key=f"voice_recording_{question_number}")
    if audio is not None:
        audio_bytes = audio.getvalue()
        try:
            duration = audio_seconds(audio_bytes)
        except Exception:
            duration = 0.0

        transcript_cache = st.session_state.setdefault("voice_transcript_cache", {})
        transcription_errors = st.session_state.setdefault("voice_transcription_errors", {})
        recording_key = hashlib.sha256(audio_bytes).hexdigest()
        if recording_key not in transcript_cache and recording_key not in transcription_errors:
            try:
                with st.spinner("Transcribing your answer..."):
                    transcript_cache[recording_key] = transcribe(audio_bytes)
            except Exception as error:
                transcript_cache[recording_key] = ""
                transcription_errors[recording_key] = str(error)

        if recording_key in transcription_errors:
            st.warning(f"Whisper transcription failed. You can enter the answer manually. {transcription_errors[recording_key]}")
        transcript = st.text_area(
            "Transcript (edit if needed)",
            value=transcript_cache.get(recording_key, ""),
            key=f"voice_transcript_{recording_key}",
        )

        if st.button("Submit Answer", type="primary", key=f"submit_voice_{recording_key}"):
            if not transcript.strip():
                st.warning("Please provide an answer before submitting.")
                st.stop()

            try:
                metrics = analyze_speech(transcript, duration)
            except Exception as error:
                logger.warning("Voice metric analysis failed: %s", error)
                metrics = {}
            evaluation = st.session_state.pipeline.evaluate_answer(
                question=st.session_state.current_question,
                candidate_answer=transcript,
                category=st.session_state.current_question_type,
            )
            if evaluation.get("evaluation_failed") and evaluation.get("score") is None:
                _render_evaluation_failure(evaluation)
                st.stop()

            entry = {
                "question_number": question_number,
                "category": st.session_state.current_question_type,
                "question": st.session_state.current_question,
                "answer": transcript,
                "score": evaluation.get("score"),
                "correctness": evaluation.get("correctness"),
                "relevance": evaluation.get("relevance"),
                "technical_depth": evaluation.get("technical_depth"),
                "completeness": evaluation.get("completeness"),
                "feedback": evaluation["feedback"],
                "strengths": evaluation.get("strengths", []),
                "weaknesses": evaluation.get("weaknesses", []),
                "missing_points": evaluation.get("missing_points", []),
                "recommended_action": evaluation.get("recommended_action", "follow_up"),
                "recommended_topic": evaluation.get("recommended_topic", "General technical discussion"),
                **metrics,
            }
            st.session_state.question_history.append(entry)
            st.session_state.scores.append(float(entry["score"]))
            st.session_state.last_evaluation = evaluation
            st.session_state.voice_history.append(entry)
            st.session_state.evaluation_pending_advance = True
            st.rerun()


def _render_evaluation_failure(evaluation):
    st.error(f"Evaluation failed: {evaluation.get('error', 'No valid score was returned by Groq.')}")
    diagnostics = evaluation.get("diagnostics")
    raw_response = evaluation.get("raw_response")
    if diagnostics or raw_response:
        with st.expander("Evaluation diagnostics (development)"):
            if diagnostics:
                st.json(diagnostics)
            if raw_response:
                st.code(raw_response, language="text")


def _render_evaluation_result(evaluation):
    st.subheader("ANSWER EVALUATION")
    st.success(f"Score: {evaluation['score']}/10")
    st.write("**Feedback**")
    st.write(evaluation.get("feedback", ""))
    if evaluation.get("strengths"):
        st.write("**What you did well**")
        for strength in evaluation["strengths"]:
            st.write(f"- {strength}")
    if evaluation.get("missing_points"):
        st.write("**What is missing**")
        for point in evaluation["missing_points"]:
            st.write(f"- {point}")
    if evaluation.get("recommended_topic"):
        st.write(f"**Recommended:** Review {evaluation['recommended_topic']}.")


def _continue_after_evaluation(vectorstore, job_description):
    question_number = st.session_state.current_question_number
    st.session_state.evaluation_pending_advance = False
    if question_number >= 5:
        st.session_state.page = "Report"
        st.rerun()

    st.session_state.current_question = ""
    st.session_state.current_question_slot = 0
    st.session_state.current_question_number = question_number + 1
    _generate_question_for_slot(vectorstore, job_description)
    st.rerun()


def show_interview():
    _ensure_interview_state()
    st.title("INTERVIEWMENTOR AI")
    st.subheader("AI MOCK INTERVIEW")
    st.markdown(
        """
        <div style="padding: 0.9rem 1rem; border: 1px solid #334155; border-radius: 10px; background: #111827; margin-bottom: 1rem;">
            <strong>Candidate Profile: Ready ✓</strong><br>
            <span>Resume: Uploaded ✓</span> &nbsp;|&nbsp; <span>Job Description: Uploaded ✓</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Answer 5 structured technical questions covering coding, CS fundamentals, project/RAG context, and adaptive follow-ups.")
    st.divider()

    if "pipeline" not in st.session_state:
        st.session_state.pipeline = InterviewPipeline()
    pipeline = st.session_state.pipeline

    source_digest = hashlib.sha256()
    for source_path in ("data/resume/resume.pdf", "data/jd/job_description.txt"):
        try:
            with open(source_path, "rb") as source_file:
                source_digest.update(source_file.read())
        except OSError as error:
            st.error(f"Could not read uploaded interview documents: {error}")
            st.stop()
    source_fingerprint = source_digest.hexdigest()

    if "vectorstore" not in st.session_state or st.session_state.get("vectorstore_source_fingerprint") != source_fingerprint:
        try:
            with st.spinner("📄 Processing Resume and Job Description..."):
                vectorstore = pipeline.build_resume_vectorstore("data/resume/resume.pdf")
            st.session_state.vectorstore = vectorstore
            st.session_state.vectorstore_source_fingerprint = source_fingerprint
        except Exception as error:
            st.error(f"Could not build the FAISS index: {error}")
            st.stop()
    vectorstore = st.session_state.vectorstore

    with open("data/jd/job_description.txt", "r", encoding="utf-8") as file:
        job_description = file.read()

    if "interview_mode" not in st.session_state:
        st.session_state.interview_mode = "Text Interview"
    interview_mode = st.radio("Interview mode", ["Text Interview", "Voice Interview"], horizontal=True, key="interview_mode")
    st.session_state.voice_mode = interview_mode

    progress_value = min((st.session_state.current_question_number - 1) / 5, 1.0)
    st.progress(progress_value, text=f"Interview Progress • Q{st.session_state.current_question_number} / 5")

    if not st.session_state.interview_started or not st.session_state.current_question:
        _generate_question_for_slot(vectorstore, job_description)

    st.markdown(
        f"""
        <div style="padding: 1rem 1.2rem; border-left: 5px solid #4F8BF9; background: #0f172a; color: #F8FAFC; border-radius: 10px; margin-bottom: 1rem; overflow-wrap: anywhere;">
            <h3 style="margin: 0 0 0.35rem 0;">QUESTION {st.session_state.current_question_number} OF 5</h3>
            <p style="margin: 0 0 0.75rem 0;"><strong>{html.escape(st.session_state.current_question_type.upper())}</strong> • <strong>{html.escape(st.session_state.get('current_question_mode', 'new_topic').upper())}</strong></p>
            <p style="margin: 0; font-size: 1.05rem; line-height: 1.55; white-space: normal;">{html.escape(st.session_state.current_question)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("evaluation_pending_advance"):
        evaluation = st.session_state.last_evaluation
        _render_evaluation_result(evaluation)
        button_label = "View Final Report" if st.session_state.current_question_number >= 5 else f"Continue to Question {st.session_state.current_question_number + 1}"
        if st.button(button_label, type="primary", use_container_width=True, key="continue_after_evaluation"):
            _continue_after_evaluation(vectorstore, job_description)
        return

    if interview_mode == "Voice Interview":
        _render_voice_question(vectorstore, job_description)
        return

    with st.form(key=f"answer_form_{st.session_state.current_question_number}"):
        answer = st.text_area(
            "✍ Your Answer",
            value=st.session_state.get(f"answer_{st.session_state.current_question_number}", ""),
            height=220,
            placeholder="Explain your answer here...",
        )
        submitted = st.form_submit_button("Submit Answer", use_container_width=True)

    if submitted:
        if not answer.strip():
            st.warning("Please provide an answer before submitting.")
            st.stop()

        st.session_state[f"answer_{st.session_state.current_question_number}"] = answer
        evaluation = pipeline.evaluate_answer(
            question=st.session_state.current_question,
            candidate_answer=answer,
            category=st.session_state.current_question_type,
        )
        if evaluation.get("evaluation_failed") and evaluation.get("score") is None:
            _render_evaluation_failure(evaluation)
            st.stop()

        entry = {
            "question_number": st.session_state.current_question_number,
            "category": st.session_state.current_question_type,
            "question": st.session_state.current_question,
            "answer": answer,
            "score": evaluation.get("score"),
            "correctness": evaluation.get("correctness"),
            "relevance": evaluation.get("relevance"),
            "technical_depth": evaluation.get("technical_depth"),
            "completeness": evaluation.get("completeness"),
            "feedback": evaluation["feedback"],
            "strengths": evaluation.get("strengths", []),
            "weaknesses": evaluation.get("weaknesses", []),
            "missing_points": evaluation.get("missing_points", []),
            "recommended_action": evaluation.get("recommended_action", "follow_up"),
            "recommended_topic": evaluation.get("recommended_topic", "General technical discussion"),
        }
        st.session_state.question_history.append(entry)
        st.session_state.scores.append(float(entry["score"]))
        st.session_state.last_evaluation = evaluation
        st.session_state.evaluation_pending_advance = True
        st.rerun()

    if st.button("🏁 Finish Interview", use_container_width=True):
        st.session_state.page = "Report"
        st.rerun()