"""Base Processor Abstractions.

Defines the interface for document and data processors.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional, Union

from utils.logger import get_logger


class BaseProcessor(ABC):
    """Abstract base class for all CRIS processors.
    
    Processors handle raw data ingestion, OCR, and extraction.
    """
    
    name: str
    
    def __init__(self, **kwargs: Any) -> None:
        """Initialize the processor.
        
        Args:
            **kwargs: Configuration for the processor.
        """
        self.logger = get_logger(f"processor.{self.name}")
        self.config = kwargs

    @abstractmethod
    async def process(self, source: Union[str, Path, bytes], **kwargs: Any) -> Any:
        """Process the source data and return structured results.
        
        Args:
            source: The path to a file, a URL, or raw bytes.
            **kwargs: Additional processing options.
            
        Returns:
            Structured data extracted from the source.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return the list of file formats supported by this processor.
        
        Returns:
            List of extensions (e.g., [".pdf", ".jpg"]).
        """
        pass
