import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.loaders.pdf_loader import PDFLoader
from src.preprocess.cleaner import TextCleaner
from src.preprocess.chunker import TextChunker
from src.preprocess.metadata import MetadataGenerator

loader = PDFLoader("data/resume/resume.pdf")

documents = loader.load()

assert len(documents) > 0

documents = TextCleaner.clean(documents)

chunker = TextChunker()

chunks = chunker.split(documents)

chunks = MetadataGenerator.enhance(chunks, "resume")

assert len(chunks) > 0

for chunk in chunks:
    assert "chunk_id" in chunk.metadata
    assert "document_type" in chunk.metadata

print("✅ Phase 1 Test Passed")