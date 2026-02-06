import pytesseract
from PIL import Image
import os
import sys

# If strictly local, we rely on user having Tesseract installed or we bundle it. 
# For this skeleton, we assume it's in PATH or standard location.
# In a real packaged app, we'd include the binary.

class OCRService:
    def __init__(self, tesseract_cmd=None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
    def extract_text(self, file_path):
        """Extract text from an image or PDF."""
        try:
            # Simple check for extension
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                return pytesseract.image_to_string(Image.open(file_path))
            elif ext == '.pdf':
                try:
                    from pypdf import PdfReader
                    reader = PdfReader(file_path)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text() + "\n"
                    return text if text.strip() else "[OCR Warning: PDF contains no selectable text (Scanned).]"
                except Exception as pdf_err:
                    return f"PDF Error: {pdf_err}"
            else:
                return f"Unsupported file type: {ext}"
        except Exception as e:
            # Fallback for Tesseract not found or other errors
            if "tesseract is not installed" in str(e).lower():
                return f"[OCR Error: Tesseract not installed. Please install Tesseract-OCR or upload a text-based PDF.] Error: {e}"
            return f"Error extracting text: {e}"

# Singleton or factory if needed
_ocr_service = OCRService()

def get_ocr_service():
    return _ocr_service
