---
language:
- sa
- mr
- hi
license: apache-2.0
task_categories:
- image-to-text
- optical-character-recognition
tags:
- indic-ocr
- synthetic-manuscripts
- devanagari
- modi
- sharada
- historical-documents
size_categories:
- n<1K
configs:
- config_name: devanagari
  data_files:
  - split: train
    path: devanagari/train/*
  - split: validation
    path: devanagari/val/*
  - split: test
    path: devanagari/test/*
- config_name: modi
  data_files:
  - split: train
    path: modi/train/*
  - split: validation
    path: modi/val/*
  - split: test
    path: modi/test/*
- config_name: sharada
  data_files:
  - split: train
    path: sharada/train/*
  - split: validation
    path: sharada/val/*
  - split: test
    path: sharada/test/*
---

# Synthetic Indic Historical Manuscript Dataset

## Dataset Description
This dataset contains synthetic historical Indic manuscript folios paired with synchronized ground-truth text annotations (.md), formatted for training and evaluating Optical Character Recognition (OCR) and document understanding models.

### Key Characteristics:
* **Scripts Covered:** Devanagari, Modi, and Sharada.
* **Substrates:** Aged handmade paper and palm-leaf backgrounds with procedural aging, coffee/water stains, and deckle borders.
* **Layouts:** Single text block folios, multi-block commentary pages, and marginal annotations.
* **Typography:** Calligraphic handwriting variations, baseline-preserving slant, and dual-color ink (carbon black with red highlighted section markers).

## Dataset Structure
* **Total Images:** 300 folios (100 per script)
* **Splits per Script:**
  * Train: 85 images (85%)
  * Validation: 10 images (10%)
  * Test: 5 images (5%)

Each image (`Image_X.png`) is paired with an exact ground-truth Markdown annotation file (`Image_X.md`) and indexed in `metadata.jsonl`.
