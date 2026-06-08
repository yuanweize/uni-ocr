"""UniOCR FastAPI service.

Run with::

    uvicorn uniocr.api:app --host 0.0.0.0 --port 8000

Or via CLI::

    uniocr serve --port 8000
"""

import io
import logging
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import UniOCR, list_available_engines

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="UniOCR API",
    description=(
        "Unified multilingual OCR service. "
        "Upload images or PDFs and get structured text, markdown, and layout blocks."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Lazy singleton OCR instances per engine name
# ---------------------------------------------------------------------------

_ocr_instances: Dict[str, UniOCR] = {}


def _get_ocr(engine: str = "auto") -> UniOCR:
    if engine not in _ocr_instances:
        _ocr_instances[engine] = UniOCR(engine=engine)
    return _ocr_instances[engine]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {"status": "ok", "version": app.version}


@app.get("/engines")
async def engines() -> Dict[str, Any]:
    """List available OCR engines in the current environment."""
    return {"available_engines": list_available_engines()}


@app.post("/extract")
async def extract_file(
    file: UploadFile = File(...),
    engine: str = Form("auto"),
) -> JSONResponse:
    """
    Extract text and layout from an uploaded file (image or PDF).

    - **file**: The file to process (image or PDF).
    - **engine**: Which engine to use (``auto``, ``paddle``, ``apple``).

    Returns a JSON document with ``text``, ``markdown``, and per-page ``blocks``.
    """
    start = time.monotonic()

    # Save uploaded file to a temp location
    suffix = Path(file.filename or "upload").suffix or ".png"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        ocr = _get_ocr(engine)
        doc = ocr.extract(tmp_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        tmp_path.unlink(missing_ok=True)

    elapsed = round(time.monotonic() - start, 3)
    result = doc.to_dict()
    result["elapsed_seconds"] = elapsed

    return JSONResponse(content=result)


@app.post("/extract/url")
async def extract_url(
    url: str = Form(...),
    engine: str = Form("auto"),
) -> JSONResponse:
    """
    Extract text and layout from a URL pointing to an image or PDF.

    - **url**: Public URL of the file.
    - **engine**: Which engine to use.
    """
    start = time.monotonic()

    try:
        ocr = _get_ocr(engine)
        doc = ocr.extract(url)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    elapsed = round(time.monotonic() - start, 3)
    result = doc.to_dict()
    result["elapsed_seconds"] = elapsed

    return JSONResponse(content=result)
