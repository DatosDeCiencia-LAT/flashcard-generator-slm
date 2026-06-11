import re
import tempfile
from pathlib import Path

import gradio as gr
from huggingface_hub import hf_hub_download

# ── Directory setup ────────────────────────────────────────────────────────────

BASE_DIR    = Path(".")
DATA_DIR    = BASE_DIR / "data"
MODELS_DIR  = DATA_DIR / "models"
INDEX_DIR   = DATA_DIR / "index"
UPLOADS_DIR = DATA_DIR / "uploads"
OUT_DIR     = DATA_DIR / "outputs"

for d in [MODELS_DIR, INDEX_DIR, UPLOADS_DIR, OUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ── Model download ─────────────────────────────────────────────────────────────

GENERATOR_PATH = MODELS_DIR / "qwen2.5-3b-instruct-q4_k_m.gguf"

if not GENERATOR_PATH.exists():
    print("Downloading Qwen2.5-3B-Instruct (~2GB)...")
    hf_hub_download(
        repo_id   = "Qwen/Qwen2.5-3B-Instruct-GGUF",
        filename  = "qwen2.5-3b-instruct-q4_k_m.gguf",
        local_dir = str(MODELS_DIR),
    )
    print("Download complete.")

# ── Pipeline initialization (runs once at startup) ─────────────────────────────

from src.indexing    import get_embed_model
from src.generation  import load_language_model

embed_model = get_embed_model()
llm         = load_language_model(GENERATOR_PATH)

# ── Helper imports (after model init to avoid circular import timing) ──────────

import fitz
from src.chunking    import fixed_size_chunking
from src.indexing    import load_or_build_index
from src.generation  import generate_flashcard
from src.export      import export_to_pdf


def process_inputs(
    pdf_file,
    notes_image,
    ref_image,
    page_start: int,
    page_end: int,
) -> tuple[str, list]:
    from PIL import Image as PILImage

    text_parts     = []
    reference_imgs = []

    if pdf_file is not None:
        doc         = fitz.open(pdf_file)
        total_pages = len(doc)
        start       = max(0, page_start - 1)
        end         = min(total_pages, page_end)

        sub = fitz.open()
        sub.insert_pdf(doc, from_page=start, to_page=end - 1)
        tmp_path = Path(tempfile.mktemp(suffix=".pdf"))
        sub.save(str(tmp_path))
        doc.close()

        from src.ingestion import extract_text_from_pdf
        text_parts.append(extract_text_from_pdf(tmp_path))
        tmp_path.unlink()

    if notes_image:
        from src.ingestion import extract_text_from_image
        for img_file in notes_image:
            text_parts.append(extract_text_from_image(Path(img_file)))

    if ref_image is not None:
        img = PILImage.open(ref_image).convert("RGB")
        reference_imgs.append(img)

    return "\n\n".join(text_parts), reference_imgs


def _safe_filename(topic: str) -> str:
    safe = re.sub(r"[^\w\s-]", "", topic)
    safe = re.sub(r"\s+", "_", safe.strip())
    return safe or "output"


MAX_ROWS = 8


def _parse_mode(raw: str) -> str:
    return "summary" if "sum" in raw.strip().lower() else "flashcard"


def generate_card_callback(
    pdf_file,
    notes_image,
    ref_image,
    page_start: int,
    page_end: int,
    visible,
    *topic_mode_pairs,
):
    topics = list(topic_mode_pairs[:MAX_ROWS])
    modes  = list(topic_mode_pairs[MAX_ROWS:])
    valid  = [
        (t.strip(), m)
        for t, m, v in zip(topics, modes, visible)
        if v and t.strip()
    ]
    if not valid:
        yield "Please add at least one topic.", None
        return

    try:
        yield "Extracting text from files...", None
        text, ref_imgs = process_inputs(pdf_file, notes_image, ref_image, page_start, page_end)

        if not text.strip():
            yield "No text could be extracted from the provided files.", None
            return

        yield "Chunking and indexing text...", None
        chunks = fixed_size_chunking(text)
        index  = load_or_build_index(
            chunks          = chunks,
            collection_name = f"session_{hash(text[:100])}",
            persist_dir     = INDEX_DIR / f"session_{hash(text[:100])}",
        )

        ref_image_pil = ref_imgs[0] if ref_imgs else None
        pdf_paths     = []
        total         = len(valid)

        for i, (topic, mode_raw) in enumerate(valid, 1):
            gradio_mode = _parse_mode(mode_raw)
            yield f"[{i}/{total}] Generating '{topic}' ({gradio_mode})...", pdf_paths or None

            result = generate_flashcard(
                query       = topic,
                index       = index,
                llm         = llm,
                embed_model = embed_model,
                mode        = gradio_mode,
            )

            pdf_out = OUT_DIR.resolve() / f"{_safe_filename(topic)}_{gradio_mode}.pdf"
            export_to_pdf(result, pdf_out, reference_image=ref_image_pil)
            pdf_paths.append(str(pdf_out))

            label = result.concept if gradio_mode == "flashcard" else result.topic
            yield f"[{i}/{total}] Done: {label}", pdf_paths

        yield f"All {total} generation(s) complete.", pdf_paths

    except Exception as e:
        yield f"Error: {e}", None


# ── Gradio interface ───────────────────────────────────────────────────────────

with gr.Blocks(title="Flashcard Generator") as demo:

    gr.Markdown("""
    # Flashcard Generator
    Generate structured study flash cards from your documents using a local AI model.
    Upload a PDF, handwritten notes, or a reference image, enter a topic, and get a
    downloadable flash card or consolidated summary.
    """)

    with gr.Tab("Generate"):
        with gr.Row():
            with gr.Column(scale=1):
                pdf_input   = gr.File(label="PDF document (optional)", file_types=[".pdf"])
                page_start  = gr.Slider(minimum=1, maximum=500, value=1,  step=1, label="First page")
                page_end    = gr.Slider(minimum=1, maximum=500, value=20, step=1, label="Last page")
                notes_input = gr.File(
                    label="Handwritten notes (optional, multiple allowed)",
                    file_types=[".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"],
                    file_count="multiple",
                )
                ref_input = gr.Image(label="Reference image (optional)", type="filepath")

                gr.Markdown("**Queries**")
                visible_state = gr.State([i < 3 for i in range(MAX_ROWS)])
                topic_boxes   = []
                mode_radios   = []
                del_btns      = []
                rows_ui       = []

                for i in range(MAX_ROWS):
                    with gr.Row(visible=(i < 3)) as row:
                        t = gr.Textbox(
                            placeholder="e.g. alcanos, photosynthesis...",
                            show_label=False,
                            scale=4,
                            min_width=200,
                        )
                        m = gr.Radio(
                            choices=["Flash Card", "Summary"],
                            value="Flash Card",
                            show_label=False,
                            scale=2,
                        )
                        d = gr.Button("✕", size="sm", scale=0, min_width=40)
                    topic_boxes.append(t)
                    mode_radios.append(m)
                    del_btns.append(d)
                    rows_ui.append(row)

                # Wire delete buttons after all rows exist so outputs list is complete
                for i, d in enumerate(del_btns):
                    def _on_delete(vis, idx=i):
                        new = list(vis)
                        new[idx] = False
                        return [gr.Row(visible=v) for v in new] + [new]
                    d.click(_on_delete, inputs=visible_state, outputs=rows_ui + [visible_state])

                add_btn = gr.Button("＋ Add query", size="sm")

                def _on_add(vis):
                    new = list(vis)
                    for j in range(len(new)):
                        if not new[j]:
                            new[j] = True
                            break
                    return [gr.Row(visible=v) for v in new] + [new]

                add_btn.click(_on_add, inputs=visible_state, outputs=rows_ui + [visible_state])

                with gr.Row():
                    submit_btn = gr.Button("Generate", variant="primary")
                    cancel_btn = gr.Button("Cancel", variant="stop")

            with gr.Column(scale=1):
                status_output = gr.Textbox(label="Status", interactive=False)
                pdf_output    = gr.File(label="Download PDFs", file_count="multiple")

        gen_event = submit_btn.click(
            fn      = generate_card_callback,
            inputs  = [pdf_input, notes_input, ref_input, page_start, page_end, visible_state] + topic_boxes + mode_radios,
            outputs = [status_output, pdf_output],
        )
        cancel_btn.click(fn=None, cancels=[gen_event])

    with gr.Tab("About"):
        gr.Markdown("""
        ## How to use

        1. Upload a PDF, handwritten notes image, or reference image (at least one required)
        2. If uploading a PDF, use the page sliders to select the relevant chapter
        3. Fill in the **Queries** — type a topic on the left, pick Flash Card or Summary on the right
        4. Use **＋ Add query** to add more rows, or **✕** to remove one
        5. Click Generate and download all PDFs


        > **Tip:** For best results, use specific single-concept queries like "amide",
        > "photosynthesis", or "Newton's first law" rather than broad queries like
        > "all strategies" or "overview of everything".
        
        ## Limitations
        - Generation takes 1-3 minutes on CPU
        - Equation recognition is not supported in this version
        - Context precision may be limited for complex multi-topic queries

        ## Model
        Running locally with Qwen2.5-3B-Instruct (GGUF Q4_K_M) via llama.cpp.
        No data is sent to any external server.
        """)


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
