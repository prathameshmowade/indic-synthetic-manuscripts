import os
import math
import random
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

SCRIPT_FONTS = {
    "devanagari": [
        "fonts/Kalam-Regular.ttf",
        "fonts/Kalam-Bold.ttf",
        "fonts/Amita-Regular.ttf"
    ],
    "modi": [
        "fonts/NotoSansModi-Regular.ttf"
    ],
    "sharada": [
        "fonts/NotoSansSharada-Regular.ttf"
    ]
}

def get_font_for_script(script_name, font_size):
    """Load appropriate font for given Indic script."""
    fonts = SCRIPT_FONTS.get(script_name.lower(), SCRIPT_FONTS["devanagari"])
    font_path = random.choice(fonts)
    return ImageFont.truetype(font_path, font_size), font_path

def wrap_text_to_lines(words, font, max_width):
    """
    Wrap words into lines strictly within max_width using Pillow text measurements.
    Returns list of lines (list of (word, is_highlighted) tuples) and plain text lines.
    """
    lines = []
    current_line = []
    current_text = ""
    
    # Dummy image for textbbox
    dummy_draw = ImageDraw.Draw(Image.new('RGB', (10, 10)))
    
    for word_info in words:
        word = word_info["text"]
        test_text = current_text + (" " if current_text else "") + word
        bbox = dummy_draw.textbbox((0, 0), test_text, font=font)
        line_w = bbox[2] - bbox[0]
        
        if line_w <= max_width:
            current_line.append(word_info)
            current_text = test_text
        else:
            if current_line:
                lines.append(current_line)
            current_line = [word_info]
            current_text = word
            
    if current_line:
        lines.append(current_line)
        
    return lines

def prepare_words_with_rubrication(text_corpus, script_name):
    """
    Split text into words and selectively mark certain tokens for rubrication (red ink),
    mimicking authentic historical manuscript practice (e.g. verse numbers, colophons, key words).
    """
    # Clean text into words
    tokens = text_corpus.split()
    words_info = []
    
    in_red_run = False
    run_len = 0
    
    for token in tokens:
        # Punctuation / number markers often rubricated
        is_verse_marker = any(m in token for m in ['।', '॥', '०', '१', '२', '३', '४', '५', '६', '७', '८', '९', '𑇅', '𑇆'])
        
        # Chance to start a rubricated run
        if not in_red_run and random.random() < 0.12:
            in_red_run = True
            run_len = random.randint(1, 4)
            
        is_highlighted = False
        if in_red_run:
            is_highlighted = True
            run_len -= 1
            if run_len <= 0:
                in_red_run = False
        elif is_verse_marker and random.random() < 0.35:
            is_highlighted = True
            
        words_info.append({
            "text": token,
            "highlight": is_highlighted
        })
        
    return words_info

def render_manuscript_text(bg_bgr, text_lines, font, bbox, slant_angle=12.0):
    """
    Renders calligraphic manuscript text onto background with:
    - Italic / calligraphic slant (shear transform)
    - Baseline waviness & natural hand jitter
    - Red / vermilion rubrication on marked words
    - Capillary ink bleeding & fiber absorption
    - Ground-truth lines returned for exact .md synchronization
    """
    h_bg, w_bg, _ = bg_bgr.shape
    
    # Colors
    # Primary ink: lampblack/carbon with slight warmth BGR
    black_ink_bgr = np.array([random.randint(28, 42), random.randint(28, 42), random.randint(30, 48)], dtype=np.float32)
    # Rubrication: cinnabar/vermilion hingula BGR
    red_ink_bgr = np.array([random.randint(35, 55), random.randint(50, 75), random.randint(175, 215)], dtype=np.float32)
    
    x_min, y_min = bbox["x_min"], bbox["y_min"]
    x_max, y_max = bbox["x_max"], bbox["y_max"]
    available_h = y_max - y_min
    
    # Calculate line height
    num_lines = len(text_lines)
    line_spacing = max(font.size + 10, int(available_h / max(1, num_lines)))
    
    # Create high-res text overlay image (RGBA)
    text_img = Image.new("RGBA", (w_bg, h_bg), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_img)
    
    rendered_ground_truth_lines = []
    
    curr_y = y_min + 5
    for l_idx, line in enumerate(text_lines):
        if curr_y + font.size > y_max:
            break # Avoid vertical overflow
            
        # Subtle baseline waviness across the line (human hand curve)
        wave_freq = random.uniform(0.005, 0.015)
        wave_phase = random.uniform(0, 2 * math.pi)
        wave_amp = random.uniform(1.0, 2.5)
        
        curr_x = x_min + random.randint(0, 8) # slight organic left margin jitter
        line_text_parts = []
        
        for w_info in line:
            w_text = w_info["text"]
            is_hl = w_info["highlight"]
            color_rgba = (int(red_ink_bgr[2]), int(red_ink_bgr[1]), int(red_ink_bgr[0]), 240) if is_hl else \
                         (int(black_ink_bgr[2]), int(black_ink_bgr[1]), int(black_ink_bgr[0]), 240)
            
            # Local baseline offset
            y_offset = wave_amp * math.sin(wave_freq * curr_x + wave_phase) + random.uniform(-0.5, 0.5)
            draw.text((curr_x, curr_y + y_offset), w_text, font=font, fill=color_rgba)
            
            w_bbox = draw.textbbox((curr_x, curr_y + y_offset), w_text, font=font)
            word_w = w_bbox[2] - w_bbox[0]
            space_bbox = draw.textbbox((0, 0), " ", font=font)
            space_w = space_bbox[2] - space_bbox[0]
            curr_x += word_w + space_w
            
            line_text_parts.append(w_text)
            
        rendered_ground_truth_lines.append(" ".join(line_text_parts))
        curr_y += line_spacing
        
    # Apply affine shear to simulate calligraphic slant if angle > 0
    text_arr = np.array(text_img)
    if abs(slant_angle) > 0.1:
        # Shear matrix: x' = x - tan(angle) * (y - y_mid)
        shear_rad = math.radians(slant_angle)
        tan_val = math.tan(shear_rad)
        M = np.float32([
            [1, -tan_val, tan_val * (h_bg / 2)],
            [0, 1, 0]
        ])
        text_arr = cv2.warpAffine(text_arr, M, (w_bg, h_bg), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
        
    # Separate ink color and alpha
    ink_rgb = text_arr[:, :, :3]
    ink_bgr = ink_rgb[:, :, ::-1].astype(np.float32)
    ink_alpha = (text_arr[:, :, 3].astype(np.float32) / 255.0)
    
    # Authentic ink simulation:
    # 1. Subtle ink bleed into fibers (Gaussian blur on ink alpha)
    bleed_alpha = cv2.GaussianBlur(ink_alpha, (3, 3), 0.5)
    
    # 2. Multiply blend with paper texture so paper grain shows through ink
    out_bgr = bg_bgr.astype(np.float32).copy()
    
    # Paper luminance for modulation
    gray_bg = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    grain_factor = np.clip(0.85 + 0.15 * gray_bg, 0.7, 1.0)
    
    # Blend: out = bg * (1 - alpha) + (ink * grain) * alpha
    for c in range(3):
        effective_ink = ink_bgr[:, :, c] * grain_factor
        out_bgr[:, :, c] = out_bgr[:, :, c] * (1.0 - bleed_alpha) + effective_ink * bleed_alpha
        
    out_bgr = np.clip(out_bgr, 0, 255).astype(np.uint8)
    ground_truth_text = "\n".join(rendered_ground_truth_lines)
    
    return out_bgr, ground_truth_text

if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from pipeline.background import generate_handmade_paper_background
    
    bg, alpha, bbox = generate_handmade_paper_background(1024, 476, style="aged_paper")
    
    # Sample devanagari test
    sample_text = """लक्षण। अपूर्व असे परियेसा ।८। ऋषि म्हणे रायासी। पुत्रभविष्य पुससी। ऐकोनि दुःख पावसी। कवणेपरी सांगावे ।९। राव विनवी तये वेळी। निरोपावे सकळी। उपाय करिसी तात्काळी। दुःखावेगळा तूचि करिसी ।१०। ऐकोनिया ऋषीश्वर। सांगता झाला विस्तार। ऐक राजा तुझा कुमार। बारा वर्षे आयुष्य असे ।११। तया बारा वर्षात। राहिले असती दिवस सात। आठवे दिवसी येईल मृत्यु। तुझ्या पुत्रासी परियेसा ।१२। ऐकोनि ऋषीचे वचन। राजा मूर्च्छित जाहला तत्क्षण। करिता"""
    
    font, font_path = get_font_for_script("devanagari", font_size=24)
    words_info = prepare_words_with_rubrication(sample_text, "devanagari")
    max_w = bbox["x_max"] - bbox["x_min"]
    lines = wrap_text_to_lines(words_info, font, max_w)
    
    rendered_img, gt_md = render_manuscript_text(bg, lines, font, bbox, slant_angle=12.0)
    cv2.imwrite("test_outputs/test_rendered_manuscript.png", rendered_img)
    with open("test_outputs/test_rendered_manuscript.md", "w", encoding="utf-8") as f:
        f.write(gt_md)
        
    print("Saved test_outputs/test_rendered_manuscript.png and .md")
    print("Ground truth output preview:\n", gt_md)
