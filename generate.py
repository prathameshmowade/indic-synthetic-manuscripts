#!/usr/bin/env python3
"""
Synthetic Indic Manuscript Generator.
Generates paired manuscript images and synchronized text annotations.
"""

import sys
import os
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from pipeline.dataset_builder import build_dataset

def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate synthetic Indic manuscript images with text annotations."
    )
    parser.add_argument(
        "--scripts",
        nargs="+",
        default=["devanagari", "modi", "sharada"],
        help="Scripts to generate: devanagari, modi, sharada (default: all three)"
    )
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="Number of images per script (default: 100)"
    )
    parser.add_argument(
        "--train-ratio",
        type=float,
        default=0.85,
        help="Train split ratio (default: 0.85)"
    )
    parser.add_argument(
        "--val-ratio",
        type=float,
        default=0.10,
        help="Validation split ratio (default: 0.10)"
    )
    parser.add_argument(
        "--test-ratio",
        type=float,
        default=0.05,
        help="Test split ratio (default: 0.05)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="dataset",
        help="Output directory path (default: dataset/)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    build_dataset(
        output_dir=args.output_dir,
        scripts=args.scripts,
        count_per_script=args.count,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed
    )

if __name__ == "__main__":
    main()
