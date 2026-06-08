import logging
from pathlib import Path
from typing import Any, Optional, Union

from .base import BaseOCREngine
from ..models import Document, DocumentPage, Block

logger = logging.getLogger(__name__)


class PaddleOCRVLAdapter(BaseOCREngine):
    """
    PaddleOCR-VL Adapter.
    Uses PaddleOCRVL internally for comprehensive document analysis.
    Lazy-loads the heavy model on first call to extract().
    """

    def __init__(self, device: str = "cpu") -> None:
        self._device = device
        self._pipeline: Optional[Any] = None  # Lazy-loaded

    def _get_pipeline(self) -> Any:
        """Lazy-load the PaddleOCR-VL pipeline on first use."""
        if self._pipeline is None:
            logger.info("Loading PaddleOCR-VL pipeline (this may take a moment)...")
            from paddleocr import PaddleOCRVL
            self._pipeline = PaddleOCRVL(device=self._device)
        return self._pipeline

    def is_available(self) -> bool:
        try:
            import paddleocr  # noqa: F401
            return True
        except ImportError:
            return False

    def extract(self, input_source: Union[str, Path], **kwargs: Any) -> Document:
        input_path = Path(input_source)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        pipeline = self._get_pipeline()
        results_generator = pipeline.predict(input=str(input_path))

        pages = []
        for i, res in enumerate(results_generator):
            blocks = []
            parsed_res = res.res.get("parsing_res_list", [])
            for block_data in parsed_res:
                raw_bbox = block_data.get("block_bbox", (0, 0, 0, 0))
                blocks.append(
                    Block(
                        block_type=block_data.get("block_label", "text"),
                        text=block_data.get("block_content", ""),
                        bbox=tuple(float(v) for v in raw_bbox),
                        confidence=1.0,
                        extra_data=block_data,
                    )
                )

            # Attempt to use structured output methods if available
            page_text = ""
            page_md = ""
            try:
                page_md = res.save_to_markdown() if hasattr(res, "save_to_markdown") else ""
            except Exception:
                pass
            
            # Fallback: concatenate block content
            if not page_text:
                page_text = "\n".join(b.text for b in blocks)
            if not page_md:
                page_md = "\n\n".join(b.text for b in blocks)

            pages.append(
                DocumentPage(
                    page_number=i + 1,
                    blocks=blocks,
                    text=page_text,
                    markdown=page_md,
                )
            )

        return Document(pages=pages)
