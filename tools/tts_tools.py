import pyttsx3
from typing import Optional, Dict, Any
from langchain.tools import tool


def _get_engine() -> pyttsx3.Engine:
    engine = pyttsx3.init()
    return engine


@tool
def list_tts_voices() -> str:
    """
    List available TTS voices (id, name, language).
    """
    try:
        engine = _get_engine()
        voices = engine.getProperty("voices")
        lines = []
        for v in voices:
            # Some drivers expose 'languages' attr; fallback gracefully
            lang = None
            try:
                lang = getattr(v, "languages", None)
            except Exception:
                lang = None
            lines.append(f"id={v.id} | name={v.name} | lang={lang}")
        if not lines:
            return "No TTS voices available."
        return "Available TTS voices:\n" + "\n".join(lines)
    except Exception as e:
        return f"Error listing TTS voices: {str(e)}"


@tool
def speak_text(text: str, voice_id: Optional[str] = None, rate: Optional[int] = None, volume: Optional[float] = None) -> str:
    """
    Speak the provided text using system TTS.
    Args:
        text: Content to speak
        voice_id: Optional voice identifier from list_tts_voices
        rate: Words per minute (e.g., 150-200). Defaults to engine default
        volume: 0.0 - 1.0. Defaults to engine default
    """
    try:
        if not text or not text.strip():
            return "Error: No text provided to speak."

        engine = _get_engine()

        if voice_id:
            try:
                engine.setProperty("voice", voice_id)
            except Exception:
                pass

        if rate is not None:
            try:
                engine.setProperty("rate", int(rate))
            except Exception:
                pass

        if volume is not None:
            try:
                # clamp between 0.0 and 1.0
                v = max(0.0, min(1.0, float(volume)))
                engine.setProperty("volume", v)
            except Exception:
                pass

        engine.say(text)
        engine.runAndWait()
        return "Spoken successfully."
    except Exception as e:
        return f"Error speaking text: {str(e)}"



