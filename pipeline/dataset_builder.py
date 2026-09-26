import os
import json
import random
import cv2
from tqdm import tqdm

from pipeline.background import generate_manuscript_background
from pipeline.corpus import TextCorpusManager
from pipeline.layout import render_layout_on_background

def build_dataset(
    output_dir="dataset",
    scripts=("devanagari", "modi", "sharada"),
    count_per_script=100,
    train_ratio=0.85,
    val_ratio=0.10,
    test_ratio=0.05,
    seed=42
):
    """
    Generate synthetic Indic manuscript dataset across specified scripts with train/val/test splits.
    Outputs paired Image_X.png and Image_X.md files with metadata.jsonl index.
    """
    random.seed(seed)
    os.makedirs(output_dir, exist_ok=True)
    
    corpus_mgr = TextCorpusManager(".")
    
    num_train = int(round(count_per_script * train_ratio))
    num_val = int(round(count_per_script * val_ratio))
    num_test = count_per_script - num_train - num_val
    
    splits_spec = [
        ("train", num_train),
        ("val", num_val),
        ("test", num_test)
    ]
    
    print(f"\n[INFO] Starting dataset generation for: {', '.join(scripts)}")
    print(f"[INFO] Counts per script: Train={num_train}, Val={num_val}, Test={num_test} (Total: {count_per_script})")
    print(f"[INFO] Output path: {os.path.abspath(output_dir)}\n")
    
    dataset_summary = {}
    
    for script in scripts:
        dataset_summary[script] = {}
        script_dir = os.path.join(output_dir, script)
        os.makedirs(script_dir, exist_ok=True)
        
        sample_global_idx = 1
        
        for split_name, split_count in splits_spec:
            split_dir = os.path.join(script_dir, split_name)
            os.makedirs(split_dir, exist_ok=True)
            metadata_entries = []
            
            pbar = tqdm(total=split_count, desc=f"{script:<10} [{split_name}]")
            
            for _ in range(split_count):
                material = "palm_leaf" if random.random() < 0.25 else "aged_paper"
                
                layout_r = random.random()
                if layout_r < 0.65:
                    layout_type = "standard"
                elif layout_r < 0.85:
                    layout_type = "multi_block"
                else:
                    layout_type = "marginal_annotated"
                    
                slant_deg = random.uniform(8.0, 13.5)
                
                bg, _, _ = generate_manuscript_background(1024, 476, material=material)
                folio_img, gt_text = render_layout_on_background(
                    bg, script, corpus_mgr, layout_type=layout_type, slant_deg=slant_deg
                )
                
                img_filename = f"Image_{sample_global_idx}.png"
                md_filename = f"Image_{sample_global_idx}.md"
                
                img_path = os.path.join(split_dir, img_filename)
                md_path = os.path.join(split_dir, md_filename)
                
                cv2.imwrite(img_path, folio_img)
                
                with open(md_path, "w", encoding="utf-8") as f_md:
                    f_md.write(gt_text + "\n")
                    
                metadata_entries.append({
                    "file_name": img_filename,
                    "text": gt_text,
                    "script": script,
                    "split": split_name,
                    "material": material,
                    "layout": layout_type,
                    "annotation_file": md_filename
                })
                
                sample_global_idx += 1
                pbar.update(1)
                
            pbar.close()
            
            meta_path = os.path.join(split_dir, "metadata.jsonl")
            with open(meta_path, "w", encoding="utf-8") as f_meta:
                for entry in metadata_entries:
                    f_meta.write(json.dumps(entry, ensure_ascii=False) + "\n")
                    
            dataset_summary[script][split_name] = split_count
            
    print("\n[INFO] Generation complete:")
    for s, splits in dataset_summary.items():
        print(f"  {s:<12} -> " + ", ".join(f"{k}: {v}" for k, v in splits.items()))
    print()
    return dataset_summary
