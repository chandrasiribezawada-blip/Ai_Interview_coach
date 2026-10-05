import asyncio
import io
import os
import re
import wave

import edge_tts
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

STT_MODEL = "whisper-large-v3-turbo"
TTS_VOICE = "en-IN-NeerjaNeural"
FILLER_PATTERN = re.compile(
    r"\b(um+|uh+|er+|erm|like|basically|actually|literally|you know|kind of|sort of)\b",
    re.IGNORECASE,
)

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing from the environment or .env file.")
        _client = Groq(api_key=api_key)
    return _client


def transcribe(audio_bytes: bytes) -> str:
    result = _get_client().audio.transcriptions.create(
        file=("answer.wav", audio_bytes),
        model=STT_MODEL,
        language="en",
    )
    return result.text.strip()


async def _tts_async(text: str, voice: str) -> bytes:
    audio_chunks = []
    async for chunk in edge_tts.Communicate(text, voice).stream():
        if chunk["type"] == "audio":
            audio_chunks.append(chunk["data"])
    return b"".join(audio_chunks)


def text_to_speech(text: str, voice: str = TTS_VOICE) -> bytes:
    return asyncio.run(_tts_async(text, voice))


def audio_seconds(audio_bytes: bytes) -> float:
    with wave.open(io.BytesIO(audio_bytes)) as recording:
        return recording.getnframes() / float(recording.getframerate())


def analyze_speech(transcript: str, seconds: float) -> dict:
    words = transcript.split()
    fillers = FILLER_PATTERN.findall(transcript)
    word_count = len(words)
    return {
        "duration_sec": round(seconds, 1),
        "word_count": word_count,
        "wpm": round(word_count / (seconds / 60)) if seconds > 0 else 0,
        "filler_count": len(fillers),
        "filler_words": sorted({filler.lower() for filler in fillers}),
        "filler_rate_pct": round(100 * len(fillers) / word_count, 1) if word_count else 0.0,
    }