import streamlit as st
from streamlit_option_menu import option_menu


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="InterviewMentor AI",
    page_icon="🎯",
    layout="wide"
)


# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.main {
    background-color:#f8f9fc;
}

.title {
    font-size:42px;
    font-weight:800;
    color:#1f4e79;
}

.subtitle {
    font-size:20px;
    color:#555;
}


.card {
    padding:20px;
    border-radius:15px;
    background:white;
    box-shadow:0px 4px 15px rgba(0,0,0,0.1);
    text-align:center;
}


.big-button {
    background:#1f77ff;
    color:white;
    padding:12px;
    border-radius:10px;
    text-align:center;
    font-size:18px;
}


</style>
""", unsafe_allow_html=True)



# ---------------- SIDEBAR ----------------


with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/4712/4712109.png",
        width=100
    )

    st.title("InterviewMentor AI")

    menu = option_menu(
        None,
        [
            "Dashboard",
            "Company Prep",
            "AI Tutor",
            "Mock Interview",
            "Performance"
        ],

        icons=[
            "house",
            "building",
            "book",
            "mic",
            "graph-up"
        ],

        default_index=0
    )


# ---------------- DASHBOARD ----------------


if menu=="Dashboard":

    st.markdown(
        "<div class='title'>🎯 InterviewMentor AI</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class='subtitle'>
        Your Personalized AI Placement Preparation Coach
        </div>
        """,
        unsafe_allow_html=True
    )


    st.write("")


    col1,col2,col3 = st.columns(3)


    with col1:

        st.markdown(
        """
        <div class="card">

        📄

        <h3>Resume Analysis</h3>

        AI understands your resume
        and generates interview questions.

        </div>
        """,
        unsafe_allow_html=True
        )


    with col2:

        st.markdown(
        """
        <div class="card">

        📚

        <h3>RAG Tutor</h3>

        Upload notes and ask doubts.

        </div>
        """,
        unsafe_allow_html=True
        )


    with col3:

        st.markdown(
        """
        <div class="card">

        🎤

        <h3>Mock Interview</h3>

        Practice real company interviews.

        </div>
        """,
        unsafe_allow_html=True
        )



    st.divider()


    st.subheader("🚀 Preparation Overview")


    c1,c2,c3,c4 = st.columns(4)


    c1.metric(
        "Documents",
        "5"
    )


    c2.metric(
        "Questions Practiced",
        "120"
    )


    c3.metric(
        "Interview Score",
        "82%"
    )


    c4.metric(
        "Company",
        "Goldman Sachs"
    )




# ---------------- COMPANY PREP ----------------


elif menu=="Company Prep":


    st.title("🏢 Company Preparation")


    company = st.selectbox(
        "Select Target Company",
        [
            "Goldman Sachs",
            "Amazon",
            "Microsoft",
            "Google",
            "TCS"
        ]
    )


    st.success(
        f"Generating preparation roadmap for {company}"
    )


    st.subheader("Important Topics")


    topics=[
        "Arrays & Hashing",
        "Graphs",
        "Dynamic Programming",
        "OOPS",
        "DBMS",
        "Operating Systems"
    ]


    for t in topics:

        st.write(
            "✅",
            t
        )



    st.subheader("30 Day Plan")


    st.progress(0.65)

    st.info(
    """
    Week 1:
    DSA Basics
    
    Week 2:
    Advanced Data Structures
    
    Week 3:
    Core CS Subjects
    
    Week 4:
    Mock Interviews
    """
    )





# ---------------- AI TUTOR ----------------


elif menu=="AI Tutor":

    st.title("📚 AI Tutor")


    uploaded = st.file_uploader(
        "Upload preparation material",
        type=["pdf"]
    )


    if uploaded:

        st.success(
            "Document uploaded successfully"
        )


    question = st.chat_input(
        "Ask your doubt..."
    )


    if question:

        with st.chat_message("user"):
            st.write(question)


        with st.chat_message("assistant"):
            st.write(
                """
                AI Explanation:

                This answer will come from your
                RAG pipeline.
                """
            )





# ---------------- MOCK INTERVIEW ----------------


elif menu=="Mock Interview":


    st.title("🎤 AI Mock Interview")


    round_type = st.selectbox(
        "Choose Round",
        [
            "HR Round",
            "Technical Round",
            "System Design",
            "Behavioral"
        ]
    )


    st.info(
        f"{round_type} Started"
    )


    st.subheader(
        "Question 1"
    )


    st.write(
        """
        Explain your project architecture.
        """
    )


    answer = st.text_area(
        "Your Answer"
    )


    if st.button("Evaluate"):

        st.success(
            """
            Score: 8/10

            Good explanation.

            Improve:
            Mention scalability and security.
            """
        )




# ---------------- PERFORMANCE ----------------


else:


    st.title("📊 Performance Report")


    st.metric(
        "Overall Score",
        "85%"
    )


    st.progress(0.85)


    st.write(
    """
    Strengths:

    ✅ DSA knowledge
    ✅ Project explanation


    Improve:

    ⚡ System Design
    ⚡ Communication
    """
    )