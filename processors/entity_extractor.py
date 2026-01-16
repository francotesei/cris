"""Entity Extraction Processor.

Extracts structured criminal investigation entities from unstructured text using LLM.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from core.base_processor import BaseProcessor
from core.registry import ComponentRegistry
from services.llm_service import LLMService
from config.prompts import ENTITY_EXTRACTION_PROMPT


class ExtractedEntity(BaseModel):
    """Represents a single extracted entity."""
    type: str = Field(..., description="Entity type: PERSON, LOCATION, DATE, etc.")
    value: str = Field(..., description="The extracted text value")
    context: Optional[str] = Field(None, description="Surrounding context")
    confidence: str = Field("medium", description="Confidence level: low, medium, high")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EntityList(BaseModel):
    """List of extracted entities."""
    entities: List[ExtractedEntity]


@ComponentRegistry.register_processor("entity_extractor")
class EntityExtractor(BaseProcessor):
    """Processor that uses LLM to extract entities from text."""
    
    name = "entity_extractor"
    
    def __init__(self, llm_service: Optional[LLMService] = None, **kwargs: Any) -> None:
        """Initialize with LLM service."""
        super().__init__(**kwargs)
        self.llm_service = llm_service or LLMService()

    async def process(self, text: str, **kwargs: Any) -> List[ExtractedEntity]:
        """Extract entities from the provided text.
        
        Args:
            text: The unstructured text to analyze.
            **kwargs: Additional options.
            
        Returns:
            List of ExtractedEntity objects.
        """
        self.logger.info(f"Extracting entities from text ({len(text)} chars)")
        
        prompt = ENTITY_EXTRACTION_PROMPT.format(text=text)
        
        try:
            result = await self.llm_service.generate_structured(
                prompt=prompt,
                schema=EntityList,
                system_instruction="You are an expert criminal investigation assistant specialized in Named Entity Recognition (NER)."
            )
            return result.entities
        except Exception as e:
            self.logger.error(f"Entity extraction failed: {str(e)}")
            return []

    def get_supported_formats(self) -> List[str]:
        return [".txt", ".md"]
    
    async def extract_from_json(self, data: Dict[str, Any]) -> List[ExtractedEntity]:
        """Convert structured JSON data into entities (useful for existing datasets)."""
        # This could be implemented to map JSON keys directly to entity types
        pass
