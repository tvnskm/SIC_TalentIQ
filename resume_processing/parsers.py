from abc import ABC, abstractmethod
from common.exceptions import ResumeProcessingError, InvalidFileFormatError

class BaseParser(ABC):
    """
    Abstract base class for all document parsers.
    Demonstrates: Abstraction, Encapsulation
    """
    def __init__(self, file_path: str):
        self._file_path = file_path      # encapsulated with underscore
        self._raw_text = ""
    
    @abstractmethod
    def extract_text(self) -> str:
        """Must be implemented by all subclasses — Polymorphism"""
        pass
    
    def get_raw_text(self) -> str:
        return self._raw_text
    
    def _clean_text(self, text: str) -> str:
        """Protected method — shared by all subclasses"""
        import re
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


class PDFParser(BaseParser):
    """Concrete parser for PDF files — Inheritance from BaseParser"""
    def extract_text(self) -> str:
        import PyPDF2
        try:
            with open(self._file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                pages = [page.extract_text() or "" for page in reader.pages]
                self._raw_text = self._clean_text(" ".join(pages))
            return self._raw_text
        except Exception as e:
            raise ResumeProcessingError(f"PDF parsing failed: {e}")


class DOCXParser(BaseParser):
    """Concrete parser for DOCX files — Inheritance from BaseParser"""
    def extract_text(self) -> str:
        from docx import Document
        try:
            doc = Document(self._file_path)
            paragraphs = [p.text for p in doc.paragraphs]
            self._raw_text = self._clean_text(" ".join(paragraphs))
            return self._raw_text
        except Exception as e:
            raise ResumeProcessingError(f"DOCX parsing failed: {e}")


class TXTParser(BaseParser):
    """Concrete parser for TXT files — Inheritance from BaseParser"""
    def extract_text(self) -> str:
        try:
            with open(self._file_path, 'r', encoding='utf-8', errors='ignore') as f:
                self._raw_text = self._clean_text(f.read())
            return self._raw_text
        except Exception as e:
            raise ResumeProcessingError(f"TXT parsing failed: {e}")


class ParserFactory:
    """
    Factory Pattern — returns the correct parser based on file extension.
    Demonstrates: Factory Design Pattern, Open/Closed Principle
    """
    _parser_map = {
        'pdf':  PDFParser,
        'docx': DOCXParser,
        'txt':  TXTParser,
    }
    
    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        ext = file_path.rsplit('.', 1)[-1].lower()
        parser_class = ParserFactory._parser_map.get(ext)
        if not parser_class:
            raise InvalidFileFormatError(f"Unsupported file type: {ext}")
        return parser_class(file_path)
    
    @staticmethod
    def supported_formats() -> list:
        return list(ParserFactory._parser_map.keys())
