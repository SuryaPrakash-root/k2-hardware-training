import os
from pathlib import Path


def parse_image(file_path: str) -> str:
    try:
        import pytesseract
        from PIL import Image
        
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except ImportError:
        return "OCR requires pytesseract and Pillow. Install: pip install pytesseract Pillow"
    except Exception as e:
        return f"OCR failed: {str(e)}"


def get_image_info(file_path: str) -> dict:
    try:
        from PIL import Image
        image = Image.open(file_path)
        return {
            "format": image.format,
            "mode": image.mode,
            "size": image.size,
        }
    except Exception:
        return {}


IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp'}
