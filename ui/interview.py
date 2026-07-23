import streamlit as st
from src.interview.pipeline import InterviewPipeline


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

    if "vectorstore" not in st.session_state:

        with st.spinner("📄 Processing Resume..."):

            vectorstore = pipeline.build_resume_vectorstore(
                "data/resume/resume.pdf"
            )

        st.session_state.vectorstore = vectorstore

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

    # ---------------------------------------
    # Generate Question
    # ---------------------------------------

    if "question" not in st.session_state:

        topic = topics[0]

        with st.spinner("🤖 Generating Interview Question..."):

            question = pipeline.generate_first_question(
                vectorstore,
                job_description,
                topic
            )

        st.session_state.question = question

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