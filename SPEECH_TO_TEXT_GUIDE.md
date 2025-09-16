# Speech-to-Text Integration Guide

This guide explains how to use the speech-to-text functionality in your News Aggregator Agent.

## Overview

The agent now supports speech-to-text conversion through multiple methods:
- Audio file transcription
- Microphone input transcription
- Base64 encoded audio transcription

## Installation

Make sure you have the required dependencies installed:

```bash
pip install speechrecognition pydub pyaudio
```

**Note for Windows users:** You may need to install PyAudio separately:
```bash
pip install pipwin
pipwin install pyaudio
```

## Configuration

The speech recognition settings can be configured in `config/config.yaml`:

```yaml
speech_recognition:
  default_language: "en-US"
  supported_languages:
    - "en-US"
    - "en-GB"
    - "es-ES"
    - "fr-FR"
    - "de-DE"
    - "it-IT"
    - "pt-BR"
    - "ru-RU"
    - "ja-JP"
    - "ko-KR"
    - "zh-CN"
  energy_threshold: 300
  pause_threshold: 0.8
  phrase_threshold: 0.3
  non_speaking_duration: 0.8
```

## Usage Methods

### 1. API Endpoint for Audio File Transcription

**Endpoint:** `POST /transcribe`

**Parameters:**
- `audio_file_path`: Path to the audio file
- `language`: Language code (optional, uses config default)

**Example:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_file_path": "/path/to/audio.wav",
    "language": "en-US"
  }'
```

### 2. Integrated Query with Audio

**Endpoint:** `POST /query`

**Parameters:**
- `question`: Your question (will be combined with transcribed text)
- `audio_file_path`: Path to audio file (optional)
- `language`: Language for transcription (optional)
- `model_provider`: LLM provider (optional)
- `thread_id`: Conversation thread ID (optional)

**Example:**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the latest developments?",
    "audio_file_path": "/path/to/audio.wav",
    "language": "en-US",
    "model_provider": "groq"
  }'
```

### 3. Direct Tool Usage

You can also use the speech-to-text tools directly in your code:

```python
from tools.speech_tools import transcribe_audio_file, transcribe_audio_from_microphone

# Transcribe from file
result = transcribe_audio_file("/path/to/audio.wav", "en-US")
print(result)

# Transcribe from microphone (5 seconds)
result = transcribe_audio_from_microphone(duration=5, language="en-US")
print(result)
```

## Supported Audio Formats

The system supports various audio formats:
- WAV (recommended)
- MP3
- M4A
- FLAC
- OGG

## Language Support

Currently supported languages:
- English (US, GB)
- Spanish (ES)
- French (FR)
- German (DE)
- Italian (IT)
- Portuguese (BR)
- Russian (RU)
- Japanese (JP)
- Korean (KR)
- Chinese (CN)

## Recognition Engines

The system uses multiple recognition engines with fallback:
1. **Google Speech Recognition** (primary) - High accuracy, requires internet
2. **Sphinx** (fallback) - Offline, lower accuracy

## Error Handling

The system provides detailed error messages for common issues:
- Unsupported audio formats
- Network connectivity issues
- Invalid language codes
- Audio file not found
- Recognition failures

## Best Practices

1. **Audio Quality**: Use clear, noise-free audio for best results
2. **File Format**: WAV format typically provides the best recognition accuracy
3. **Language Selection**: Always specify the correct language code
4. **File Size**: Keep audio files under 10MB for optimal performance
5. **Duration**: For microphone input, 5-10 seconds is usually sufficient

## Troubleshooting

### Common Issues:

1. **"No module named 'pyaudio'"**
   - Install PyAudio: `pip install pyaudio`
   - On Windows: `pip install pipwin && pipwin install pyaudio`

2. **"Could not understand audio"**
   - Check audio quality and volume
   - Ensure correct language is selected
   - Try different audio format

3. **"Audio file not found"**
   - Verify file path is correct
   - Check file permissions

4. **Network errors with Google Speech Recognition**
   - Check internet connection
   - The system will automatically fallback to Sphinx

## Integration with News Agent

When you provide an audio file with your query, the agent will:
1. Transcribe the audio to text
2. Combine the transcribed text with your question
3. Search for relevant news based on the combined input
4. Provide a comprehensive response

Example workflow:
1. Record yourself saying "What are the latest AI developments?"
2. Save as audio file
3. Send to `/query` endpoint with audio_file_path
4. Agent transcribes and searches for AI news
5. Returns formatted news results

## Security Considerations

- Audio files are processed locally
- No audio data is stored permanently
- Transcribed text is only used for the current query
- Consider file cleanup for sensitive audio content


