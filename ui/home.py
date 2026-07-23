import streamlit as st
import os


def show_home():

    # -------------------------------
    # Header
    # -------------------------------

    st.title("🤖 AI Interview Coach")

    st.markdown(
        """
### Personalized AI Interview Preparation Platform

Prepare for technical interviews using Artificial Intelligence.

The system analyzes your **Resume** and **Job Description**, generates
personalized interview questions, evaluates your answers,
and provides detailed feedback with a final interview report.
"""
    )

    st.divider()

    # -------------------------------
    # Features
    # -------------------------------

    st.subheader("✨ What can this application do?")

    col1, col2 = st.columns(2)

    with col1:

        st.success("📄 Analyze Resume")

        st.success("💼 Analyze Job Description")

        st.success("🎤 Conduct AI Mock Interview")

    with col2:

        st.success("🧠 Personalized Questions")

        st.success("⭐ AI Answer Evaluation")

        st.success("📊 Final Performance Report")

    st.divider()

    # -------------------------------
    # Workflow
    # -------------------------------

    st.subheader("🚀 Workflow")

    st.info("""
1️⃣ Upload Resume

2️⃣ Upload Job Description

3️⃣ Resume Processing

4️⃣ AI Generates Questions

5️⃣ Answer Questions

6️⃣ AI Evaluates Answers

7️⃣ View Final Report
""")

    st.divider()

    # -------------------------------
    # Upload Files
    # -------------------------------

    st.subheader("📂 Upload Documents")

    col1, col2 = st.columns(2)

    # Resume Upload
    with col1:

        resume = st.file_uploader(
            "Upload Resume (PDF)",
            type=["pdf"]
        )

        if resume:

            os.makedirs("data/resume", exist_ok=True)

            with open(
                "data/resume/resume.pdf",
                "wb"
            ) as f:

                f.write(resume.getbuffer())

            st.session_state.resume_uploaded = True

            st.success("✅ Resume Uploaded")

            st.caption(resume.name)

    # JD Upload
    with col2:

        jd = st.file_uploader(
            "Upload Job Description (TXT)",
            type=["txt"]
        )

        if jd:

            os.makedirs("data/jd", exist_ok=True)

            with open(
                "data/jd/job_description.txt",
                "wb"
            ) as f:

                f.write(jd.getbuffer())

            st.session_state.jd_uploaded = True

            st.success("✅ Job Description Uploaded")

            st.caption(jd.name)

    st.divider()

    # -------------------------------
    # Technology Stack
    # -------------------------------

    st.subheader("⚙ AI Technologies Used")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("LLM", "Groq")

    with c2:
        st.metric("Framework", "LangChain")

    with c3:
        st.metric("Vector DB", "FAISS")

    with c4:
        st.metric("Technique", "RAG")

    st.divider()

    # -------------------------------
    # Start Interview
    # -------------------------------

    if st.button(
        "🚀 Start Interview",
        use_container_width=True
    ):

        if not st.session_state.resume_uploaded:

            st.error("Please upload your Resume.")

        elif not st.session_state.jd_uploaded:

            st.error("Please upload the Job Description.")

        else:

            st.session_state.page = "Interview"

            st.rerun()