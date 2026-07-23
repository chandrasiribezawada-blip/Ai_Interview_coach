class ContextRefiner:
    """
    Removes unnecessary information
    before sending context to the LLM.
    """

    def refine(self, documents):

        refined_context = []

        for doc in documents:

            lines = doc.page_content.split("\n")

            cleaned_lines = []

            for line in lines:

                line = line.strip()

                if len(line) > 5:
                    cleaned_lines.append(line)

            refined_context.append(
                "\n".join(cleaned_lines)
            )

        return "\n\n".join(refined_context)