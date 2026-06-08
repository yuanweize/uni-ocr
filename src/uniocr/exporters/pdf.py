import logging
from pathlib import Path

import fitz

from ..models import Document

logger = logging.getLogger(__name__)


def export_to_pdf(doc: Document, input_path: Path, output_path: Path) -> None:
    """Generate a searchable PDF (双层 PDF) by overlaying invisible text on the original image/PDF."""
    logger.info("Generating searchable PDF: %s", output_path)
    
    # Check if input is a PDF or an Image
    is_pdf = input_path.suffix.lower() == ".pdf"
    
    try:
        src_doc = fitz.open(input_path)
    except Exception as e:
        logger.error("Failed to open input file for PDF generation: %s", e)
        raise RuntimeError(f"Failed to open input file for PDF generation: {e}")

    # If it's an image, convert to PDF document
    if not is_pdf:
        pdf_bytes = src_doc.convert_to_pdf()
        src_doc.close()
        src_doc = fitz.open("pdf", pdf_bytes)

    # Validate page counts match (in case engine processed subset or failed)
    if len(src_doc) != len(doc.pages):
        logger.warning(
            "Page count mismatch: Input has %d pages, Document has %d pages. "
            "PDF might be incomplete or misaligned.",
            len(src_doc), len(doc.pages)
        )

    # Prepare CJK Font for Chinese characters
    font = fitz.Font("cjk")
    font_name = "cjk"

    for i, page_data in enumerate(doc.pages):
        if i >= len(src_doc):
            break  # Prevent index out of bounds if mismatch
            
        pdf_page = src_doc[i]
        
        # Load font into this page
        pdf_page.insert_font(fontname=font_name, fontbuffer=font.buffer)
        
        # Overlay invisible text blocks
        for block in page_data.blocks:
            if not block.text.strip():
                continue
                
            x1, y1, x2, y2 = block.bbox
            width = x2 - x1
            height = y2 - y1
            
            if width <= 0 or height <= 0:
                continue
                
            rect = fitz.Rect(x1, y1, x2, y2)
            
            # Use height as approximate font size
            fontsize = height
            if fontsize < 4:
                fontsize = 4  # Minimum readable size logic
                
            # render_mode=3 makes text invisible but selectable
            try:
                # We use insert_textbox to fit the text into the bounding box
                # It handles wrapping if necessary
                pdf_page.insert_textbox(
                    rect,
                    block.text,
                    fontsize=fontsize,
                    fontname=font_name,
                    render_mode=3,
                    align=0, # left align
                )
            except Exception as e:
                logger.debug("Failed to insert text at %s: %s", rect, e)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    src_doc.save(str(output_path))
    src_doc.close()
    logger.info("Searchable PDF saved to %s", output_path)
