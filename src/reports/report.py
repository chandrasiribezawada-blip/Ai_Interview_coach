class ReportGenerator:

    def generate(self, session):

        report = "\n"
        report += "=" * 60
        report += "\nFINAL INTERVIEW REPORT\n"
        report += "=" * 60

        report += f"\n\nQuestions Attempted : {len(session.questions)}"

        report += f"\nAverage Score      : {session.average_score()}/10"

        report += "\n\nDetailed Feedback"

        report += "\n" + "-" * 60

        for i in range(len(session.questions)):

            report += f"\n\nQuestion {i+1}\n"

            report += "-" * 30

            report += "\n"

            report += session.questions[i]

            report += "\n\n"

            report += session.feedback[i]

        return report