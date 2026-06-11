---
title: Flashcard Generator SLM
emoji: 📚
colorFrom: green
colorTo: blue
sdk: gradio
sdk_version: 5.33.0
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

### System Requirements

Before starting, verify your computer has:

- **RAM**: At least 8GB of RAM (more is better)
- **Disk Space**: At least 3GB free space (for the AI model)
- **Processor**: Any modern CPU (no GPU required)
- **Operating System**: Windows, Mac, or Linux
- **Internet Connection**: For first-time model download

### Quick Start (Windows - Recommended for Beginners)

**No technical knowledge required!**

1. Download this repository as a ZIP file:
   - Click the green **"Code"** button on GitHub
   - Select **"Download ZIP"**
2. Extract the ZIP file to a folder on your computer
3. **Double-click `install.bat`** in the extracted folder
4. Wait for the installation to complete (may take 5-10 minutes on first run)
5. **Double-click `run.bat`** to start the app
6. Open your browser and go to: `http://localhost:7860`
7. You're ready to use the Flashcard Generator!

**That's it!** The `install.bat` script automatically:
- ✓ Downloads and installs Python (if needed)
- ✓ Installs all required packages
- ✓ Sets up everything for you

### Installation for Mac and Linux Users

#### Mac:

1. Download this repository as a ZIP file and extract it
2. Open **Terminal** (find it in Applications → Utilities)
3. Navigate to the extracted folder:
   ```bash
   cd /path/to/flashcard-generator-slm
   ```
4. Run the setup commands:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
5. Start the app:
   ```bash
   python app.py
   ```
6. Open your browser and go to: `http://localhost:7860`

#### Linux (Ubuntu/Debian):

1. Download this repository as a ZIP file and extract it
2. Open a terminal and navigate to the folder:
   ```bash
   cd /path/to/flashcard-generator-slm
   ```
3. Run the setup commands:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
4. Start the app:
   ```bash
   python app.py
   ```
5. Open your browser and go to: `http://localhost:7860`

### First Run (Downloading the AI Model)

On your first run, the app will download the AI model (~2GB) automatically. This:
- Only happens once
- May take 5-15 minutes depending on internet speed
- Is stored for future use (no re-download needed)

**Keep the command window open during this process.**

### Running the App (After Installation)

**Windows**: Simply double-click `run.bat`

**Mac/Linux**: Open terminal and run:
```bash
cd /path/to/flashcard-generator-slm
source .venv/bin/activate
python app.py
```

Then open `http://localhost:7860` in your browser.

### Troubleshooting

**Error: "Python is not recognized"** (Windows):
- The `install.bat` should install Python for you
- If you see this error, try running `install.bat` again
- If it persists, download Python manually from [python.org](https://www.python.org/downloads/)

**Browser page won't load**:
- Make sure the app is still running (the command window should still be open)
- Try a different browser (Chrome, Firefox, Safari, or Edge)
- Wait 30 seconds after seeing the "Running on..." message

**App is very slow on first run**:
- It's downloading the AI model (~2GB) — this is normal
- Ensure you have a stable internet connection
- Check you have at least 3GB free disk space

**"Out of memory" error**:
- Close other applications to free up RAM
- Restart your computer
- The app requires at least 8GB RAM to function

**Still having issues?**:
- Check the [GitHub repository](https://github.com/DatosDeCiencia-LAT/flashcard-generator-slm)
- Open an issue on GitHub with details about your error

## Repository

Notebooks, evaluation results, and documentation:
https://github.com/DatosDeCiencia-LAT/flashcard-generator-slm

## Author

Juan Esteban Agudelo Ortiz — Founder and principal author