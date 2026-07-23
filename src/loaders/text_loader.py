from langchain_core.documents import Document


class TextLoader:

    def __init__(self, file_path):
        self.file_path = file_path

    def load(self):
        with open(self.file_path, "r", encoding="utf-8") as file:
            text = file.read()

        return [Document(page_content=text)]