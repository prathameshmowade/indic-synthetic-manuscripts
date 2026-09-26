# Layout & Rendering Engine for Historical Folios
import os
import math
import random
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

SCRIPT_FONT_PATHS = {
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

def get_font_prop(script_name, size=20, bold=False):
    """Return font properties for the requested script."""
    fonts = SCRIPT_FONT_PATHS.get(script_name.lower(), SCRIPT_FONT_PATHS["devanagari"])
    if bold and len(fonts) > 1 and "Bold" in fonts[1]:
        fpath = fonts[1]
    else:
        fpath = fonts[0]
    return fm.FontProperties(fname=fpath, size=size)

def wrap_tokens_to_lines(tokens, font_prop, max_px_width, canvas_w=1024, canvas_h=476):
    """
    Wrap words into lines fitting strictly inside max_px_width.
    Uses cached Matplotlib renderer for fast text measurement.
    """
    fig = plt.figure(figsize=(canvas_w/100, canvas_h/100), dpi=100)
    fig.patch.set_alpha(0.0)
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    
    token_objs = []
    in_red_run = False
    run_rem = 0
    
    for t in tokens:
        is_verse_marker = any(m in t for m in ['।', '॥', '०', '१', '२', '३', '४', '५', '६', '७', '८', '९', '𑇅', '𑇆'])
        if not in_red_run and random.random() < 0.12:
            in_red_run = True
            run_rem = random.randint(1, 3)
            
        is_hl = False
        if in_red_run:
            is_hl = True
            run_rem -= 1
            if run_rem <= 0:
                in_red_run = False
        elif is_verse_marker and random.random() < 0.35:
            is_hl = True
            
        token_objs.append({"text": t, "highlight": is_hl})
        
    lines = []
    curr_line = []
    curr_str = ""
    
    for t_obj in token_objs:
        word = t_obj["text"]
        test_str = curr_str + (" " if curr_str else "") + word
        txt = plt.text(0, 0, test_str, fontproperties=font_prop)
        bbox = txt.get_window_extent(renderer=renderer)
        txt.remove()
        
        if bbox.width <= max_px_width:
            curr_line.append(t_obj)
            curr_str = test_str
        else:
            if curr_line:
                lines.append(curr_line)
            curr_line = [t_obj]
            curr_str = word
            
    if curr_line:
        lines.append(curr_line)
        
    plt.close(fig)
    return lines

def render_layout_on_background(bg_bgr, script_name, corpus_mgr, layout_type="standard", slant_deg=11.0):
    """
    Render text onto background according to selected layout type:
    - 'standard': Single central block with margins
    - 'multi_block': Main text with top/bottom commentary
    - 'marginal_annotated': Main text with marginal note
    """
    h, w, _ = bg_bgr.shape
    dpi = 100
    
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi)
    fig.patch.set_alpha(0.0)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis('off')
    ax.patch.set_alpha(0.0)
    
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    
    # Text colors
    black_ink = '#252220'
    red_ink = '#B33624'
    
    gt_lines = []
    
    if layout_type == "standard":
        font_size = 18 if script_name == "devanagari" else 17
        font_prop = get_font_prop(script_name, size=font_size)
        
        x_min_px = int(w * 0.08)
        x_max_px = int(w * 0.84)
        y_min_norm = 0.14
        y_max_norm = 0.88
        avail_h_norm = y_max_norm - y_min_norm
        
        max_px_width = x_max_px - x_min_px
        tokens = corpus_mgr.sample_text_passage(script_name, target_words=60).split()
        lines = wrap_tokens_to_lines(tokens, font_prop, max_px_width, canvas_w=w, canvas_h=h)
        lines = lines[:8]
        
        line_spacing_norm = avail_h_norm / max(1, len(lines))
        
        space_txt = ax.text(0, 0, " ", fontproperties=font_prop)
        space_px = space_txt.get_window_extent(renderer=renderer).width
        space_txt.remove()
        
        for l_idx, line in enumerate(lines):
            y_pos = y_max_norm - (l_idx * line_spacing_norm)
            cur_x_norm = x_min_px / w
            
            line_str_parts = []
            for t_obj in line:
                word = t_obj["text"]
                c = red_ink if t_obj["highlight"] else black_ink
                txt_obj = ax.text(cur_x_norm, y_pos, word, fontproperties=font_prop, color=c, va='top', ha='left')
                w_px = txt_obj.get_window_extent(renderer=renderer).width
                cur_x_norm += (w_px + space_px) / w
                line_str_parts.append(word)
                
            gt_lines.append(" ".join(line_str_parts))

    elif layout_type == "multi_block":
        font_main = get_font_prop(script_name, size=18, bold=True)
        font_comm = get_font_prop(script_name, size=13)
        
        space_comm = ax.text(0, 0, " ", fontproperties=font_comm).get_window_extent(renderer=renderer).width
        space_main = ax.text(0, 0, " ", fontproperties=font_main).get_window_extent(renderer=renderer).width
        
        top_tokens = corpus_mgr.sample_text_passage(script_name, target_words=22).split()
        top_lines = wrap_tokens_to_lines(top_tokens, font_comm, int(w * 0.74), canvas_w=w, canvas_h=h)[:2]
        
        main_tokens = corpus_mgr.sample_text_passage(script_name, target_words=32).split()
        main_lines = wrap_tokens_to_lines(main_tokens, font_main, int(w * 0.70), canvas_w=w, canvas_h=h)[:3]
        
        bot_tokens = corpus_mgr.sample_text_passage(script_name, target_words=25).split()
        bot_lines = wrap_tokens_to_lines(bot_tokens, font_comm, int(w * 0.74), canvas_w=w, canvas_h=h)[:2]
        
        curr_y = 0.90
        for line in top_lines:
            cur_x = 0.10
            line_strs = []
            for t in line:
                c = red_ink if t["highlight"] else black_ink
                txt = ax.text(cur_x, curr_y, t["text"], fontproperties=font_comm, color=c, va='top')
                w_px = txt.get_window_extent(renderer=renderer).width
                cur_x += (w_px + space_comm) / w
                line_strs.append(t["text"])
            gt_lines.append(" ".join(line_strs))
            curr_y -= 0.08
            
        curr_y -= 0.04
        for line in main_lines:
            cur_x = 0.12
            line_strs = []
            for t in line:
                c = red_ink if t["highlight"] else black_ink
                txt = ax.text(cur_x, curr_y, t["text"], fontproperties=font_main, color=c, va='top')
                w_px = txt.get_window_extent(renderer=renderer).width
                cur_x += (w_px + space_main) / w
                line_strs.append(t["text"])
            gt_lines.append(" ".join(line_strs))
            curr_y -= 0.13
            
        curr_y -= 0.03
        for line in bot_lines:
            cur_x = 0.10
            line_strs = []
            for t in line:
                c = red_ink if t["highlight"] else black_ink
                txt = ax.text(cur_x, curr_y, t["text"], fontproperties=font_comm, color=c, va='top')
                w_px = txt.get_window_extent(renderer=renderer).width
                cur_x += (w_px + space_comm) / w
                line_strs.append(t["text"])
            gt_lines.append(" ".join(line_strs))
            curr_y -= 0.08

    elif layout_type == "marginal_annotated":
        font_main = get_font_prop(script_name, size=18)
        font_margin = get_font_prop(script_name, size=12)
        space_main = ax.text(0, 0, " ", fontproperties=font_main).get_window_extent(renderer=renderer).width
        
        side_text = corpus_mgr.sample_short_annotation(script_name)
        ax.text(0.04, 0.94, side_text, fontproperties=font_margin, color=red_ink, va='top', ha='left')
        gt_lines.append(f"[{side_text}]")
        
        tokens = corpus_mgr.sample_text_passage(script_name, target_words=55).split()
        lines = wrap_tokens_to_lines(tokens, font_main, int(w * 0.76), canvas_w=w, canvas_h=h)[:7]
        
        curr_y = 0.86
        for line in lines:
            cur_x = 0.09
            line_strs = []
            for t in line:
                c = red_ink if t["highlight"] else black_ink
                txt = ax.text(cur_x, curr_y, t["text"], fontproperties=font_main, color=c, va='top')
                w_px = txt.get_window_extent(renderer=renderer).width
                cur_x += (w_px + space_main) / w
                line_strs.append(t["text"])
            gt_lines.append(" ".join(line_strs))
            curr_y -= 0.105

    fig.canvas.draw()
    rgba_buf = np.asarray(fig.canvas.buffer_rgba())
    plt.close(fig)
    
    # Baseline shear for handwriting slant
    if abs(slant_deg) > 0.1:
        rad = np.radians(slant_deg)
        tan_v = np.tan(rad)
        M = np.float32([
            [1, -tan_v, tan_v * (h * 0.5)],
            [0, 1, 0]
        ])
        sheared_text = cv2.warpAffine(rgba_buf, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0,0,0,0))
    else:
        sheared_text = rgba_buf
        
    text_bgr = sheared_text[:, :, :3][:, :, ::-1].astype(np.float32)
    text_alpha = (sheared_text[:, :, 3].astype(np.float32) / 255.0)
    
    # Ink bleed into fibers
    bleed_alpha = cv2.GaussianBlur(text_alpha, (3, 3), 0.45)
    
    # Paper grain texture modulation
    gray_bg = cv2.cvtColor(bg_bgr, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    grain_factor = np.clip(0.80 + 0.20 * gray_bg, 0.70, 1.0)
    
    out_bgr = bg_bgr.astype(np.float32).copy()
    for c in range(3):
        eff_ink = text_bgr[:, :, c] * grain_factor
        out_bgr[:, :, c] = out_bgr[:, :, c] * (1.0 - bleed_alpha) + eff_ink * bleed_alpha
        
    out_bgr = np.clip(out_bgr, 0, 255).astype(np.uint8)
    ground_truth_md = "\n".join(gt_lines)
    
    return out_bgr, ground_truth_md
