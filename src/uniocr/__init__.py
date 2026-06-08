"""UniOCR - Unified multilingual OCR abstraction layer."""

import logging
from pathlib import Path
from typing import Optional, Union

from .models import Block, Document, DocumentPage
from .engines import get_engine, list_available_engines
from .processors.input import InputProcessor

logger = logging.getLogger(__name__)


class UniOCR:
    """Main entry point for the UniOCR library.
    
    Usage::
    
        from uniocr import UniOCR
        
        ocr = UniOCR(engine="auto")
        doc = ocr.extract("document.pdf")
        print(doc.markdown)
    """

    def __init__(self, engine: str = "auto") -> None:
        self._engine_name = engine
        self.processor = InputProcessor()
        self.engine = get_engine(engine)

    def extract(self, input_source: Union[str, Path], **kwargs) -> Document:
        """
        Extract text and structured layout from the given input.

        Args:
            input_source: File path (str or Path), URL, or data-URI / base64 string.
            **kwargs: Passed through to the underlying engine (e.g. ``languages``).

        Returns:
            A :class:`Document` containing pages, blocks, text, and markdown.
        """
        image_paths = self.processor.process(input_source)

        all_pages = []
        for path in image_paths:
            doc = self.engine.extract(path, **kwargs)
            all_pages.extend(doc.pages)

        # Re-number pages sequentially
        for idx, page in enumerate(all_pages):
            page.page_number = idx + 1

        result = Document(
            pages=all_pages,
            engine_name=self.engine.__class__.__name__,
        )
        return result


__all__ = [
    "UniOCR",
    "Document",
    "DocumentPage",
    "Block",
    "get_engine",
    "list_available_engines",
]
