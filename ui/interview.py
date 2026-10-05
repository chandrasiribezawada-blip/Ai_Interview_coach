import hashlib

import streamlit as st
from src.interview.pipeline import InterviewPipeline
from src.interview.voice import analyze_speech, audio_seconds, text_to_speech, transcribe


def show_interview():

    st.title("🎤 AI Mock Interview")

    st.markdown(
        "Answer the AI-generated interview questions based on your Resume and Job Description."
    )

    st.divider()

    # ---------------------------------------
    # Create Pipeline
    # ---------------------------------------

    if "pipeline" not in st.session_state:

        st.session_state.pipeline = InterviewPipeline()

    pipeline = st.session_state.pipeline

    # ---------------------------------------
    # Build Vector Database
    # ---------------------------------------

    source_digest = hashlib.sha256()
    for source_path in ("data/resume/resume.pdf", "data/jd/job_description.txt"):
        try:
            with open(source_path, "rb") as source_file:
                source_digest.update(source_file.read())
        except OSError as error:
            st.error(f"Could not read uploaded interview documents: {error}")
            st.stop()
    source_fingerprint = source_digest.hexdigest()

    if (
        "vectorstore" not in st.session_state
        or st.session_state.get("vectorstore_source_fingerprint") != source_fingerprint
    ):
        try:
            with st.spinner("📄 Processing Resume and Job Description..."):
                vectorstore = pipeline.build_resume_vectorstore(
                    "data/resume/resume.pdf"
                )
            st.session_state.vectorstore = vectorstore
            st.session_state.vectorstore_source_fingerprint = source_fingerprint
        except Exception as error:
            st.error(f"Could not build the resume/JD FAISS index: {error}")
            st.stop()

    vectorstore = st.session_state.vectorstore

    # ---------------------------------------
    # Read Job Description
    # ---------------------------------------

    with open(
        "data/jd/job_description.txt",
        "r",
        encoding="utf-8"
    ) as file:

        job_description = file.read()

    # ---------------------------------------
    # Topics
    # ---------------------------------------

    topics = [
        "Projects",
        "Technical Skills",
        "Achievements",
        "Leadership",
        "Problem Solving"
    ]

    mode_locked = bool(st.session_state.get("voice_history")) or bool(pipeline.session.questions)
    interview_mode = st.radio(
        "Interview mode",
        ["Text Interview", "Voice Interview"],
        horizontal=True,
        key="interview_mode",
        disabled=mode_locked,
    )

    # ---------------------------------------
    # Generate Question
    # ---------------------------------------

    if "question" not in st.session_state:

        topic = topics[0]

        try:
            with st.spinner("🤖 Generating Interview Question..."):
                question = pipeline.generate_first_question(
                    vectorstore,
                    job_description,
                    topic
                )
            st.session_state.question = question
        except Exception as error:
            st.error(f"Could not generate the interview question: {error}")
            st.stop()

    if interview_mode == "Voice Interview":
        question_number = st.session_state.question_number
        voice_history = st.session_state.setdefault("voice_history", [])
        st.session_state.voice_interview_topics = topics
        st.progress(len(voice_history) / len(topics), text=f"Question {question_number} of {len(topics)}")
        st.subheader(f"Question {question_number} / {len(topics)}")
        st.info(st.session_state.question)

        speech_text = st.session_state.get("voice_say_text", st.session_state.question)
        if not speech_text.endswith(st.session_state.question):
            speech_text = st.session_state.question
        question_key = hashlib.sha256(
            f"{question_number}:{speech_text}".encode("utf-8")
        ).hexdigest()[:16]
        tts_cache = st.session_state.setdefault("voice_tts_cache", {})
        tts_errors = st.session_state.setdefault("voice_tts_errors", {})
        if question_key not in tts_cache and question_key not in tts_errors:
            try:
                tts_cache[question_key] = text_to_speech(speech_text)
            except Exception as error:
                tts_errors[question_key] = str(error)

        if question_key in tts_errors:
            st.warning(f"Could not generate speech: {tts_errors[question_key]}")
            if st.button("Retry speech", key=f"retry_tts_{question_key}"):
                del tts_errors[question_key]
                st.rerun()
        elif question_key in tts_cache:
            if st.session_state.get("voice_spoken_question") != question_key:
                st.audio(tts_cache[question_key], format="audio/mp3", autoplay=True)
                st.session_state.voice_spoken_question = question_key
            if st.button("🔁 Replay question", key=f"replay_{question_key}"):
                st.audio(tts_cache[question_key], format="audio/mp3", autoplay=True)

        audio = st.audio_input("Record your answer", key=f"voice_recording_{question_number}")
        if audio is not None:
            audio_bytes = audio.getvalue()
            recording_key = hashlib.sha256(audio_bytes).hexdigest()
            transcript_cache = st.session_state.setdefault("voice_transcript_cache", {})
            transcription_errors = st.session_state.setdefault("voice_transcription_errors", {})
            if recording_key not in transcript_cache and recording_key not in transcription_errors:
                try:
                    with st.spinner("Transcribing your answer..."):
                        transcript_cache[recording_key] = transcribe(audio_bytes)
                except Exception as error:
                    transcript_cache[recording_key] = ""
                    transcription_errors[recording_key] = str(error)

            if recording_key in transcription_errors:
                st.warning(f"Whisper transcription failed. You can enter the answer manually. {transcription_errors[recording_key]}")
            elif not transcript_cache[recording_key]:
                st.info("No speech was detected. Enter your answer in the transcript field.")

            transcript = st.text_area(
                "Transcript (edit if needed)",
                value=transcript_cache[recording_key],
                key=f"voice_transcript_{recording_key}",
            )

            if st.button("Submit voice answer", type="primary", key=f"submit_voice_{recording_key}"):
                if not transcript.strip():
                    st.warning("Please record an answer or enter a transcript before submitting.")
                    st.stop()

                try:
                    duration = audio_seconds(audio_bytes)
                except Exception as error:
                    st.warning(f"Could not read recording duration ({error}); fluency metrics will use 0 seconds.")
                    duration = 0.0

                metrics = analyze_speech(transcript, duration)
                try:
                    with st.spinner("Evaluating your answer and retrieving relevant context..."):
                        evaluation = pipeline.evaluate_voice_answer(
                            st.session_state.question,
                            transcript,
                            vectorstore,
                        )
                except Exception as error:
                    st.error(f"Answer evaluation or FAISS retrieval failed: {error}")
                    st.stop()

                entry = {
                    "question": st.session_state.question,
                    "answer": transcript,
                    **metrics,
                    **evaluation,
                }
                retrieved_context = entry.pop("_retrieved_context", "")
                st.session_state.voice_history = voice_history + [entry]

                if question_number >= len(topics):
                    st.session_state.voice_report = None
                    st.session_state.page = "Report"
                    st.rerun()

                next_question_number = question_number + 1
                next_topic = topics[next_question_number - 1]
                next_question = ""
                try:
                    with st.spinner("Preparing the next interview question..."):
                        result = pipeline.generate_voice_follow_up(
                            next_topic,
                            st.session_state.question,
                            transcript,
                            st.session_state.voice_history,
                            vectorstore,
                            retrieved_context=retrieved_context,
                        )
                    next_question = result["next_question"].strip()
                    if not next_question:
                        raise ValueError("The model returned an empty follow-up question.")
                    st.session_state.voice_say_text = (
                        f"{result['acknowledgement']} {next_question}".strip()
                    )
                except Exception as error:
                    st.warning(f"Could not generate a personalized follow-up ({error}). Using the existing RAG question generator instead.")
                    try:
                        st.session_state.voice_say_text = pipeline.generate_first_question(
                            vectorstore,
                            job_description,
                            next_topic,
                        )
                    except Exception as fallback_error:
                        st.error(f"Could not generate the next question: {fallback_error}")
                        st.stop()
                st.session_state.question_number = next_question_number
                st.session_state.question = next_question or st.session_state.voice_say_text
                st.rerun()

        if st.button("🏁 Finish Interview", key="finish_voice_interview"):
            if voice_history:
                st.session_state.voice_report = None
                st.session_state.page = "Report"
                st.rerun()
            st.warning("Answer at least one question before viewing a report.")
        st.stop()

    # ---------------------------------------
    # Question Card
    # ---------------------------------------

    st.subheader(
        f"Question {st.session_state.question_number} / {len(topics)}"
    )

    st.info(st.session_state.question)

    # ---------------------------------------
    # Answer
    # ---------------------------------------

    answer = st.text_area(
        "✍ Your Answer",
        height=220,
        placeholder="Explain your answer here..."
    )

    # ---------------------------------------
    # Submit
    # ---------------------------------------

    if st.button(
        "Submit Answer",
        use_container_width=True
    ):

        if answer.strip() == "":

            st.warning("Please enter your answer.")

            st.stop()

        with st.spinner("🧠 Evaluating Answer..."):

            feedback = pipeline.evaluate_answer(
                st.session_state.question,
                answer
            )

        pipeline.save_round(
            st.session_state.question,
            answer,
            feedback
        )

        st.session_state.feedback = feedback

    # ---------------------------------------
    # Feedback
    # ---------------------------------------

    if "feedback" in st.session_state:

        st.divider()

        st.subheader("🤖 AI Feedback")

        st.success(st.session_state.feedback)

        st.divider()

        col1, col2 = st.columns(2)

        # -------------------------------
        # Next Question
        # -------------------------------

        with col1:

            if st.button(
                "➡ Next Question",
                use_container_width=True
            ):

                if st.session_state.question_number < len(topics):

                    st.session_state.question_number += 1

                    topic = topics[
                        st.session_state.question_number - 1
                    ]

                    with st.spinner(
                        "Generating Next Question..."
                    ):

                        question = pipeline.generate_first_question(
                            vectorstore,
                            job_description,
                            topic
                        )

                    st.session_state.question = question

                    del st.session_state.feedback

                    st.rerun()

                else:

                    st.success("Interview Completed!")

                    st.session_state.page = "Report"

                    st.rerun()

        # -------------------------------
        # Finish Interview
        # -------------------------------

        with col2:

            if st.button(
                "🏁 Finish Interview",
                use_container_width=True
            ):

                st.session_state.page = "Report"

                st.rerun()