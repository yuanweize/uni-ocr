import logging
from typing import List

from .base import BaseOCREngine

logger = logging.getLogger(__name__)

# Registry of engine names -> (module_path, class_name)
_ENGINE_REGISTRY = [
    ("paddle", "uniocr.engines.paddle", "PaddleOCRVLAdapter"),
    ("apple", "uniocr.engines.apple_vision", "AppleVisionAdapter"),
]


def list_available_engines() -> List[str]:
    """Return a list of engine names that are currently usable."""
    available = []
    for name, mod_path, cls_name in _ENGINE_REGISTRY:
        try:
            import importlib
            mod = importlib.import_module(mod_path)
            cls = getattr(mod, cls_name)
            inst = cls.__new__(cls)
            if inst.is_available():
                available.append(name)
        except Exception:
            pass
    return available


def get_engine(engine_name: str = "auto") -> BaseOCREngine:
    """
    Factory function to get the appropriate OCR engine.
    If engine_name is 'auto', it tries engines in priority order
    (PaddleOCR → Apple Vision) and returns the first available one.
    """
    import importlib

    if engine_name == "auto":
        for name, mod_path, cls_name in _ENGINE_REGISTRY:
            try:
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name)
                adapter = cls()
                if adapter.is_available():
                    logger.info("Auto-selected engine: %s (%s)", name, cls_name)
                    return adapter
            except Exception as e:
                logger.debug("Engine '%s' unavailable: %s", name, e)
        raise RuntimeError(
            "No suitable OCR engine found. "
            "Install paddleocr (pip install uniocr[paddle]) or "
            "pyobjc-framework-Vision (pip install uniocr[apple]) on macOS."
        )

    # Explicit engine requested
    for name, mod_path, cls_name in _ENGINE_REGISTRY:
        if name == engine_name:
            try:
                mod = importlib.import_module(mod_path)
                cls = getattr(mod, cls_name)
                adapter = cls()
                if adapter.is_available():
                    logger.info("Using engine: %s (%s)", name, cls_name)
                    return adapter
                else:
                    raise RuntimeError(f"Engine '{name}' detected but reported unavailable.")
            except ImportError as e:
                raise RuntimeError(
                    f"Engine '{name}' requested but its dependencies are missing: {e}"
                ) from e

    raise ValueError(
        f"Unknown engine '{engine_name}'. Available: {[n for n, _, _ in _ENGINE_REGISTRY]}"
    )
