import streamlit as st

# Import UI Pages
from ui.home import show_home
from ui.interview import show_interview
from ui.report import show_report

# -------------------------------
# Page Configuration
# -------------------------------

st.set_page_config(
    page_title="AI Interview Coach",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------
# Session State
# -------------------------------

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "resume_uploaded" not in st.session_state:
    st.session_state.resume_uploaded = False

if "jd_uploaded" not in st.session_state:
    st.session_state.jd_uploaded = False

if "question_number" not in st.session_state:
    st.session_state.question_number = 1

if "score" not in st.session_state:
    st.session_state.score = 0

# -------------------------------
# Sidebar
# -------------------------------

with st.sidebar:

    st.title("🤖 AI Interview Coach")

    st.markdown("---")

    st.subheader("Navigation")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.page = "Home"

    if st.button("🎤 Interview", use_container_width=True):
        st.session_state.page = "Interview"

    if st.button("📊 Report", use_container_width=True):
        st.session_state.page = "Report"

    st.markdown("---")

    st.subheader("Current Session")

    if st.session_state.resume_uploaded:
        st.success("📄 Resume Uploaded")
    else:
        st.warning("📄 Resume Missing")

    if st.session_state.jd_uploaded:
        st.success("💼 Job Description Uploaded")
    else:
        st.warning("💼 JD Missing")

    st.markdown("---")

    st.subheader("Interview Progress")

    progress = st.session_state.question_number / 5

    if progress > 1:
        progress = 1

    st.progress(progress)

    st.write(
        f"Question {st.session_state.question_number} / 5"
    )

# -------------------------------
# Routing
# -------------------------------

if st.session_state.page == "Home":
    show_home()

elif st.session_state.page == "Interview":
    show_interview()

elif st.session_state.page == "Report":
    show_report()