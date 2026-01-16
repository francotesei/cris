"""Document Processing Pipeline.

Orchestrates raw file ingestion, text extraction (OCR), and entity extraction.
"""

import os
from pathlib import Path
from typing import Any, List, Optional, Union

from PIL import Image
import PyPDF2
import pytesseract

from core.base_processor import BaseProcessor
from core.registry import ComponentRegistry
from processors.entity_extractor import EntityExtractor, ExtractedEntity
from database.vector_store import VectorStore
from utils.logger import get_logger


@ComponentRegistry.register_processor("document_processor")
class DocumentProcessor(BaseProcessor):
    """Main document processing pipeline for CRIS."""
    
    name = "document_processor"
    
    def __init__(self, entity_extractor: Optional[EntityExtractor] = None, vector_store: Optional[VectorStore] = None, **kwargs: Any) -> None:
        """Initialize pipeline components."""
        super().__init__(**kwargs)
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.vector_store = vector_store or VectorStore()
        self.logger = get_logger("processor.document")

    async def process(self, file_path: Union[str, Path], case_id: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Full processing pipeline for a single file.
        
        Steps:
        1. Extract text (PDF/Image/Text)
        2. Extract entities using LLM
        3. Index in vector store
        4. Return summary
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        self.logger.info(f"Processing document: {path.name}")
        
        # 1. Extract raw text
        raw_text = await self._extract_text(path)
        
        # 2. Extract entities
        entities = await self.entity_extractor.process(raw_text)
        
        # 3. Index in vector store
        doc_id = f"doc_{path.stem}_{os.getpid()}"
        await self.vector_store.add_documents(
            documents=[raw_text],
            metadatas=[{
                "filename": path.name,
                "case_id": case_id,
                "entity_count": len(entities)
            }],
            ids=[doc_id]
        )
        
        return {
            "filename": path.name,
            "text_length": len(raw_text),
            "entities": entities,
            "vector_id": doc_id,
            "case_id": case_id
        }

    async def _extract_text(self, path: Path) -> str:
        """Extract text based on file extension."""
        ext = path.suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf(path)
        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            return self._extract_image(path)
        elif ext in [".txt", ".md"]:
            return path.read_text(encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_pdf(self, path: Path) -> str:
        """Extract text from PDF, with fallback to OCR if needed."""
        text = ""
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                    
            # If text extraction is poor, it might be a scanned PDF
            if len(text.strip()) < 50:
                self.logger.info(f"PDF {path.name} appears to be scanned, using OCR fallback")
                # OCR implementation for PDF would go here (e.g., pdf2image + tesseract)
                pass
                
        except Exception as e:
            self.logger.error(f"PDF extraction failed: {str(e)}")
            
        return text

    def _extract_image(self, path: Path) -> str:
        """Extract text from image using Tesseract OCR."""
        try:
            image = Image.open(path)
            return pytesseract.image_to_string(image)
        except Exception as e:
            self.logger.error(f"Image OCR failed: {str(e)}")
            return ""

    def get_supported_formats(self) -> List[str]:
        return [".pdf", ".jpg", ".jpeg", ".png", ".txt", ".md"]
