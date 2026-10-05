from langchain_groq import ChatGroq
from src.config.settings import Settings


class LLMFactory:
    """
    Factory for creating LLM instances.
    """

    @staticmethod
    def create_llm(max_tokens=None):

        return ChatGroq(
            api_key=Settings.GROQ_API_KEY,
            model=Settings.MODEL_NAME,
            temperature=Settings.TEMPERATURE,
            max_tokens=max_tokens if max_tokens is not None else Settings.MAX_TOKENS
        )