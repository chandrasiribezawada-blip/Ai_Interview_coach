class InterviewSession:

    def __init__(self):
        self.questions = []
        self.answers = []
        self.feedback = []
        self.scores = []

    def add_round(self, question, answer, feedback, score=None):
        self.questions.append(question)
        self.answers.append(answer)
        self.feedback.append(feedback)

        normalized_score = score
        if normalized_score is None:
            normalized_score = self.extract_score(feedback)
        self.scores.append(float(normalized_score))

    def extract_score(self, feedback):
        if not feedback:
            return 0.0
        try:
            if isinstance(feedback, dict):
                score = feedback.get("score", 0)
            else:
                score = feedback
                if hasattr(feedback, "get"):
                    score = feedback.get("score", 0)
                else:
                    lines = str(score).splitlines()
                    first_line = lines[0] if lines else ""
                    score = first_line.replace("Score:", "").replace("/10", "").strip()
            return float(score)
        except (TypeError, ValueError):
            return 0.0

    def average_score(self):
        if len(self.scores) == 0:
            return 0
        return round(sum(self.scores) / len(self.scores), 2)