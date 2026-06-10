---
title: Flashcard Generator SLM
emoji: 📚
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
python_version: 3.10.12
app_file: app.py
pinned: false
---

# Flashcard Generator SLM

A local-first flashcard generator for students built with a Small Language Model (Qwen2.5-3B), LlamaIndex, and Gradio. Accepts PDFs, handwritten note images, and reference images as input. Generates structured study cards and consolidated summaries exportable as PDF. Runs fully offline on CPU with 8GB RAM. No cloud APIs required.

## Features

- Upload PDFs, handwritten notes, or reference images
- Select specific page ranges from large PDFs
- Generate individual flash cards or consolidated summaries
- Export results as downloadable PDF
- Fully local — no data sent to external servers
- Supports Spanish and English queries

## Installation

```bash
pip install -r requirements.txt
python app.py
```

For Windows users: run `install.bat` once, then `run.bat` to start the app.

## Repository

Notebooks, evaluation results, and documentation:
https://github.com/DatosDeCiencia-LAT/flashcard-generator-slm

## Author

Juan Esteban Agudelo Ortiz — Founder and principal author