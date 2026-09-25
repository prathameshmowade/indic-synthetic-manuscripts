import os
import random
import re

class TextCorpusManager:
    """Manages raw text loading and sampling from Devanagari, Sharada, and Modi corpora."""
    
    def __init__(self, workspace_dir="."):
        self.workspace_dir = workspace_dir
        self.corpora = {}
        self.load_corpora()
        
    def load_corpora(self):
        files = {
            "devanagari": "devanagari_md.md",
            "sharada": "sharada_md.md",
            "modi": "Modi_md.md"
        }
        for script, filename in files.items():
            path = os.path.join(self.workspace_dir, filename)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = [line.strip() for line in f if line.strip()]
                self.corpora[script] = lines
                print(f"Loaded {len(lines):,} lines for {script}")
            else:
                print(f"Warning: {path} not found")

    def sample_text_passage(self, script_name, target_words=45, start_idx=None):
        """
        Sample a coherent chunk of text from the corpus.
        For Sharada, sanitizes ASCII hyphens and unwanted symbols.
        """
        lines = self.corpora.get(script_name.lower(), [])
        if not lines:
            return "नमः शिवाय ।"
            
        if start_idx is None:
            max_start = max(0, len(lines) - 20)
            start_idx = random.randint(0, max_start)
            
        collected_tokens = []
        curr_idx = start_idx
        
        while len(collected_tokens) < target_words and curr_idx < len(lines):
            line = lines[curr_idx]
            if script_name.lower() == "sharada":
                # Clean ASCII punctuation that doesn't exist in historical Sharada fonts
                for ch in ['-', '_', ';', ',', '.', '?', '!', '(', ')', '[', ']', '"', "'"]:
                    line = line.replace(ch, " ")
            elif script_name.lower() == "modi":
                for ch in ['-', '_', ';', ',', '.', '?', '!', '(', ')', '[', ']', '"', "'"]:
                    line = line.replace(ch, " ")
                
            tokens = line.split()
            collected_tokens.extend(tokens)
            curr_idx += 1
            
        # Return passage
        selected_tokens = collected_tokens[:target_words]
        return " ".join(selected_tokens)

    def sample_short_annotation(self, script_name):
        """Sample a short phrase for marginal note or commentary."""
        passage = self.sample_text_passage(script_name, target_words=random.randint(4, 8))
        return passage
