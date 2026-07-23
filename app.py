from src.interview.pipeline import InterviewPipeline


def main():

    pipeline = InterviewPipeline()

    # Build Resume Vector Database
    vectorstore = pipeline.build_resume_vectorstore(
        "data/resume/resume.pdf"
    )

    # Temporary Job Description
    job_description = """
Looking for a Python Developer with experience in
Python, Django, LangChain, LangGraph,
Retrieval-Augmented Generation (RAG),
Large Language Models (LLMs),
REST APIs and AI application development.
"""

    # Interview Topics
    topics = [
        "Projects",
        "Technical Skills",
        "Achievements"
    ]

    print("\n" + "=" * 70)
    print("          🤖 WELCOME TO AI INTERVIEW COACH")
    print("=" * 70)
    print("✅ Resume Loaded")
    print("✅ Vector Database Created")
    print("✅ AI Interview Ready")
    print(f"📋 Total Interview Rounds : {len(topics)}")
    print("=" * 70)

    # Interview Loop
    for round_no, topic in enumerate(topics, start=1):

        print("\n")
        print("=" * 70)
        print(f"ROUND {round_no}/{len(topics)}")
        print(f"TOPIC : {topic}")
        print("=" * 70)

        question = pipeline.generate_first_question(
            vectorstore,
            job_description,
            topic
        )

        print("\n🧠 Interview Question\n")
        print(question)

        answer = input("\n👤 Your Answer:\n> ")

        feedback = pipeline.evaluate_answer(
            question,
            answer
        )

        pipeline.save_round(
            question,
            answer,
            feedback
        )

        print("\n")
        print("=" * 70)
        print("📊 AI FEEDBACK")
        print("=" * 70)
        print(feedback)

    # Final Report
    print("\n")
    print("=" * 70)
    print("🎯 FINAL INTERVIEW REPORT")
    print("=" * 70)

    report = pipeline.generate_report()

    print(report)

    print("\n")
    print("=" * 70)
    print("✅ Interview Completed Successfully")
    print("Thank you for using AI Interview Coach.")
    print("=" * 70)


if __name__ == "__main__":
    main()