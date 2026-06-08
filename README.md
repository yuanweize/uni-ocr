<p align="center">
  <img src="assets/logo.svg" alt="UniOCR Logo" width="400"/>
</p>

<p align="center">
  <strong>One API. Multiple engines. Zero friction.</strong>
</p>

<p align="center">
  <a href="https://github.com/yuanweize/uni-ocr/actions"><img src="https://img.shields.io/github/actions/workflow/status/yuanweize/uni-ocr/ci.yml?style=flat-square&logo=github" alt="CI"></a>
  <a href="https://pypi.org/project/uniocr/"><img src="https://img.shields.io/pypi/v/uniocr?style=flat-square&logo=pypi&logoColor=white" alt="PyPI"></a>
  <a href="https://github.com/yuanweize/uni-ocr/pkgs/container/uni-ocr"><img src="https://img.shields.io/badge/GHCR-Docker-blue?style=flat-square&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="LICENSE"><img src="https://img.shields.io/github/license/yuanweize/uni-ocr?style=flat-square" alt="License"></a>
  <a href="README_zh.md"><img src="https://img.shields.io/badge/文档-中文版-orange?style=flat-square" alt="中文文档"></a>
</p>

---

**UniOCR** is a unified, multilingual OCR abstraction layer that wraps best-in-class OCR engines behind a single, clean interface. Throw any image or PDF at it — get back structured text, Markdown, and layout blocks — regardless of which engine runs under the hood.

## ✨ Highlights

- 🔌 **Pluggable engines** — PaddleOCR-VL (deep document AI) and Apple Vision (native macOS) with automatic priority fallback
- ⚡ **Zero-config acceleration** — Auto-detects Apple Silicon and launches MLX-VLM for Neural Engine speedup. No manual setup.
- 📄 **Accepts anything** — file paths, URLs, Base64 data URIs, multi-page PDFs (auto-flattened)
- 📦 **Unified output** — `Document → Pages → Blocks` with `.text`, `.markdown`, `.to_dict()`
- 🌐 **REST API included** — FastAPI service with Swagger docs, batch processing, and request tracking
- 🐳 **Docker ready** — Single command deployment via Docker Compose
- 🖥️ **CLI** — `uniocr extract`, `uniocr engines`, `uniocr serve`

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────┐
│              User Interface Layer                │
│         SDK  ·  CLI  ·  REST API                 │
├──────────────────────────────────────────────────┤
│              Input Processor                     │
│    URL → File  ·  PDF → Images  ·  Base64        │
├──────────────────────────────────────────────────┤
│           Engine Dispatcher (auto)               │
│    PaddleOCR-VL → Apple Vision → fallback        │
├────────────────┬─────────────────────────────────┤
│  PaddleOCR-VL  │      Apple Vision               │
│  + MLX-VLM     │      (native macOS)              │
│  (auto-accel)  │                                  │
├────────────────┴─────────────────────────────────┤
│           Standardised Output                    │
│    Document → Pages → Blocks                     │
│    .text  ·  .markdown  ·  .to_dict()            │
└──────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Installation

```bash
# Core only (lightweight)
pip install uniocr

# With PaddleOCR-VL (powerful document AI, ~1.8 GB model)
pip install "uniocr[paddle]"

# With Apple Vision (macOS only, zero-dependency)
pip install "uniocr[apple]"

# With REST API server
pip install "uniocr[api]"

# Everything
pip install "uniocr[all]"
```

### Python SDK

```python
from uniocr import UniOCR

ocr = UniOCR(engine="auto")          # Auto-selects best engine
doc = ocr.extract("invoice.pdf")

print(doc.text)                       # Plain text
print(doc.markdown)                   # Structured Markdown
print(doc.to_dict())                  # JSON-serialisable dict

for page in doc.pages:
    for block in page.blocks:
        print(f"[{block.block_type}] {block.text} @ {block.bbox}")
```

### CLI

```bash
# List available engines
uniocr engines

# Extract text (auto-selects engine)
uniocr extract document.pdf

# Specify engine and output format
uniocr extract scan.png --engine apple --format json -o result.json

# Start the API server
uniocr serve --port 8000 --workers 4
```

### REST API

```bash
# Start
uniocr serve --port 8000

# Health check
curl http://localhost:8000/health

# Extract from uploaded file
curl -X POST http://localhost:8000/extract \
  -F "file=@document.pdf" \
  -F "engine=auto"

# Extract from URL
curl -X POST http://localhost:8000/extract/url \
  -F "url=https://example.com/image.png"

# Batch processing
curl -X POST http://localhost:8000/extract/batch \
  -F "files=@page1.png" \
  -F "files=@page2.png"
```

Interactive API docs are available at `http://localhost:8000/docs` (Swagger UI).

### Docker

```bash
# Pull and run
docker run -p 8000:8000 ghcr.io/yuanweize/uni-ocr:latest

# Or use Docker Compose
docker compose up
```

## 🔧 Engine Priority

When `engine="auto"`, UniOCR selects the best available engine:

| Priority | Engine | Best for | Speed |
|----------|--------|----------|-------|
| 1 | **PaddleOCR-VL** + MLX-VLM | Complex layouts, tables, formulas, 109 languages | ⚡⚡ |
| 2 | **PaddleOCR-VL** (CPU) | Same capabilities, no MLX-VLM | ⚡ |
| 3 | **Apple Vision** | Simple text, macOS only, instant | ⚡⚡⚡ |

> On Apple Silicon with `mlx-vlm` installed, PaddleOCR-VL **automatically** starts an MLX-VLM server for Neural Engine acceleration. No configuration needed.

## ⚙️ Configuration

UniOCR works out of the box with zero configuration. For advanced use cases:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `UNIOCR_MLX_VLM_URL` | Override MLX-VLM server URL | Auto-detected |
| `UNIOCR_MLX_VLM_MODEL` | MLX-VLM model name | `PaddlePaddle/PaddleOCR-VL-1.6` |

## 📁 Project Structure

```
uni-ocr/
├── src/uniocr/
│   ├── __init__.py          # UniOCR main class & public API
│   ├── models.py            # Document / Page / Block dataclasses
│   ├── cli.py               # CLI (extract · engines · serve)
│   ├── api.py               # FastAPI REST service
│   ├── engines/
│   │   ├── __init__.py      # Engine registry & auto-dispatcher
│   │   ├── base.py          # BaseOCREngine ABC
│   │   ├── apple_vision.py  # macOS Vision adapter
│   │   └── paddle.py        # PaddleOCR-VL + MLX-VLM adapter
│   └── processors/
│       └── input.py         # URL / Base64 / PDF input handling
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md
```

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request.

## 📄 License

[MIT](LICENSE) © 2026 Weize Yuan
