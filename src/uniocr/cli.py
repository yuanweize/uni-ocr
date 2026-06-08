"""UniOCR Command Line Interface."""

import argparse
import json
import sys
from pathlib import Path

from . import UniOCR, list_available_engines


def cmd_extract(args: argparse.Namespace) -> None:
    """Handle the 'extract' sub-command."""
    ocr = UniOCR(engine=args.engine)
    engine_cls = ocr.engine.__class__.__name__
    print(f"Processing '{args.input}' with engine: {engine_cls}")

    doc = ocr.extract(args.input)

    if args.format == "json":
        output_text = json.dumps(doc.to_dict(), ensure_ascii=False, indent=2)
    elif args.format == "text":
        output_text = doc.text
    else:  # markdown (default)
        output_text = doc.markdown

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"Done. Output written to: {out_path}")
    else:
        print(output_text)


def cmd_engines(args: argparse.Namespace) -> None:
    """Handle the 'engines' sub-command."""
    available = list_available_engines()
    if available:
        print("Available engines:")
        for name in available:
            print(f"  - {name}")
    else:
        print("No OCR engines detected. Install extras: pip install uniocr[paddle] or uniocr[apple]")


def cmd_serve(args: argparse.Namespace) -> None:
    """Handle the 'serve' sub-command."""
    try:
        import uvicorn
    except ImportError:
        print("uvicorn is required. Install with: pip install uniocr[api]", file=sys.stderr)
        sys.exit(1)

    print(f"Starting UniOCR API server on {args.host}:{args.port} ...")
    uvicorn.run("uniocr.api:app", host=args.host, port=args.port, reload=args.reload)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="uniocr",
        description="UniOCR - Unified multilingual OCR tool.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- extract ---
    p_extract = subparsers.add_parser("extract", help="Extract text from a file or URL.")
    p_extract.add_argument("input", help="File path, URL, or Base64 data URI.")
    p_extract.add_argument("--engine", "-e", default="auto",
                           help="Engine: 'auto', 'paddle', 'apple'. Default: auto.")
    p_extract.add_argument("--output", "-o", help="Write output to file instead of stdout.")
    p_extract.add_argument("--format", "-f", default="markdown",
                           choices=["markdown", "text", "json"],
                           help="Output format. Default: markdown.")
    p_extract.set_defaults(func=cmd_extract)

    # --- engines ---
    p_engines = subparsers.add_parser("engines", help="List available OCR engines.")
    p_engines.set_defaults(func=cmd_engines)

    # --- serve ---
    p_serve = subparsers.add_parser("serve", help="Start the FastAPI server.")
    p_serve.add_argument("--host", default="0.0.0.0", help="Bind host. Default: 0.0.0.0.")
    p_serve.add_argument("--port", "-p", type=int, default=8000, help="Port. Default: 8000.")
    p_serve.add_argument("--reload", action="store_true", help="Enable auto-reload for development.")
    p_serve.set_defaults(func=cmd_serve)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
