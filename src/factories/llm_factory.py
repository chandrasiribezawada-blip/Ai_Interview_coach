from langchain_groq import ChatGroq
from src.config.settings import Settings


class LLMFactory:
    """
    Factory for creating LLM instances.
    """

    @staticmethod
    def create_llm():

        return ChatGroq(
            api_key=Settings.GROQ_API_KEY,
            model=Settings.MODEL_NAME,
            temperature=Settings.TEMPERATURE,
            max_tokens=Settings.MAX_TOKENS
        )