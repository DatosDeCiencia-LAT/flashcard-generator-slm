import base64
import io
from pathlib import Path

from PIL import Image
from weasyprint import HTML

from src.generation import ConsolidatedSummary, FlashCard


def image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def flashcard_to_html(card: FlashCard, reference_image: Image.Image = None) -> str:
    key_points_html = "".join(f"<li>{p}</li>" for p in card.key_points)
    examples_html   = "".join(f"<li>{e}</li>" for e in card.examples)

    if reference_image is not None:
        img_src  = image_to_base64(reference_image)
        img_html = f'<img src="{img_src}" style="max-width:100%; border-radius:8px;">'
    else:
        img_html = f'<p style="color:#888; font-style:italic;">{card.suggested_image}</p>'

    return f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #ffffff;
        }}
        .card {{
            display: flex;
            border: 2px solid #2ecc71;
            border-radius: 12px;
            padding: 20px;
            gap: 20px;
        }}
        .image-col {{
            width: 35%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .content-col {{
            width: 65%;
        }}
        h1 {{
            color: #2ecc71;
            font-size: 22px;
            margin-bottom: 8px;
        }}
        h3 {{
            color: #555;
            font-size: 14px;
            margin: 12px 0 4px 0;
        }}
        ul {{
            margin: 4px 0;
            padding-left: 20px;
        }}
        li {{
            font-size: 13px;
            margin-bottom: 3px;
        }}
        p {{
            font-size: 13px;
            line-height: 1.5;
        }}
    </style>
    </head>
    <body>
        <div class="card">
            <div class="image-col">{img_html}</div>
            <div class="content-col">
                <h1>{card.concept}</h1>
                <p>{card.definition}</p>
                <h3>Key Points</h3>
                <ul>{key_points_html}</ul>
                <h3>Examples</h3>
                <ul>{examples_html}</ul>
            </div>
        </div>
    </body>
    </html>
    """


def summary_to_html(summary: ConsolidatedSummary) -> str:
    concepts_html = "".join(
        f"<li><strong>{c['name']}:</strong> {c['description']}</li>"
        for c in summary.concepts
    )

    return f"""
    <html>
    <head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #ffffff;
        }}
        .summary {{
            border: 2px solid #3498db;
            border-radius: 12px;
            padding: 20px;
        }}
        h1 {{
            color: #3498db;
            font-size: 22px;
            margin-bottom: 8px;
        }}
        h3 {{
            color: #555;
            font-size: 14px;
            margin: 12px 0 4px 0;
        }}
        ul {{
            margin: 4px 0;
            padding-left: 20px;
        }}
        li {{
            font-size: 13px;
            margin-bottom: 6px;
        }}
        p {{
            font-size: 13px;
            line-height: 1.5;
        }}
    </style>
    </head>
    <body>
        <div class="summary">
            <h1>{summary.topic}</h1>
            <p>{summary.overview}</p>
            <h3>Concepts</h3>
            <ul>{concepts_html}</ul>
        </div>
    </body>
    </html>
    """


def export_to_pdf(
    content: "FlashCard | ConsolidatedSummary",
    output_path: Path,
    reference_image: Image.Image = None,
) -> Path:
    if isinstance(content, FlashCard):
        html = flashcard_to_html(content, reference_image)
    else:
        html = summary_to_html(content)

    HTML(string=html).write_pdf(str(output_path))
    return output_path
