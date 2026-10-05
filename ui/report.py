import streamlit as st
import pandas as pd


def show_report():

    st.title("📊 AI Interview Report")

    if (
        st.session_state.get("interview_mode") == "Voice Interview"
        and st.session_state.get("voice_history")
    ):
        pipeline = st.session_state.get("pipeline")
        if pipeline is None:
            st.error("Interview pipeline state is missing. Return to the interview and try again.")
            return

        if st.session_state.get("voice_report") is None:
            try:
                with st.spinner("Generating your voice-interview report..."):
                    st.session_state.voice_report = pipeline.generate_voice_report(
                        " / ".join(st.session_state.get("voice_interview_topics", []))
                        or "Multi-round interview",
                        st.session_state.voice_history,
                    )
            except Exception as error:
                st.error(f"Could not generate the final report: {error}")
                if st.button("Retry report generation"):
                    st.rerun()
                return

        report = st.session_state.voice_report
        history = st.session_state.voice_history
        col1, col2, col3 = st.columns(3)
        col1.metric("Overall", f"{report['overall_score']}/100")
        col2.metric("Content", f"{report['content_score']}/100")
        col3.metric("Communication", f"{report['communication_score']}/100")

        st.subheader("Summary")
        st.write(report["summary"])
        left, right = st.columns(2)
        with left:
            st.subheader("Strengths")
            for strength in report["strengths"]:
                st.write(f"- {strength}")
        with right:
            st.subheader("Weaknesses")
            for weakness in report["weaknesses"]:
                st.write(f"- {weakness}")

        st.subheader("Missing points")
        for missing_point in report["missing_points"]:
            st.write(f"- {missing_point}")
        st.subheader("Fluency feedback")
        st.write(report["fluency_feedback"])

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Average WPM", report["average_wpm"])
        metric2.metric("Total filler words", report["total_filler_words"])
        metric3.metric("Average answer duration", f"{report['average_duration_sec']} sec")

        st.subheader("Per-question breakdown")
        st.dataframe(
            pd.DataFrame(history)[
                ["question", "answer", "score", "feedback", "wpm", "filler_count", "filler_rate_pct"]
            ],
            use_container_width=True,
        )

        if st.button("Start New Interview", use_container_width=True):
            _reset_interview_state()
            st.session_state.page = "Home"
            st.rerun()
        return

    st.markdown(
        """
Thank you for completing the AI Interview.

Below is your interview performance summary.
"""
    )

    st.divider()

    pipeline = st.session_state.get("pipeline", None)

    if pipeline is None:

        st.warning("No interview data found.")

        return

    report = pipeline.generate_report()

    # -------------------------
    # Metrics
    # -------------------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Questions Attempted",
            st.session_state.question_number
        )

    with col2:
        st.metric(
            "Interview Status",
            "Completed"
        )

    with col3:
        st.metric(
            "AI Evaluation",
            "Available"
        )

    st.divider()

    st.subheader("📝 Complete Interview Report")

    st.success(report)

    st.divider()


    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "🏠 Back to Home",
            use_container_width=True
        ):

            st.session_state.page = "Home"

            st.rerun()

    with c2:

        if st.button(
            "🔄 Start New Interview",
            use_container_width=True
        ):

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