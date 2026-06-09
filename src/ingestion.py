import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

import fitz
from PIL import Image


class InputType(Enum):
    PDF           = "pdf"
    HANDWRITTEN   = "handwritten_image"
    REFERENCE_IMG = "reference_image"
    PLAIN_TEXT    = "plain_text"


@dataclass
class IngestedDocument:
    input_type       : InputType
    text             : str
    reference_images : list = field(default_factory=list)
    source_path      : Optional[Path] = None


class IngestionError(Exception):
    pass


_ocr_engine = None


def _get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        from paddleocr import PaddleOCR
        _ocr_engine = PaddleOCR(use_angle_cls=True, lang="es", show_log=False)
    return _ocr_engine


def extract_text_from_pdf(pdf_path: Path, min_block_chars: int = 20) -> str:
    doc = fitz.open(pdf_path)
    all_text = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("blocks")
        blocks_sorted = sorted(blocks, key=lambda b: (b[1], b[0]))

        page_text = []
        for block in blocks_sorted:
            text = block[4].strip()
            if len(text) < min_block_chars:
                continue
            text = re.sub(r"\s+", " ", text)
            page_text.append(text)

        if page_text:
            all_text.append(f"--- Page {page_num + 1} ---\n" + "\n\n".join(page_text))

    doc.close()
    return "\n\n".join(all_text)


def extract_text_from_image(image_path: Path, confidence_threshold: float = 0.7) -> str:
    ocr = _get_ocr_engine()
    result = ocr.ocr(str(image_path), cls=True)
    if not result or not result[0]:
        return ""
    lines = [
        line[1][0]
        for line in result[0]
        if line[1][1] >= confidence_threshold
    ]
    return "\n".join(lines)


def load_reference_image(image_path: Path, max_dimension: int = 800) -> Image.Image:
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    scale = min(1.0, max_dimension / max(w, h))
    if scale < 1.0:
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return img


def classify_input(file_path: Path, is_reference_image: bool = False) -> InputType:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return InputType.PDF
    if suffix in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
        if is_reference_image:
            return InputType.REFERENCE_IMG
        return InputType.HANDWRITTEN
    return InputType.PLAIN_TEXT


def ingest(file_path: Path, is_reference_image: bool = False) -> IngestedDocument:
    input_type = classify_input(file_path, is_reference_image)

    if input_type == InputType.PDF:
        text = extract_text_from_pdf(file_path)
        return IngestedDocument(input_type=input_type, text=text, source_path=file_path)

    if input_type == InputType.HANDWRITTEN:
        text = extract_text_from_image(file_path)
        return IngestedDocument(input_type=input_type, text=text, source_path=file_path)

    if input_type == InputType.REFERENCE_IMG:
        img = load_reference_image(file_path)
        return IngestedDocument(
            input_type=input_type,
            text="",
            reference_images=[img],
            source_path=file_path,
        )

    text = file_path.read_text(encoding="utf-8")
    return IngestedDocument(input_type=input_type, text=text, source_path=file_path)


def validate_ingestion(doc: IngestedDocument, min_chars: int = 50) -> None:
    text_bearing = {InputType.PDF, InputType.HANDWRITTEN, InputType.PLAIN_TEXT}
    if doc.input_type in text_bearing and len(doc.text) < min_chars:
        raise IngestionError(
            f"Extracted text too short ({len(doc.text)} chars). "
            f"Minimum required: {min_chars}."
        )
    if doc.input_type == InputType.REFERENCE_IMG and not doc.reference_images:
        raise IngestionError("No reference images found in ingested document.")
