# tests/test_pdf_parser.py
import pytest
import pdfplumber
from modules.pdf_parser import PDFParser

class DummyPage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text

class DummyPDF:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

@pytest.fixture
def parser():
    # Initialize parser with dummy OCR config
    return PDFParser(ocr_config={})


def test_extract_text_with_pdfplumber(parser, monkeypatch):
    # Mock pdfplumber.open to return a PDF with text
    dummy_pdf = DummyPDF([DummyPage("Page 1 text"), DummyPage("Page 2 text")])
    monkeypatch.setattr(pdfplumber, 'open', lambda stream: dummy_pdf)

    result = parser.extract_text(b"fake pdf bytes")
    # Should concatenate texts
    assert "Page 1 text" in result
    assert "Page 2 text" in result


def test_ocr_fallback_when_pdfplumber_empty(parser, monkeypatch):
    # Mock pdfplumber.open to return pages with empty text
    dummy_pdf = DummyPDF([DummyPage(""), DummyPage(None)])
    monkeypatch.setattr(pdfplumber, 'open', lambda stream: dummy_pdf)

    # Monkeypatch OCR method
    monkeypatch.setattr(PDFParser, '_ocr_extract', lambda self, b: "OCR output text")

    result = parser.extract_text(b"fake pdf bytes")
    # Should be OCR fallback result
    assert result == "OCR output text"
