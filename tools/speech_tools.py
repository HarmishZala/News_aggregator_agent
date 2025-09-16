import os
import tempfile
from typing import Optional, Dict, Any
from langchain.tools import tool
import speech_recognition as sr
from pydub import AudioSegment
import io
import base64
from utils.config_loader import load_config

class SpeechToTextProcessor:
    """Handles speech-to-text conversion with multiple recognition engines"""
    
    def __init__(self):
        self.config = load_config()
        self.speech_config = self.config.get('speech_recognition', {})
        
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = self.speech_config.get('energy_threshold', 300)
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = self.speech_config.get('pause_threshold', 0.8)
        self.recognizer.operation_timeout = None
        self.recognizer.phrase_threshold = self.speech_config.get('phrase_threshold', 0.3)
        self.recognizer.non_speaking_duration = self.speech_config.get('non_speaking_duration', 0.8)
        
        self.default_language = self.speech_config.get('default_language', 'en-US')
        self.supported_languages = self.speech_config.get('supported_languages', ['en-US'])
        
    def convert_audio_to_wav(self, audio_data: bytes, input_format: str = "mp3") -> bytes:
        """Convert audio data to WAV format for better recognition"""
        try:
            # Load audio from bytes
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format=input_format)
            
            # Convert to WAV format
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            wav_data = wav_buffer.getvalue()
            wav_buffer.close()
            
            return wav_data
        except Exception as e:
            print(f"Error converting audio: {e}")
            return audio_data  # Return original if conversion fails
    
    def transcribe_audio_file(self, audio_file_path: str, language: str = "en-US") -> Dict[str, Any]:
        """Transcribe audio from file path"""
        try:
            with sr.AudioFile(audio_file_path) as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.record(source)
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                confidence = "high"  # Google doesn't provide confidence scores
                engine = "google"
            except sr.UnknownValueError:
                # Fallback to other engines
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    confidence = "medium"
                    engine = "sphinx"
                except sr.UnknownValueError:
                    return {
                        "success": False,
                        "error": "Could not understand audio",
                        "text": "",
                        "confidence": "low",
                        "engine": "none"
                    }
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "engine": engine,
                "language": language
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": "low",
                "engine": "none"
            }
    
    def transcribe_audio_bytes(self, audio_data: bytes, input_format: str = "wav", language: str = "en-US") -> Dict[str, Any]:
        """Transcribe audio from bytes data"""
        try:
            # Convert to WAV if needed
            if input_format.lower() != "wav":
                audio_data = self.convert_audio_to_wav(audio_data, input_format)
            
            # Create audio source from bytes
            audio_source = sr.AudioData(audio_data, 16000, 2)  # Assuming 16kHz, 16-bit, stereo
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio_source, language=language)
                confidence = "high"
                engine = "google"
            except sr.UnknownValueError:
                # Fallback to other engines
                try:
                    text = self.recognizer.recognize_sphinx(audio_source)
                    confidence = "medium"
                    engine = "sphinx"
                except sr.UnknownValueError:
                    return {
                        "success": False,
                        "error": "Could not understand audio",
                        "text": "",
                        "confidence": "low",
                        "engine": "none"
                    }
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "engine": engine,
                "language": language
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": "low",
                "engine": "none"
            }
    
    def transcribe_microphone(self, duration: int = 5, language: str = "en-US") -> Dict[str, Any]:
        """Transcribe audio from microphone"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Listening for {duration} seconds...")
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Try Google Speech Recognition first
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                confidence = "high"
                engine = "google"
            except sr.UnknownValueError:
                # Fallback to other engines
                try:
                    text = self.recognizer.recognize_sphinx(audio)
                    confidence = "medium"
                    engine = "sphinx"
                except sr.UnknownValueError:
                    return {
                        "success": False,
                        "error": "Could not understand audio",
                        "text": "",
                        "confidence": "low",
                        "engine": "none"
                    }
            
            return {
                "success": True,
                "text": text,
                "confidence": confidence,
                "engine": engine,
                "language": language
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "text": "",
                "confidence": "low",
                "engine": "none"
            }

# Initialize the speech processor
speech_processor = SpeechToTextProcessor()

@tool
def transcribe_audio_file(audio_file_path: str, language: str = None) -> str:
    """
    Transcribe speech from an audio file to text.
    
    Args:
        audio_file_path (str): Path to the audio file to transcribe
        language (str): Language code for transcription (uses config default if not provided)
        
    Returns:
        str: Transcribed text or error message
    """
    try:
        if not os.path.exists(audio_file_path):
            return f"Error: Audio file not found at {audio_file_path}"
        
        # Use default language from config if not provided
        if not language:
            language = speech_processor.default_language
        
        # Validate language
        if language not in speech_processor.supported_languages:
            return f"Error: Unsupported language '{language}'. Supported languages: {speech_processor.supported_languages}"
        
        result = speech_processor.transcribe_audio_file(audio_file_path, language)
        
        if result["success"]:
            return f"Transcription successful using {result['engine']} engine:\n\n{result['text']}"
        else:
            return f"Transcription failed: {result['error']}"
            
    except Exception as e:
        return f"Error processing audio file: {str(e)}"

@tool
def transcribe_audio_from_microphone(duration: int = 5, language: str = None) -> str:
    """
    Transcribe speech from microphone input to text.
    
    Args:
        duration (int): Duration to listen in seconds (default: 5)
        language (str): Language code for transcription (uses config default if not provided)
        
    Returns:
        str: Transcribed text or error message
    """
    try:
        # Use default language from config if not provided
        if not language:
            language = speech_processor.default_language
        
        # Validate language
        if language not in speech_processor.supported_languages:
            return f"Error: Unsupported language '{language}'. Supported languages: {speech_processor.supported_languages}"
        
        result = speech_processor.transcribe_microphone(duration, language)
        
        if result["success"]:
            return f"Transcription successful using {result['engine']} engine:\n\n{result['text']}"
        else:
            return f"Transcription failed: {result['error']}"
            
    except Exception as e:
        return f"Error processing microphone input: {str(e)}"

@tool
def transcribe_base64_audio(audio_base64: str, input_format: str = "wav", language: str = None) -> str:
    """
    Transcribe speech from base64 encoded audio data to text.
    
    Args:
        audio_base64 (str): Base64 encoded audio data
        input_format (str): Audio format (wav, mp3, etc.) (default: wav)
        language (str): Language code for transcription (uses config default if not provided)
        
    Returns:
        str: Transcribed text or error message
    """
    try:
        # Use default language from config if not provided
        if not language:
            language = speech_processor.default_language
        
        # Validate language
        if language not in speech_processor.supported_languages:
            return f"Error: Unsupported language '{language}'. Supported languages: {speech_processor.supported_languages}"
        
        # Decode base64 audio data
        audio_data = base64.b64decode(audio_base64)
        
        result = speech_processor.transcribe_audio_bytes(audio_data, input_format, language)
        
        if result["success"]:
            return f"Transcription successful using {result['engine']} engine:\n\n{result['text']}"
        else:
            return f"Transcription failed: {result['error']}"
            
    except Exception as e:
        return f"Error processing base64 audio: {str(e)}"

# Tool list for speech functionality
speech_tool_list = [
    transcribe_audio_file,
    transcribe_audio_from_microphone,
    transcribe_base64_audio
]
