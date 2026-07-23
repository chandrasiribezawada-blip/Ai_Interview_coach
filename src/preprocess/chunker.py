from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:

    def __init__(self, chunk_size=500, chunk_overlap=100):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )

    def split(self, documents):
        return self.splitter.split_documents(documents)