import re


class TextCleaner:

    @staticmethod
    def clean(documents):
        cleaned_documents = []

        for doc in documents:
            text = doc.page_content

            # Replace tabs with spaces
            text = text.replace("\t", " ")

            # Remove multiple spaces
            text = re.sub(r" +", " ", text)

            # Remove multiple blank lines
            text = re.sub(r"\n\s*\n", "\n\n", text)

            # Strip leading/trailing whitespace
            text = text.strip()

            # Update document content
            doc.page_content = text
            cleaned_documents.append(doc)

        return cleaned_documents