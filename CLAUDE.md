# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Local-first flashcard generator for students. Accepts PDFs, handwritten note images, and reference images. Generates flash cards or multi-concept summaries exported as PDF. Runs entirely on CPU — no cloud APIs or GPU required.

**Stack:** Qwen2.5-3B-Instruct (GGUF via llama-cpp-python), LlamaIndex, ChromaDB, Gradio, WeasyPrint, PaddleOCR.

## Running the app

```bash
# Activate venv first
source .venv/bin/activate

# Launch Gradio UI at http://localhost:7860
python app.py
```

On first run, `app.py` automatically downloads the GGUF model (~2 GB) from HuggingFace into `data/models/`. Subsequent runs load from disk.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`torch` is installed CPU-only via the extra index URL in `requirements.txt`.

## Architecture: RAG pipeline

The pipeline flows linearly through five `src/` modules:

```
Input files
    └─ ingestion.py   – PDF text extraction (PyMuPDF), OCR (PaddleOCR), image loading
    └─ chunking.py    – SentenceSplitter, fixed 512-token chunks with 64-token overlap
    └─ indexing.py    – Embeds with paraphrase-multilingual-MiniLM-L12-v2, stores in ChromaDB
    └─ generation.py  – Retrieves top-3 chunks, calls Llama GGUF, parses JSON response
    └─ export.py      – Renders FlashCard/ConsolidatedSummary as HTML, writes PDF via WeasyPrint
```

`app.py` wires everything together in a Gradio UI and is the only entry point.

### Key data structures

- `FlashCard` (dataclass): `concept`, `definition`, `key_points`, `examples`, `suggested_image`
- `ConsolidatedSummary` (dataclass): `topic`, `overview`, `concepts` (list of `{name, description}`)
- Both are produced by `generate_flashcard()` in `src/generation.py` by selecting `mode="flashcard"` or `mode="summary"`.

### Model interaction

The LLM is prompted to return strict JSON only. `_clean_json_output()` strips markdown fences and trailing commas before `json.loads()`. On parse failure a second attempt appends a few-shot example to the system prompt.

### Index persistence

ChromaDB indexes are persisted under `data/index/session_<hash>/`. On load, the stored embedding model name is checked; if it differs from the current one the index is rebuilt. Each session keyed by a hash of the first 100 chars of the extracted text.

### Runtime directories

All created automatically by `app.py`:

| Path | Purpose |
|---|---|
| `data/models/` | GGUF model weights |
| `data/index/` | Persistent ChromaDB collections |
| `data/uploads/` | Temp files from Gradio uploads |
| `data/outputs/` | Generated PDFs |

## Notebooks

`notebooks/` contains exploratory development notebooks numbered in pipeline order (01–07). Notebook 07 (`07-gradio_app.ipynb`) tracks the Gradio app iteration. These are reference/exploration — production code lives in `src/` and `app.py`.
