import os
import fitz
import docx
import markdown
from pathlib import Path


def parse_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text_parts = []
    for page in doc:
        text_parts.append(page.get_text())
    doc.close()
    return "\n\n".join(text_parts)


def parse_docx(file_path: str) -> str:
    doc = docx.Document(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def parse_markdown(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        md_content = f.read()
    return markdown.markdown(md_content)


def parse_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        image = Image.open(file_path)
        return pytesseract.image_to_string(image).strip()
    except ImportError:
        return "OCR requires pytesseract and Pillow. Install: pip install pytesseract Pillow"
    except Exception as e:
        return f"OCR failed: {str(e)}"


def parse_audio(file_path: str) -> str:
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(file_path)
        return result["text"].strip()
    except ImportError:
        return "Audio requires openai-whisper. Install: pip install openai-whisper"
    except Exception as e:
        return f"Transcription failed: {str(e)}"


PARSERS = {
    ".pdf": parse_pdf,
    ".docx": parse_docx,
    ".txt": parse_txt,
    ".md": parse_markdown,
    ".png": parse_image,
    ".jpg": parse_image,
    ".jpeg": parse_image,
    ".bmp": parse_image,
    ".tiff": parse_image,
    ".tif": parse_image,
    ".webp": parse_image,
    ".mp3": parse_audio,
    ".wav": parse_audio,
    ".m4a": parse_audio,
    ".ogg": parse_audio,
    ".flac": parse_audio,
    ".wma": parse_audio,
    ".aac": parse_audio,
}


def extract_text(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    parser = PARSERS.get(ext)
    if not parser:
        raise ValueError(f"Unsupported file type: {ext}")
    return parser(file_path)
