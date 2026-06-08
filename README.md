# UniOCR

**Unified multilingual OCR abstraction layer** — one API, multiple engines, zero friction.

UniOCR wraps best-in-class OCR engines behind a single, clean interface. Throw any image or PDF at it and get back structured text, Markdown, and layout blocks — regardless of which engine runs under the hood.

## ✨ Features

- 🔌 **Pluggable engines** — PaddleOCR-VL (deep document analysis) and Apple Vision (instant macOS native) with automatic priority fallback.
- 📄 **Accepts anything** — local file paths, URLs, Base64 data URIs, and multi-page PDFs (auto-flattened to images).
- 📦 **Unified output** — every engine returns the same `Document → Pages → Blocks` structure with text, Markdown, bounding boxes, and confidence scores.
- 🌐 **REST API included** — a built-in FastAPI service so any language (Go, JS, Java…) can call OCR over HTTP.
- 🖥️ **CLI** — `uniocr extract`, `uniocr engines`, `uniocr serve` — ready to use from the terminal.

## 🚀 Quick Start

### Install

```bash
# Core (lightweight, includes PDF flattening)
pip install uniocr

# With Apple Vision support (macOS only)
pip install "uniocr[apple]"

# With PaddleOCR-VL support (powerful, downloads ~1 GB model on first run)
pip install "uniocr[paddle]"

# With REST API server
pip install "uniocr[api]"

# Everything
pip install "uniocr[all]"
```

### Python SDK

```python
from uniocr import UniOCR

ocr = UniOCR(engine="auto")  # auto-selects best available engine
doc = ocr.extract("invoice.pdf")

print(doc.text)      # plain text
print(doc.markdown)  # structured Markdown
print(doc.to_dict()) # full JSON-serializable dict
```

### CLI

```bash
# List available engines
uniocr engines

# Extract from a file
uniocr extract document.pdf --format markdown

# Extract from a URL, output as JSON
uniocr extract "https://example.com/scan.png" --format json -o result.json

# Start the API server
uniocr serve --port 8000
```

### REST API

```bash
# Start server
uniocr serve --port 8000

# Health check
curl http://localhost:8000/health

# List engines
curl http://localhost:8000/engines

# Upload a file
curl -X POST http://localhost:8000/extract \
  -F "file=@document.pdf" \
  -F "engine=auto"

# From a URL
curl -X POST http://localhost:8000/extract/url \
  -F "url=https://example.com/image.png"
```

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│         User Interface          │
│   (SDK / CLI / FastAPI)         │
├─────────────────────────────────┤
│       Input Processor           │
│  URL → File, PDF → Images,     │
│  Base64 → File                  │
├─────────────────────────────────┤
│      Engine Dispatcher          │
│  auto → Paddle → Apple → ...   │
├──────────┬──────────────────────┤
│ Paddle   │  Apple Vision        │
│ Adapter  │  Adapter             │
├──────────┴──────────────────────┤
│     Standardized Output         │
│  Document → Pages → Blocks      │
│  .text / .markdown / .to_dict() │
└─────────────────────────────────┘
```

## 🔧 Engine Priority (auto mode)

| Priority | Engine | Best for |
|----------|--------|----------|
| 1 | **PaddleOCR-VL** | Complex layouts, tables, formulas, 109-language support |
| 2 | **Apple Vision** | Fast, zero-dependency on macOS, great for simple text |
| 3 | *Tesseract* (planned) | Lightweight cross-platform fallback |

## 📁 Project Structure

```
uni-ocr/
├── src/uniocr/
│   ├── __init__.py        # UniOCR main class
│   ├── models.py          # Document, DocumentPage, Block dataclasses
│   ├── cli.py             # CLI (extract, engines, serve)
│   ├── api.py             # FastAPI REST service
│   ├── engines/
│   │   ├── base.py        # BaseOCREngine ABC
│   │   ├── apple_vision.py
│   │   └── paddle.py
│   └── processors/
│       └── input.py       # URL/Base64/PDF input handling
├── pyproject.toml
├── CLAUDE.md              # Development guidelines
└── README.md
```

## License

MIT
