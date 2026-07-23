class InterviewSession:

    def __init__(self):
        self.questions = []
        self.answers = []
        self.feedback = []
        self.scores = []

    def add_round(self, question, answer, feedback):

        self.questions.append(question)
        self.answers.append(answer)
        self.feedback.append(feedback)

        score = self.extract_score(feedback)
        self.scores.append(score)

    def extract_score(self, feedback):

        try:
            first_line = feedback.split("\n")[0]

            score = first_line.replace("Score:", "").replace("/10", "").strip()

            return float(score)

        except:
            return 0

    def average_score(self):

        if len(self.scores) == 0:
            return 0

        return round(sum(self.scores) / len(self.scores), 2)