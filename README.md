# FingerVision • Contactless Fingerprint Quality Assessment System

![Python](https://img.shields.io/badge/Python-3.10%2B-2CF6C3?style=for-the-badge&logo=python&logoColor=08120F)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-7CF7D4?style=for-the-badge&logo=streamlit&logoColor=08120F)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-D7FF64?style=for-the-badge&logo=opencv&logoColor=08120F)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-3AFF9A?style=for-the-badge&logo=numpy&logoColor=08120F)
![Plotly](https://img.shields.io/badge/Plotly-5.17%2B-2CF6C3?style=for-the-badge&logo=plotly&logoColor=08120F)
![License](https://img.shields.io/badge/License-MIT-7CF7D4?style=for-the-badge)

Production-grade, enterprise contactless fingerprint quality control software platform developed for **Assignment 4: Contactless Fingerprint Quality Assessment & Scoring Pipeline**.

---

## 📐 System Architecture Diagram

```mermaid
flowchart TD
    subgraph Input ["📥 Capture Source"]
        A[Camera Photo / Upload] --> B[load_image]
    end

    subgraph Core ["⚡ Core Computer Vision Engine (quality_assessment.py)"]
        B --> C1["1. check_blur<br/>(Laplacian Variance σ²_Δ)"]
        B --> C2["2. check_brightness<br/>(Grayscale Mean Intensity μ)"]
        B --> C3["3. check_glare<br/>(Specular Ratio > 240)"]
        B --> C4["4. check_roi_completeness<br/>(Otsu Binarization Mask)"]
        B --> C5["5. check_ridge_clarity<br/>(2D Gabor Filter Energy / 100)"]
    end

    subgraph Logic ["🎯 Normalization & Composite Gate"]
        C1 --> D["Metric Normalization [0.0, 1.0]<br/>n_blur, n_bright, n_glare, n_roi, n_ridge"]
        C2 --> D
        C3 --> D
        C4 --> D
        C5 --> D
        D --> E["Composite Score Calculation<br/>(0.25 n_blur + 0.15 n_bright + 0.15 n_glare + 0.20 n_roi + 0.25 n_ridge) * 100"]
        E --> F{"Hard Boundary Check & Score >= 60.0?"}
    end

    subgraph Output ["📊 Operational Decision Payload"]
        F -->|Yes - All Passed| G["✅ PASSED<br/>'Good capture — ready for processing.'"]
        F -->|No - Any Fail| H["❌ REJECTED<br/>Priority Guidance Message"]
    end
```

---

## 🔬 Computer Vision Metric Pipeline

```mermaid
graph LR
    A["Raw BGR Capture"] --> B["Grayscale Conversion"]
    B --> C["Sobel Edge Mapping"]
    B --> D["Otsu ROI Mask Segmentation"]
    B --> E["2D Gabor Ridge Filtering"]
    
    C --> F["Feature Matrix Payload"]
    D --> F
    E --> F
    F --> G["Quality Decision Payload"]
```

---

## ⚡ Metric Specification & SLA Performance Budgets

| Metric | Algorithm / Operator | Default Threshold | Target SLA | Rejection Criteria |
| :--- | :--- | :---: | :---: | :--- |
| **Spatial Blur** | 2D Laplacian Operator Variance ($\sigma^2_{\Delta}$) | `10.0` | `< 10 ms` | Variance $< 10.0$ |
| **Luminance Balance** | Global Arithmetic Pixel Mean ($\mu$) | `[50.0, 210.0]` | `< 5 ms` | Mean $< 50.0$ (Dark) or $> 210.0$ (Bright) |
| **Specular Glare** | Overexposed Pixel Fraction ($I > 240$) | `0.05` | `< 10 ms` | Fraction $> 0.05$ |
| **ROI Completeness** | Gaussian Blur + Otsu Binarization Mask | `0.15` | `< 100 ms` | Foreground Ratio $< 0.15$ |
| **Ridge Clarity** | 2D Gabor Filter Bank ($21 \times 21, \theta=\pi/4, \lambda=10$) | `15.0` | `< 150 ms` | Response Variance $/ 100.0 < 15.0$ |
| **Total Pipeline** | Master Coordinator (`quality_gate()`) | `60.0` | **`< 300 ms`** | Composite $< 60.0$ or any Hard Failure |

---

## 📂 Project Directory Structure

```
contactless-fingerprint-qc/
├── quality_assessment.py     # CORE LAYER — 5 metrics + quality_gate()
├── quality_app.py            # PRESENTATION LAYER — Streamlit Master App
├── ui/                       # PRESENTATION MODULES
│   ├── __init__.py
│   ├── theme.py              # Emerald Glassmorphism CSS & Color Tokens
│   ├── components.py         # Base64 SVG Logo Engine, Timeline & Cards
│   └── charts.py             # Interactive Plotly Analytics Charts
├── test_quality.py           # CORE LAYER — Batch Verification Suite
├── generate_test_dataset.py  # Realistic Human Fingerprint Dataset Generator
├── generate_report.py        # ReportLab PDF Report Generator
├── requirements.txt        # Package Dependencies
├── README.md               # Visual Repository Documentation
├── test_dataset/           # 20 Realistic Human Fingerprint Captures
│   ├── good/               # 5 x Good Quality Human Captures (PASS)
│   ├── blurry/             # 5 x Blurry Human Captures (is_blurry=True)
│   ├── dark/               # 5 x Dark/Bright Human Captures (too_dark/too_bright=True)
│   └── glare/              # 5 x Glare Human Captures (has_glare=True)
└── report.pdf              # Assignment Technical Report (PDF)
```

---

## 🚀 Quick Start Guide

### 1. Clone Repository & Install Dependencies
```bash
git clone https://github.com/Kathitavan/YellowSence-Assignment.git
cd YellowSence-Assignment
pip install -r requirements.txt
```

### 2. Generate Human Test Captures
```bash
python generate_test_dataset.py
```

### 3. Run Automated Batch Evaluation
```bash
python test_quality.py
```

### 4. Launch Web Application Dashboard
```bash
streamlit run quality_app.py
```

---

## 📜 License & Compliance
Developed for **YellowSense Technologies Assignment 4**. Built strictly according to assignment reference code specifications.
