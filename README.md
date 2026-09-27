# Indic Synthetic Manuscript Generator

A modular Python pipeline for synthesizing realistic historical Indic manuscript folios with synchronized ground-truth text annotations. Designed to generate training data for Indic Optical Character Recognition (OCR) and document analysis models.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/prathameshmowade/indic-synthetic-manuscripts)
[![Hugging Face Dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Dataset-blue)](https://huggingface.co/datasets/prathamesh1119/synthetic-indic-manuscripts)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)

> **Hugging Face Dataset Name:** [`prathamesh1119/synthetic-indic-manuscripts`](https://huggingface.co/datasets/prathamesh1119/synthetic-indic-manuscripts)  
> **GitHub Repository:** [`prathameshmowade/indic-synthetic-manuscripts`](https://github.com/prathameshmowade/indic-synthetic-manuscripts)

## Features

- **Script Support:** Generates folios for Devanagari, Modi, and Sharada scripts with OpenType conjunct and ligature shaping.
- **Substrate Synthesis:** Procedural generation of aged paper and palm-leaf backgrounds with paper fiber textures, water/ink stains, creases, and frayed deckle borders.
- **Layout Variations:** Supports single-block folios, multi-block commentary layouts (*root text + commentary*), and marginal annotations.
- **Ink & Styling:** Calligraphic handwriting variations, baseline-preserving slant, and dual-tone ink rendering (carbon black text with red highlighted section markers and numbers).
- **Strict Boundary Safety:** Automatic token wrapping and line clamping to ensure zero horizontal or vertical text overflow.
- **Synchronized Annotations:** Generates exact paired `.png` images and `.md` transcription files with indexed `metadata.jsonl` files.

---

## Repository Structure

```
├── fonts/                       # Indic fonts (Devanagari, Modi, Sharada)
├── pipeline/
│   ├── background.py            # Paper and palm-leaf texture generator
│   ├── corpus.py                # Text corpus loader and tokenizer
│   ├── layout.py                # Typography, layout engine, and ink renderer
│   └── dataset_builder.py       # Split manager and dataset organizer
├── dataset/                     # Generated manuscript dataset
├── generate.py                  # Main CLI generation script
├── hf_upload.py                 # Hugging Face Hub upload utility
├── requirements.txt             # Project dependencies
└── README.md
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/prathameshmowade/indic-synthetic-manuscripts.git
cd indic-synthetic-manuscripts
```

### 2. Setup virtual environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Linux / macOS:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Usage

### Generate Default Dataset
Generates 100 images per script (300 total) split into 85% train (85 images), 10% validation (10 images), and 5% test (5 images):

```bash
python generate.py
```

### CLI Options
```bash
python generate.py --help

Options:
  --scripts SCRIPTS [SCRIPTS ...]
                        Scripts to generate: devanagari, modi, sharada (default: all)
  --count COUNT         Images per script (default: 100)
  --train-ratio RATIO   Training set ratio (default: 0.85)
  --val-ratio RATIO     Validation set ratio (default: 0.10)
  --test-ratio RATIO    Test set ratio (default: 0.05)
  --output-dir DIR      Output folder path (default: dataset/)
  --seed SEED           Random seed (default: 42)
```

#### Custom Examples
```bash
# Generate only Devanagari folios:
python generate.py --scripts devanagari --count 50 --output-dir custom_dataset/

# Custom random seed:
python generate.py --seed 1234
```

---

## Dataset Format

Output files are organized by script and split:

```
dataset/
├── devanagari/
│   ├── train/
│   │   ├── Image_1.png
│   │   ├── Image_1.md
│   │   ├── ...
│   │   └── metadata.jsonl
│   ├── val/
│   └── test/
├── modi/
│   ├── train/
│   ├── val/
│   └── test/
└── sharada/
    ├── train/
    ├── val/
    └── test/
```

Each image file `Image_X.png` is paired with an exact ground-truth Markdown file `Image_X.md` containing the transcribed lines. `metadata.jsonl` provides Hugging Face `load_dataset` compatibility:

```json
{"file_name": "Image_1.png", "text": "...", "script": "devanagari", "split": "train", "material": "aged_paper", "layout": "standard", "annotation_file": "Image_1.md"}
```

---

## Hugging Face Dataset
 
- **Dataset Name:** `prathamesh1119/synthetic-indic-manuscripts`
- **Dataset URL:** [https://huggingface.co/datasets/prathamesh1119/synthetic-indic-manuscripts](https://huggingface.co/datasets/prathamesh1119/synthetic-indic-manuscripts)
- **Task Categories:** `image-to-text`, `optical-character-recognition`
- **Supported Scripts:** Devanagari (`sa`, `hi`), Modi (`mr`), Sharada (`sa`)
- **Total Folios:** 300 paired images & ground-truth annotations (85% train, 10% validation, 5% test)
 
### 1. Uploading to Hugging Face Hub
```bash
# Set your token or pass via --token
export HF_TOKEN="your_hf_write_token"

python hf_upload.py --repo-id prathamesh1119/synthetic-indic-manuscripts
```

### 2. Loading with the `datasets` Library
```python
from datasets import load_dataset

# Load the dataset directly from Hugging Face Hub
dataset = load_dataset("prathamesh1119/synthetic-indic-manuscripts", "devanagari")

# Access train, validation, or test folios
sample = dataset["train"][0]
print("Image file:", sample["file_name"])
print("Ground truth text:", sample["text"])
```

---

## License

This project is licensed under the Apache 2.0 License.
