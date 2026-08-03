"""
Realistic Human Contactless Fingerprint Dataset Generator (generate_test_dataset.py)

Generates 20 realistic human finger captures across 4 categories:
- test_dataset/good/    (5 x Good Quality Human Captures - PASS)
- test_dataset/blurry/  (5 x Blurry Human Captures - is_blurry=True)
- test_dataset/dark/    (5 x Dark/Bright Human Captures - too_dark/too_bright=True)
- test_dataset/glare/   (5 x Glare Human Captures - has_glare=True)
"""

import os
import cv2
import numpy as np

DATASET_DIR = "test_dataset"
IMAGE_DIRS = ["good", "blurry", "dark", "glare"]

def ensure_directories():
    os.makedirs(DATASET_DIR, exist_ok=True)
    for sub in IMAGE_DIRS:
        os.makedirs(os.path.join(DATASET_DIR, sub), exist_ok=True)
    
    os.makedirs("test_images", exist_ok=True)
    for sub in IMAGE_DIRS:
        os.makedirs(os.path.join("test_images", sub), exist_ok=True)

def generate_human_finger(
    width=500, height=500,
    pattern_type="whorl",
    skin_base=(150, 185, 235), # BGR skin tone
    bg_color=(35, 30, 25),    # Dark desktop environment BGR
    brightness_mult=1.0,
    ridge_contrast=1.0
) -> tuple:
    """Generates realistic human finger capture with skin shading, joint creases, and biometric ridge flow."""
    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[:, :] = bg_color
    
    # 1. Human Finger Silhouette Mask (index finger contour)
    mask = np.zeros((height, width), dtype=np.uint8)
    center_tip = (width // 2, 170)
    axes_tip = (100, 110)
    cv2.ellipse(mask, center_tip, axes_tip, 0, 180, 360, 255, -1)
    
    pts = np.array([
        [width // 2 - 100, 170],
        [width // 2 + 100, 170],
        [width // 2 + 115, height],
        [width // 2 - 115, height]
    ], dtype=np.int32)
    cv2.fillPoly(mask, [pts], 255)
    
    mask = cv2.GaussianBlur(mask, (7, 7), 0)
    _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    
    # 2. Skin Shading & Flexion Crease
    y_grid, x_grid = np.ogrid[:height, :width]
    dist_center = np.abs(x_grid - width // 2) / 115.0
    shading = np.clip(1.0 - (dist_center ** 2) * 0.35, 0.45, 1.0)
    
    skin = np.zeros_like(img)
    for c in range(3):
        skin[:, :, c] = np.clip(skin_base[c] * shading * brightness_mult, 0, 255).astype(np.uint8)
        
    # Joint creases
    crease_color = tuple(max(0, int(skin_base[c] * 0.45 * brightness_mult)) for c in range(3))
    cv2.ellipse(skin, (width // 2, 410), (90, 8), 0, 0, 180, crease_color, 3)
    cv2.ellipse(skin, (width // 2, 420), (95, 6), 0, 0, 180, crease_color, 2)
    
    # 3. Biometric Ridge Flow Pattern
    xc, yc = width // 2, 220
    if pattern_type == "whorl":
        r = np.sqrt(((x_grid - xc)/1.1)**2 + ((y_grid - yc)/1.4)**2)
        theta = np.arctan2(y_grid - yc, x_grid - xc)
        ridge_val = np.sin(r * 0.35 + theta * 2.0)
    elif pattern_type == "loop":
        rx = (x_grid - xc) / 1.0
        ry = (y_grid - yc) / 1.5
        r = np.sqrt(rx**2 + ry**2)
        ridge_val = np.sin(r * 0.35 + np.sin(rx * 0.08) * 3.0)
    else: # arch
        rx = (x_grid - xc) / 1.2
        ry = (y_grid - yc) / 1.3
        ridge_val = np.sin(ry * 0.35 + np.cos(rx * 0.05) * 4.0)

    ridge_pattern = ((ridge_val + 1.0) * 55.0 * ridge_contrast + 55.0).astype(np.uint8)
    
    finger_bgr = skin.copy()
    for c in range(3):
        finger_bgr[:, :, c] = np.clip(
            skin[:, :, c].astype(np.float32) * (0.50 + 0.50 * (ridge_pattern / 255.0)),
            0, 255
        ).astype(np.uint8)

    bg_mask = cv2.bitwise_not(mask)
    finger_part = cv2.bitwise_and(finger_bgr, finger_bgr, mask=mask)
    bg_part = cv2.bitwise_and(img, img, mask=bg_mask)
    
    combined = cv2.add(finger_part, bg_part)
    return combined, mask

def main():
    print("Generating realistic human contactless fingerprint captures (20 images)...")
    ensure_directories()

    patterns = ["whorl", "loop", "arch", "whorl", "loop"]

    # 1. Good Captures (PASS)
    for i in range(1, 6):
        pattern = patterns[i - 1]
        good_img, _ = generate_human_finger(pattern_type=pattern, skin_base=(150, 185, 235), brightness_mult=1.0)
        filename = f"good_0{i}.jpg"
        cv2.imwrite(os.path.join(DATASET_DIR, "good", filename), good_img)
        cv2.imwrite(os.path.join("test_images", "good", filename), good_img)

    # 2. Blurry Captures (is_blurry=True)
    for i in range(1, 6):
        pattern = patterns[i - 1]
        base, _ = generate_human_finger(pattern_type=pattern, skin_base=(150, 185, 235))
        blurry_img = cv2.GaussianBlur(base, (45, 45), 0)
        filename = f"blur_0{i}.jpg"
        cv2.imwrite(os.path.join(DATASET_DIR, "blurry", filename), blurry_img)
        cv2.imwrite(os.path.join("test_images", "blurry", filename), blurry_img)

    # 3. Dark / Bright Captures (too_dark=True / too_bright=True)
    for i in range(1, 6):
        pattern = patterns[i - 1]
        if i <= 3:
            # Underexposed dark: dim lighting with sharp ridge contrast (mean < 50, blur >= 10)
            dark_img, _ = generate_human_finger(
                pattern_type=pattern, skin_base=(75, 90, 115), bg_color=(15, 12, 10), brightness_mult=0.5, ridge_contrast=2.2
            )
            filename = f"dark_0{i}.jpg"
        else:
            # Overexposed bright: high intensity background & finger
            img_bg = np.zeros((500, 500, 3), dtype=np.uint8)
            img_bg[:, :] = [218, 218, 218]
            center_tip = (250, 170)
            mask = np.zeros((500, 500), dtype=np.uint8)
            cv2.ellipse(mask, center_tip, (100, 110), 0, 180, 360, 255, -1)
            pts = np.array([[150, 170], [350, 170], [365, 500], [135, 500]], dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)
            
            y_grid, x_grid = np.ogrid[:500, :500]
            sinusoid = np.sin((x_grid - 250)**2 / 300.0 + (y_grid - 220)**2 / 400.0)
            ridge_pattern = ((sinusoid + 1.0) * 20.0 + 195.0).astype(np.uint8)
            
            finger_part = np.zeros_like(img_bg)
            for c in range(3):
                finger_part[:, :, c] = ridge_pattern
            
            bg_mask = cv2.bitwise_not(mask)
            f_p = cv2.bitwise_and(finger_part, finger_part, mask=mask)
            b_p = cv2.bitwise_and(img_bg, img_bg, mask=bg_mask)
            dark_img = cv2.add(f_p, b_p)
            filename = f"dark_0{i}.jpg"

        cv2.imwrite(os.path.join(DATASET_DIR, "dark", filename), dark_img)
        cv2.imwrite(os.path.join("test_images", "dark", filename), dark_img)

    # 4. Glare Captures (has_glare=True)
    for i in range(1, 6):
        pattern = patterns[i - 1]
        base, mask = generate_human_finger(pattern_type=pattern, skin_base=(150, 185, 235))
        glare_img = base.copy()
        h, w = base.shape[:2]
        
        # Flash reflection highlight (>240 intensity over skin)
        cv2.circle(glare_img, (w // 2, 200), 75 + i * 5, (255, 255, 255), -1)
        filename = f"glare_0{i}.jpg"
        cv2.imwrite(os.path.join(DATASET_DIR, "glare", filename), glare_img)
        cv2.imwrite(os.path.join("test_images", "glare", filename), glare_img)

    print(f"Realistic human fingerprint dataset ready in '{DATASET_DIR}/'.")

if __name__ == "__main__":
    main()
