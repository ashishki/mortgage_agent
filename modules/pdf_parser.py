# modules/pdf_parser.py
"""
Extract text from PDFs using pdfplumber with an OCR fallback via Tesseract.
"""
import io
import pdfplumber

class PDFParser:
    def __init__(self, ocr_config: dict):
        """
        Initialize the parser.

        Args:
            ocr_config: dict of OCR settings (e.g., language, tesseract_cmd).
        """
        self.ocr_config = ocr_config

    def extract_text(self, pdf_bytes: bytes) -> str:
        """
        Extract text from a PDF. Use pdfplumber first; if no text found, use OCR.

        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            Extracted text as a single string.
        """
        # Open the PDF from bytes
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            # Collect text from each page
            texts = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                texts.append(page_text)
            combined = "\n".join(texts)

        # If extracted text is empty or whitespace-only, fallback to OCR
        if not combined.strip():
            return self._ocr_extract(pdf_bytes)
        return combined

    def _ocr_extract(self, pdf_bytes: bytes) -> str:
        """
        Perform OCR on PDF bytes using Tesseract via PIL.Image (placeholder).

        Args:
            pdf_bytes: Raw bytes of the PDF.

        Returns:
            OCR-extracted text as a string.
        """
        # TODO: implement OCR extraction: convert PDF pages to images and run pytesseract
        return ""  # placeholder implementation
