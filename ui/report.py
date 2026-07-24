import streamlit as st


def show_report():

    st.title("📊 AI Interview Report")

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

            # Reset Session

            for key in [
                "pipeline",
                "vectorstore",
                "question",
                "feedback",
                "question_number"
            ]:

                if key in st.session_state:

                    del st.session_state[key]

            for key in list(st.session_state.keys()):

                if key.startswith("answer_"):

                    del st.session_state[key]

            st.session_state.question_number = 1

            st.session_state.page = "Home"

            st.rerun()