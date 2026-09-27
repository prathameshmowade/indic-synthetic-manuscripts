#!/usr/bin/env python3
"""
Hugging Face Dataset Uploader
Helper script to publish the generated synthetic Indic manuscript dataset to the Hugging Face Hub.
"""

import os
import sys
import argparse
from huggingface_hub import HfApi, create_repo

HF_DATASET_CARD_TEMPLATE = """---
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
"""

def parse_args():
    parser = argparse.ArgumentParser(description="Upload dataset to Hugging Face Hub")
    parser.add_argument("--repo-id", type=str, required=True, help="Target Hugging Face repo ID, e.g., 'username/synthetic-indic-manuscripts'")
    parser.add_argument("--dataset-dir", type=str, default="dataset", help="Local directory containing generated dataset")
    parser.add_argument("--token", type=str, default=None, help="Hugging Face User Access Token (with write permission)")
    parser.add_argument("--private", action="store_true", help="Set repository to private")
    return parser.parse_args()

def main():
    args = parse_args()
    
    if not os.path.exists(args.dataset_dir):
        print(f"Error: Dataset directory '{args.dataset_dir}' does not exist. Run 'python generate.py' first.")
        sys.exit(1)
        
    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        print("Error: Hugging Face token required. Provide via --token <TOKEN> or set HF_TOKEN environment variable.")
        sys.exit(1)
        
    api = HfApi(token=token)
    
    print(f"Verifying repository: {args.repo_id}...")
    create_repo(
        repo_id=args.repo_id,
        repo_type="dataset",
        private=args.private,
        token=token,
        exist_ok=True
    )
    
    card_path = os.path.join(args.dataset_dir, "README.md")
    with open(card_path, "w", encoding="utf-8") as f:
        f.write(HF_DATASET_CARD_TEMPLATE)
    
    print(f"Uploading '{args.dataset_dir}' to https://huggingface.co/datasets/{args.repo_id}...")
    api.upload_folder(
        folder_path=args.dataset_dir,
        repo_id=args.repo_id,
        repo_type="dataset",
        commit_message="Add synthetic Indic manuscript dataset"
    )
    print(f"Dataset successfully uploaded: https://huggingface.co/datasets/{args.repo_id}")

if __name__ == "__main__":
    main()
