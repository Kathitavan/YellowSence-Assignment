"""
Contactless Fingerprint Quality Assessment Pipeline (quality_assessment.py)
CORE LAYER — Reference Implementation for Assignment 4
"""

import time
import cv2
import numpy as np
from typing import Union, Dict, Any, Optional

DEFAULT_THRESHOLDS = {
    "blur_min": 10.0,
    "brightness_min": 50.0,
    "brightness_max": 210.0,
    "glare_max_ratio": 0.05,
    "roi_min_ratio": 0.15,
    "ridge_min_score": 15.0,
    "composite_pass_score": 60.0
}

def load_image(image_input: Union[str, np.ndarray]) -> np.ndarray:
    """Loads an image from a file path string or validates a numpy array."""
    if isinstance(image_input, str):
        img = cv2.imread(image_input)
        if img is None:
            raise ValueError(f"Could not load image from file path: {image_input}")
        return img
    elif isinstance(image_input, np.ndarray):
        if image_input.size == 0:
            raise ValueError("Input numpy array is empty.")
        return image_input.copy()
    else:
        raise ValueError("Image input must be a valid file path string or numpy ndarray.")

def check_blur(image_bgr: np.ndarray, threshold: float = 10.0) -> Dict[str, Any]:
    """1. Blur Detection using Laplacian Variance (threshold = 10.0)."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    is_blurry = blur_score < threshold
    return {
        "blur_score": round(blur_score, 2),
        "is_blurry": is_blurry
    }

def check_brightness(image_bgr: np.ndarray, min_thresh: float = 50.0, max_thresh: float = 210.0) -> Dict[str, Any]:
    """2. Brightness Check using Grayscale Mean Intensity (range = [50.0, 210.0])."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    brightness = float(np.mean(gray))
    too_dark = brightness < min_thresh
    too_bright = brightness > max_thresh
    return {
        "brightness": round(brightness, 2),
        "too_dark": too_dark,
        "too_bright": too_bright
    }

def check_glare(image_bgr: np.ndarray, max_glare_ratio: float = 0.05) -> Dict[str, Any]:
    """3. Glare Detection using overexposed pixel ratio (> 240 intensity)."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    overexposed_pixels = np.sum(gray > 240)
    glare_fraction = float(overexposed_pixels / gray.size)
    has_glare = glare_fraction > max_glare_ratio
    return {
        "glare_fraction": round(glare_fraction, 4),
        "has_glare": has_glare
    }

def check_roi_completeness(image_bgr: np.ndarray, min_roi_ratio: float = 0.15) -> Dict[str, Any]:
    """4. ROI Completeness using Otsu binarization filter."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, otsu_mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    roi_pixels = np.sum(otsu_mask > 0)
    roi_fraction = float(roi_pixels / otsu_mask.size)
    roi_complete = roi_fraction >= min_roi_ratio
    return {
        "roi_fraction": round(roi_fraction, 4),
        "roi_complete": roi_complete,
        "mask": otsu_mask
    }

def check_ridge_clarity(image_bgr: np.ndarray, threshold: float = 15.0) -> Dict[str, Any]:
    """5. Ridge Clarity using 2D Gabor kernel convolution."""
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    g_kernel = cv2.getGaborKernel((21, 21), sigma=5.0, theta=np.pi/4, lambd=10.0, gamma=0.5, psi=0, ktype=cv2.CV_64F)
    filtered = cv2.filter2D(gray, cv2.CV_64F, g_kernel)
    ridge_score = float(np.var(filtered)) / 100.0
    ridges_clear = ridge_score >= threshold
    
    gabor_vis = cv2.normalize(np.abs(filtered), None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return {
        "ridge_score": round(ridge_score, 2),
        "ridges_clear": ridges_clear,
        "gabor_vis": gabor_vis
    }

def get_pipeline_preview_tracks(image_bgr: np.ndarray) -> Dict[str, np.ndarray]:
    """Generates 5 transformation matrices for presentation layer previews."""
    orig_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY) if len(image_bgr.shape) == 3 else image_bgr
    gray_3ch = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    
    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    sobel_mag = np.sqrt(sobel_x**2 + sobel_y**2)
    sobel_norm = cv2.normalize(sobel_mag, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    sobel_3ch = cv2.applyColorMap(sobel_norm, cv2.COLORMAP_VIRIDIS)
    sobel_3ch = cv2.cvtColor(sobel_3ch, cv2.COLOR_BGR2RGB)

    roi_res = check_roi_completeness(image_bgr)
    mask = roi_res.get("mask", np.zeros_like(gray))
    mask_3ch = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)

    ridge_res = check_ridge_clarity(image_bgr)
    gabor_vis = ridge_res.get("gabor_vis", np.zeros_like(gray))
    gabor_colored = cv2.applyColorMap(gabor_vis, cv2.COLORMAP_VIRIDIS)
    gabor_3ch = cv2.cvtColor(gabor_colored, cv2.COLOR_BGR2RGB)

    return {
        "Original Capture": orig_rgb,
        "Grayscale Mapping": gray_3ch,
        "Sobel Edge Map": sobel_3ch,
        "Otsu ROI Mask": mask_3ch,
        "Gabor Ridge Map": gabor_3ch
    }

def quality_gate(image_path_or_array: Union[str, np.ndarray], thresholds: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Master quality coordinator evaluating 5 metrics and returning structured payload."""
    cfg = DEFAULT_THRESHOLDS.copy()
    if thresholds:
        cfg.update(thresholds)

    image_bgr = load_image(image_path_or_array)

    t0 = time.perf_counter()
    blur_res = check_blur(image_bgr, threshold=cfg["blur_min"])
    t_blur = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    bright_res = check_brightness(image_bgr, min_thresh=cfg["brightness_min"], max_thresh=cfg["brightness_max"])
    t_bright = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    glare_res = check_glare(image_bgr, max_glare_ratio=cfg["glare_max_ratio"])
    t_glare = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    roi_res = check_roi_completeness(image_bgr, min_roi_ratio=cfg["roi_min_ratio"])
    _mask = roi_res.pop("mask", None)
    t_roi = (time.perf_counter() - t0) * 1000.0

    t0 = time.perf_counter()
    ridge_res = check_ridge_clarity(image_bgr, threshold=cfg["ridge_min_score"])
    _gabor = ridge_res.pop("gabor_vis", None)
    t_ridge = (time.perf_counter() - t0) * 1000.0

    t_total = t_blur + t_bright + t_glare + t_roi + t_ridge

    # Reference Divisors & Normalization
    n_blur   = min(1.0, blur_res["blur_score"] / 50.0)
    n_bright = max(0.0, 1.0 - abs(bright_res["brightness"] - 128.0) / 128.0)
    n_glare  = max(0.0, 1.0 - (glare_res["glare_fraction"] / 0.05))
    n_roi    = min(1.0, roi_res["roi_fraction"] / 0.35)
    n_ridge  = min(1.0, ridge_res["ridge_score"] / 30.0)

    composite_score = round((0.25*n_blur + 0.15*n_bright + 0.15*n_glare + 0.20*n_roi + 0.25*n_ridge) * 100.0, 1)

    has_hard_failure = (
        blur_res["is_blurry"] or
        bright_res["too_dark"] or
        bright_res["too_bright"] or
        glare_res["has_glare"] or
        (not roi_res["roi_complete"]) or
        (not ridge_res["ridges_clear"])
    )

    passed = (composite_score >= cfg["composite_pass_score"]) and (not has_hard_failure)

    if blur_res["is_blurry"]:
        guidance = "Image is too blurry — hold steady and refocus"
    elif bright_res["too_dark"]:
        guidance = "Image is too dark — increase ambient lighting"
    elif bright_res["too_bright"]:
        guidance = "Image is too bright — reduce direct light"
    elif glare_res["has_glare"]:
        guidance = "Glare detected — tilt camera to avoid specular reflection"
    elif not roi_res["roi_complete"]:
        guidance = "Finger ROI incomplete — center fingertip in frame"
    elif not ridge_res["ridges_clear"]:
        guidance = "Ridge patterns unclear — ensure clean camera lens and sharp focus"
    else:
        guidance = "Good capture — ready for processing."

    return {
        "passed": passed,
        "composite_score": composite_score,
        "blur": blur_res,
        "brightness": bright_res,
        "glare": glare_res,
        "roi": roi_res,
        "ridge": ridge_res,
        "guidance": guidance,
        "timing_ms": {
            "blur": round(t_blur, 2),
            "brightness": round(t_bright, 2),
            "glare": round(t_glare, 2),
            "roi": round(t_roi, 2),
            "ridge": round(t_ridge, 2),
            "total": round(t_total, 2)
        },
        "normalized_scores": {
            "n_blur": round(n_blur * 100.0, 1),
            "n_bright": round(n_bright * 100.0, 1),
            "n_glare": round(n_glare * 100.0, 1),
            "n_roi": round(n_roi * 100.0, 1),
            "n_ridge": round(n_ridge * 100.0, 1)
        }
    }
