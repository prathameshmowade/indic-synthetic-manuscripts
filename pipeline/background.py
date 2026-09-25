import os
import math
import random
import numpy as np
import cv2

def generate_fractal_noise_2d(h, w, scale=64, octaves=4, persistence=0.5):
    """Generate 2D multi-octave fractal noise."""
    noise = np.zeros((h, w), dtype=np.float32)
    max_val = 0.0
    amp = 1.0
    freq = scale
    for _ in range(octaves):
        grid_h = max(2, int(h / freq))
        grid_w = max(2, int(w / freq))
        low_res = np.random.randn(grid_h, grid_w).astype(np.float32)
        upscaled = cv2.resize(low_res, (w, h), interpolation=cv2.INTER_CUBIC)
        noise += upscaled * amp
        max_val += amp
        amp *= persistence
        freq = max(2, freq / 2)
    return (noise / max_val)

def add_organic_liquid_stains(img_bgr, num_stains=4):
    """Add fluid and moisture stain blooms with edge gradients."""
    h, w, _ = img_bgr.shape
    stain_map = np.zeros((h, w), dtype=np.float32)
    
    for _ in range(num_stains):
        cx = random.randint(int(w * 0.1), int(w * 0.9))
        cy = random.randint(int(h * 0.1), int(h * 0.9))
        rx = random.randint(50, int(w * 0.30))
        ry = random.randint(35, int(h * 0.38))
        angle = random.uniform(0, 180)
        
        blob = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(blob, (cx, cy), (rx, ry), angle, 0, 360, 1.0, -1)
        
        noise = generate_fractal_noise_2d(h, w, scale=24, octaves=3)
        blob = blob * np.clip(0.85 + noise * 0.45, 0, 1)
        blob = cv2.GaussianBlur(blob, (31, 31), 0)
        
        grad_x = cv2.Sobel(blob, cv2.CV_32F, 1, 0, ksize=5)
        grad_y = cv2.Sobel(blob, cv2.CV_32F, 0, 1, ksize=5)
        grad = np.sqrt(grad_x**2 + grad_y**2)
        if grad.max() > 0:
            grad = grad / grad.max()
            
        stain = blob * 0.25 + grad * 0.75
        intensity = random.uniform(0.12, 0.28)
        stain_map += stain * intensity
        
    stain_map = np.clip(stain_map, 0, 1)
    
    # Warm sepia tone darkening
    for c, factor in enumerate([0.45, 0.30, 0.18]):
        img_bgr[:, :, c] = np.clip(img_bgr[:, :, c] * (1.0 - stain_map * factor) - stain_map * 16.0, 0, 255)
    return img_bgr

def add_paper_creases(img_bgr, num_creases=1):
    """Add paper fold lines with shadow and highlight offsets."""
    h, w, _ = img_bgr.shape
    for _ in range(num_creases):
        pt1 = (random.randint(0, int(w * 0.3)), 0)
        pt2 = (random.randint(int(w * 0.6), w), h)
        
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.line(mask, pt1, pt2, 255, thickness=2)
        
        dist = cv2.distanceTransform(255 - mask, cv2.DIST_L2, 5)
        shadow = np.exp(-((dist - 2.5)**2) / 12.0) * (dist < 10)
        highlight = np.exp(-((dist + 2.5)**2) / 12.0) * (dist < 10)
        
        for c in range(3):
            img_bgr[:, :, c] = np.clip(img_bgr[:, :, c] * (1.0 - shadow * 0.08) + highlight * 8.0, 0, 255)
    return img_bgr

def add_deckle_edges_and_vignette(img_bgr):
    """Add torn paper deckle borders and edge darkening."""
    h, w, _ = img_bgr.shape
    
    Y, X = np.ogrid[:h, :w]
    dist_x = np.minimum(X, w - 1 - X)
    dist_y = np.minimum(Y, h - 1 - Y)
    dist_border = np.minimum(dist_x, dist_y).astype(np.float32)
    
    roughness = generate_fractal_noise_2d(h, w, scale=20, octaves=4) * 25.0
    effective_dist = dist_border + roughness - 12.0
    
    vignette = np.clip(effective_dist / (min(h, w) * 0.22), 0, 1)
    vignette = np.power(vignette, 0.40)
    alpha = np.clip((effective_dist - 3.0) / 4.0, 0, 1)
    
    for c, factor in enumerate([0.45, 0.30, 0.18]):
        img_bgr[:, :, c] = img_bgr[:, :, c] * (0.65 + 0.35 * vignette)
        
    return img_bgr, alpha

def generate_manuscript_background(w=1024, h=476, material="aged_paper"):
    """
    Generate synthetic aged paper or palm-leaf substrate.
    Returns: (image_bgr, alpha_mask, safe_bounding_box)
    """
    if material == "palm_leaf":
        base_bgr = np.array([
            random.randint(90, 115),
            random.randint(140, 165),
            random.randint(180, 210)
        ], dtype=np.float32)
    else:
        # Warm aged paper base (sepia/tan)
        base_bgr = np.array([
            random.randint(135, 150),
            random.randint(175, 192),
            random.randint(205, 222)
        ], dtype=np.float32)
        
    img = np.ones((h, w, 3), dtype=np.float32) * base_bgr
    
    # 1. Base paper fiber noise
    fiber_noise = generate_fractal_noise_2d(h, w, scale=36, octaves=4)
    for c in range(3):
        img[:, :, c] += fiber_noise * random.uniform(14, 22)
        
    # 2. Grain direction
    if material == "palm_leaf":
        long_grain = np.random.randn(h, 1).repeat(w, axis=1).astype(np.float32)
        long_grain = cv2.GaussianBlur(long_grain, (1, 19), 0)
        for c in range(3):
            img[:, :, c] += long_grain * 18.0
    else:
        sieve = np.random.randn(h, w).astype(np.float32) * 3.5
        for c in range(3):
            img[:, :, c] += sieve
            
    # 3. Moisture stains
    img = add_organic_liquid_stains(img, num_stains=random.randint(3, 5))
    
    # 4. Creases
    img = add_paper_creases(img, num_creases=random.randint(1, 2))
    
    # 5. Vertical margin ruling lines
    margin_x = int(w * random.uniform(0.86, 0.89))
    has_margin_ruling = (material == "aged_paper") and (random.random() < 0.88)
    
    if has_margin_ruling:
        red_line_bgr = (random.randint(40, 65), random.randint(50, 75), random.randint(175, 210))
        line_noise = np.random.randn(h) * 0.35
        for y_i in range(12, h - 12):
            x_i = int(margin_x + line_noise[y_i])
            cv2.line(img, (x_i, y_i), (x_i, y_i + 1), red_line_bgr, thickness=random.choice([1, 2]))
            cv2.line(img, (x_i + 10, y_i), (x_i + 10, y_i + 1), red_line_bgr, thickness=1)
            
    # 6. Binding holes and stitches
    if material == "palm_leaf":
        for hole_x in [int(w * 0.28), int(w * 0.72)]:
            hole_y = h // 2 + random.randint(-4, 4)
            cv2.circle(img, (hole_x, hole_y), radius=random.randint(7, 10), color=(25, 35, 45), thickness=-1)
            cv2.circle(img, (hole_x, hole_y), radius=random.randint(11, 14), color=(45, 65, 85), thickness=2)
    else:
        if random.random() < 0.80:
            num_holes = random.randint(5, 7)
            for py in np.linspace(h * 0.12, h * 0.88, num_holes):
                hx = int(w * random.uniform(0.97, 0.982))
                hy = int(py) + random.randint(-2, 2)
                cv2.circle(img, (hx, hy), radius=2, color=(35, 45, 55), thickness=-1)
                cv2.line(img, (hx - 3, hy - 2), (hx + 3, hy + 2), (65, 80, 100), 1)

    # 7. Deckle borders and vignette
    img, alpha = add_deckle_edges_and_vignette(img)
    img = np.clip(img, 0, 255).astype(np.uint8)
    
    safe_bbox = {
        "x_min": int(w * 0.08),
        "y_min": int(h * 0.09),
        "x_max": margin_x - 22 if has_margin_ruling else int(w * 0.88),
        "y_max": int(h * 0.91)
    }
    
    return img, alpha, safe_bbox
