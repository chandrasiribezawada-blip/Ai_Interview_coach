class MetadataGenerator:

    @staticmethod
    def enhance(chunks, document_type):
        total_chunks = len(chunks)

        for index, chunk in enumerate(chunks):

            chunk.metadata["document_type"] = document_type
            chunk.metadata["chunk_id"] = index + 1
            chunk.metadata["total_chunks"] = total_chunks
            chunk.metadata["chunk_size"] = len(chunk.page_content)

        return chunks