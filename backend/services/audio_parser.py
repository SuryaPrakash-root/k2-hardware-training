import os
from pathlib import Path


def parse_audio(file_path: str) -> str:
    try:
        import whisper
        
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"].strip()
    except ImportError:
        return "Audio transcription requires openai-whisper. Install: pip install openai-whisper"
    except Exception as e:
        return f"Transcription failed: {str(e)}"


def parse_audio_faster(file_path: str) -> str:
    try:
        from faster_whisper import WhisperModel
        
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(file_path, beam_size=5)
        
        text = " ".join([segment.text for segment in segments])
        return text.strip()
    except ImportError:
        return parse_audio(file_path)
    except Exception as e:
        return f"Transcription failed: {str(e)}"


AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.wma', '.aac'}
