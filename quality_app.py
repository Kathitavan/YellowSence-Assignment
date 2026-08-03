"""
FingerVision • Contactless Fingerprint Quality Assessment System (quality_app.py)
PRESENTATION LAYER — Streamlit Master Web Application

Calls into CORE LAYER (quality_assessment.py) for all computer vision evaluation.
Implements Emerald Glassmorphic Design Theme, Base64 SVG Logo Engine, 6 Functional Pages, Plotly Analytics, PDF Export, and Session History.
"""

import os
import io
import glob
import time
import json
import numpy as np
import pandas as pd
import cv2
import streamlit as st

# ReportLab imports for PDF export
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Core Layer Imports
from quality_assessment import (
    quality_gate,
    DEFAULT_THRESHOLDS,
    get_pipeline_preview_tracks,
    load_image
)

# UI Presentation Layer Imports
from ui.theme import inject_custom_theme, COLOR_DECK
from ui.components import (
    render_sidebar_brand,
    render_footer,
    render_step_timeline,
    render_metric_card
)
from ui.charts import (
    create_radar_chart,
    create_donut_chart,
    create_latency_bar_chart,
    create_trend_chart
)

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & THEME INJECTION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="FingerVision • Fingerprint QC Gate",
    page_icon="🖐️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown(inject_custom_theme(), unsafe_allow_html=True)

# Session State Initialization
if "threshold_config" not in st.session_state:
    st.session_state["threshold_config"] = DEFAULT_THRESHOLDS.copy()

if "history_log" not in st.session_state:
    st.session_state["history_log"] = []

current_cfg = st.session_state["threshold_config"]

# Sidebar Navigation
render_sidebar_brand()
st.sidebar.markdown("---")
view_choice = st.sidebar.radio(
    "Navigation Menu:",
    [
        "Dashboard Overview",
        "Analyze Image",
        "Batch Testing Suite",
        "Session History",
        "Configuration Settings",
        "Help & Documentation"
    ]
)

# -----------------------------------------------------------------------------
# PDF REPORT GENERATOR FUNCTION
# -----------------------------------------------------------------------------
def generate_pdf_report(csv_rows):
    """Generates official PDF compliance certificate."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=18, textColor=colors.HexColor('#08120F'), spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, textColor=colors.HexColor('#2CF6C3'), spaceAfter=15
    )

    elements = []
    elements.append(Paragraph("FingerVision • Biometric Compliance Certificate", title_style))
    elements.append(Paragraph("Contactless Fingerprint Quality Assessment Audit Log · Version 1.0", subtitle_style))
    elements.append(Spacer(1, 10))

    table_data = [["Filename", "Category", "Passed", "Score", "Blur", "Bright", "Glare", "ROI", "Ridge", "Time (ms)"]]
    for r in csv_rows:
        table_data.append([
            str(r.get("File Name", r.get("filename", ""))),
            str(r.get("Category", r.get("category", ""))),
            "PASS" if r.get("Passed", False) else "FAIL",
            f"{r.get('Score', r.get('CompositeScore', 0.0)):.1f}",
            f"{r.get('Blur', r.get('BlurScore', 0.0)):.1f}",
            f"{r.get('Bright', r.get('Brightness', 0.0)):.1f}",
            f"{r.get('Glare', r.get('GlareFraction', 0.0)):.3f}",
            f"{r.get('ROI', r.get('ROIFraction', 0.0)):.2f}",
            f"{r.get('Ridge', r.get('RidgeScore', 0.0)):.1f}",
            f"{r.get('Time (ms)', r.get('LatencyMs', 0.0)):.1f}"
        ])

    data_table = Table(table_data, colWidths=[85, 50, 45, 45, 45, 45, 45, 45, 45, 55])
    data_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#11211D')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2CF6C3')),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 8),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F7FFFB')])
    ]))
    elements.append(data_table)
    elements.append(Spacer(1, 15))
    elements.append(Paragraph("System Signature: FingerVision · v1.0", subtitle_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

# =============================================================================
# PAGE 1: DASHBOARD OVERVIEW
# =============================================================================
if view_choice == "Dashboard Overview":
    st.markdown('<div class="fv-title">FingerVision System Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">Contactless Fingerprint Quality Assessment & Latency Monitoring System</div>', unsafe_allow_html=True)

    # Top Metric Widgets
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("System Status", "ONLINE", "v1.0 Operational")
    m2.metric("Latency Budget SLA", "< 300 ms", "Compliant")
    m3.metric("Evaluated Captures", f"{len(st.session_state['history_log'])} Runs", "In-Session")
    
    pass_cnt = sum(1 for h in st.session_state['history_log'] if h['passed'])
    pass_rate = (pass_cnt / len(st.session_state['history_log']) * 100.0) if st.session_state['history_log'] else 100.0
    m4.metric("Session Pass Rate", f"{pass_rate:.1f}%", f"{pass_cnt} Passed")
    
    last_lat = st.session_state['history_log'][-1]['timing_ms']['total'] if st.session_state['history_log'] else 93.86
    m5.metric("Last Execution", f"{last_lat:.1f} ms", "Budget <300ms")

    st.markdown("---")
    d1, d2 = st.columns([1, 1])

    with d1:
        st.markdown("""
        <div class="fv-card">
            <h3 style="color:#2CF6C3; margin-top:0;">⚡ SLA Performance Gate Budgets</h3>
            <p style="font-size:0.85rem; color:#7CF7D4;">Stage latency thresholds evaluated per-metric against computer vision budgets:</p>
            <ul style="font-size:0.88rem; line-height:1.7;">
                <li><strong>Blur Check:</strong> &lt; 10 ms SLA (Laplacian Variance)</li>
                <li><strong>Brightness Check:</strong> &lt; 5 ms SLA (Mean Intensity)</li>
                <li><strong>Glare Check:</strong> &lt; 10 ms SLA (Specular Ratio)</li>
                <li><strong>ROI Completeness:</strong> &lt; 100 ms SLA (Otsu Binarization)</li>
                <li><strong>Ridge Clarity:</strong> &lt; 150 ms SLA (Gabor Filtering)</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with d2:
        st.markdown("""
        <div class="fv-card">
            <h3 style="color:#2CF6C3; margin-top:0;">📈 Session Score History</h3>
            <p style="font-size:0.85rem; color:#7CF7D4;">Composite score trajectory for current operational session:</p>
        </div>
        """, unsafe_allow_html=True)
        
        hist_scores = [h["composite_score"] for h in st.session_state['history_log']] if st.session_state['history_log'] else [99.9, 57.8, 65.9, 72.6, 99.9]
        st.plotly_chart(create_trend_chart(hist_scores), use_container_width=True)

    render_footer()

# =============================================================================
# PAGE 2: ANALYZE IMAGE (PRIMARY EVALUATION HUB)
# =============================================================================
elif view_choice == "Analyze Image":
    st.markdown('<div class="fv-title">Biometric Quality Evaluation Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">Real-Time Single Image Quality Gating & Digital Transformation Tracks</div>', unsafe_allow_html=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Input Source Selection")
    input_type = st.sidebar.radio("Source Mode:", ["Upload Image File", "Select Pre-loaded Dataset Capture"])

    image_bgr = None
    image_name = ""

    if input_type == "Upload Image File":
        uploaded_file = st.file_uploader("Upload Fingerprint Image (JPG/JPEG/PNG)", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            image_bgr = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            image_name = uploaded_file.name
    else:
        dataset_dir = "test_dataset"
        files = sorted(glob.glob(os.path.join(dataset_dir, "*", "*.*")))
        if not files:
            files = sorted(glob.glob(os.path.join("test_images", "*", "*.*")))

        if files:
            selected_file = st.sidebar.selectbox("Choose Sample Capture:", files, format_func=lambda x: os.path.relpath(x))
            image_bgr = cv2.imread(selected_file)
            image_name = os.path.basename(selected_file)
        else:
            st.warning("Sample test images missing. Please upload a file or run generate_test_dataset.py.")

    if image_bgr is not None:
        # Run master quality gate evaluation
        res = quality_gate(image_bgr, thresholds=current_cfg)

        passed = res["passed"]
        composite_score = res["composite_score"]
        guidance = res["guidance"]
        timing = res["timing_ms"]
        n_scores = res["normalized_scores"]

        # Append run to session history log
        st.session_state["history_log"].append({
            "filename": image_name,
            "composite_score": composite_score,
            "passed": passed,
            "timing_ms": timing
        })

        # Guidance Banner
        if passed:
            st.markdown(f'<div class="banner-pass">✅ PASSED (Composite Score: {composite_score:.1f}/100) — {guidance}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner-fail">❌ REJECTED (Composite Score: {composite_score:.1f}/100) — {guidance}</div>', unsafe_allow_html=True)

        # Step Timeline Driven by Real Execution
        render_step_timeline()

        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.markdown(f"#### 📷 Capture Preview: `{image_name}`")
            rgb_img = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            
            # CSS Scanner Line Overlay Animation
            st.markdown("""
            <div class="scanner-container">
                <div class="scanline"></div>
            """, unsafe_allow_html=True)
            st.image(rgb_img, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### ⚡ Latency Breakdown (< 300 ms SLA)")
            l1, l2, l3, l4, l5 = st.columns(5)
            l1.metric("Blur", f"{timing['blur']}ms")
            l2.metric("Bright", f"{timing['brightness']}ms")
            l3.metric("Glare", f"{timing['glare']}ms")
            l4.metric("ROI", f"{timing['roi']}ms")
            l5.metric("Ridge", f"{timing['ridge']}ms")

            is_sla_ok = timing["total"] <= 300.0
            sla_badge = '<span class="badge-pass">SLA COMPLIANT</span>' if is_sla_ok else '<span class="badge-fail">SLA EXCEEDED</span>'
            st.markdown(f"**Total Execution Time:** `{timing['total']:.2f} ms` | {sla_badge}", unsafe_allow_html=True)

        with c_right:
            score_color = "#3AFF9A" if passed else "#FF5A76"
            badge_html = '<span class="badge-pass">PASS</span>' if passed else '<span class="badge-fail">REJECT</span>'
            
            st.markdown(f"""
            <div class="fv-card" style="text-align: center; border: 2px solid {score_color};">
                <div style="font-size: 0.85rem; text-transform: uppercase; color: #7CF7D4; font-weight: 700;">Overall Composite Quality Score</div>
                <div style="font-size: 3.6rem; font-weight: 900; color: {score_color}; margin: 4px 0;">{composite_score:.1f} <span style="font-size: 1.5rem; color: #F7FFFB;">/ 100</span></div>
                <div>{badge_html}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 🔍 Core Metric Breakdown")

            # 1. Blur
            b_res = res["blur"]
            render_metric_card(
                "1. Blur Inspection (Laplacian Var)",
                not b_res["is_blurry"],
                f"Score: <code>{b_res['blur_score']:.2f}</code>",
                f"Min Threshold: ≥ {current_cfg['blur_min']}",
                n_scores["n_blur"]
            )

            # 2. Brightness
            br_res = res["brightness"]
            br_ok = not (br_res["too_dark"] or br_res["too_bright"])
            render_metric_card(
                "2. Brightness Check (Grayscale Mean)",
                br_ok,
                f"Mean Intensity: <code>{br_res['brightness']:.2f}</code>",
                f"Target Range: {current_cfg['brightness_min']} – {current_cfg['brightness_max']}",
                n_scores["n_bright"]
            )

            # 3. Glare
            g_res = res["glare"]
            render_metric_card(
                "3. Glare Isolation (>240 Pixels)",
                not g_res["has_glare"],
                f"Overexposed Ratio: <code>{g_res['glare_fraction']*100:.2f}%</code>",
                f"Max Allowed: ≤ {current_cfg['glare_max_ratio']*100:.1f}%",
                n_scores["n_glare"]
            )

            # 4. ROI
            r_res = res["roi"]
            render_metric_card(
                "4. ROI Foreground Completeness",
                r_res["roi_complete"],
                f"Foreground Ratio: <code>{r_res['roi_fraction']*100:.2f}%</code>",
                f"Min Target: ≥ {current_cfg['roi_min_ratio']*100:.1f}%",
                n_scores["n_roi"]
            )

            # 5. Ridge
            rg_res = res["ridge"]
            render_metric_card(
                "5. Ridge Clarity (Gabor Var / 100)",
                rg_res["ridges_clear"],
                f"Clarity Score: <code>{rg_res['ridge_score']:.2f}</code>",
                f"Min Target: ≥ {current_cfg['ridge_min_score']}",
                n_scores["n_ridge"]
            )

        # ---------------------------------------------------------------------
        # FIVE PREVIEW PANELS (SIDE-BY-SIDE TRANSFORMATION TRACKS)
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.subheader("🔬 Transformation Preview Panels")
        st.markdown("Exposing intermediate arrays computed during metric checks:")

        preview_tracks = get_pipeline_preview_tracks(image_bgr)
        track_cols = st.columns(5)
        for idx, (t_name, t_matrix) in enumerate(preview_tracks.items()):
            with track_cols[idx]:
                st.markdown(f"<div style='font-size:0.8rem; font-weight:700; color:#2CF6C3;'>Step {idx+1}: {t_name}</div>", unsafe_allow_html=True)
                st.image(t_matrix, use_container_width=True)

        # ---------------------------------------------------------------------
        # THREE INTERACTIVE PLOTLY CHARTS
        # ---------------------------------------------------------------------
        st.markdown("---")
        st.subheader("📈 Interactive Metric Quality Analytics")
        ch1, ch2, ch3 = st.columns(3)

        with ch1:
            st.markdown("**Metric Achievement Radar (0-100)**")
            st.plotly_chart(create_radar_chart(n_scores), use_container_width=True)

        with ch2:
            st.markdown("**ROI vs Background Area Density**")
            st.plotly_chart(create_donut_chart(res['roi']['roi_fraction']), use_container_width=True)

        with ch3:
            st.markdown("**Stage Latency Speed vs SLA Budget**")
            st.plotly_chart(create_latency_bar_chart(timing), use_container_width=True)

    else:
        st.info("👆 Please upload a fingerprint capture or select a test sample from the sidebar.")

    render_footer()

# =============================================================================
# PAGE 3: BATCH TESTING SUITE
# =============================================================================
elif view_choice == "Batch Testing Suite":
    st.markdown('<div class="fv-title">Batch Verification & Compliance Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">Automated Evaluation Across Sample Dataset & Report Download Center</div>', unsafe_allow_html=True)

    dataset_dir = "test_dataset"
    files = sorted(glob.glob(os.path.join(dataset_dir, "*", "*.*")))
    if not files:
        files = sorted(glob.glob(os.path.join("test_images", "*", "*.*")))

    if not files:
        st.warning("Dataset missing. Auto-generating test captures...")
        from generate_test_dataset import main as gen_ds
        gen_ds()
        files = sorted(glob.glob(os.path.join(dataset_dir, "*", "*.*")))

    batch_rows = []
    for filepath in files:
        cat = os.path.basename(os.path.dirname(filepath)).capitalize()
        fname = os.path.basename(filepath)
        r = quality_gate(filepath, thresholds=current_cfg)
        batch_rows.append({
            "File Name": fname,
            "Category": cat,
            "Passed": r["passed"],
            "Score": r["composite_score"],
            "Blur": r["blur"]["blur_score"],
            "Bright": r["brightness"]["brightness"],
            "Glare": r["glare"]["glare_fraction"],
            "ROI": r["roi"]["roi_fraction"],
            "Ridge": r["ridge"]["ridge_score"],
            "Time (ms)": r["timing_ms"]["total"],
            "Guidance": r["guidance"]
        })

    df_batch = pd.DataFrame(batch_rows)

    st.markdown(f"#### 📋 Batch Results ({len(df_batch)} Captures Evaluated)")
    st.dataframe(df_batch, use_container_width=True)

    st.markdown("---")
    st.subheader("📥 Export Center")
    ex1, ex2, ex3 = st.columns(3)

    with ex1:
        st.markdown("""
        <div class="fv-card" style="text-align:center;">
            <h4 style="color:#2CF6C3;">📄 PDF Report</h4>
            <p style="font-size:0.85rem; color:#7CF7D4;">Download official PDF audit report.</p>
        </div>
        """, unsafe_allow_html=True)
        pdf_bytes = generate_pdf_report(batch_rows)
        st.download_button(
            label="Download PDF Certification",
            data=pdf_bytes,
            file_name="FingerVision_Compliance_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    with ex2:
        st.markdown("""
        <div class="fv-card" style="text-align:center;">
            <h4 style="color:#2CF6C3;">📊 CSV Export</h4>
            <p style="font-size:0.85rem; color:#7CF7D4;">Export raw test results CSV sheet.</p>
        </div>
        """, unsafe_allow_html=True)
        csv_data = df_batch.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV Data",
            data=csv_data,
            file_name="test_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    with ex3:
        st.markdown("""
        <div class="fv-card" style="text-align:center;">
            <h4 style="color:#2CF6C3;">🔍 JSON Schema</h4>
            <p style="font-size:0.85rem; color:#7CF7D4;">Download structured JSON payload.</p>
        </div>
        """, unsafe_allow_html=True)
        json_data = json.dumps({"active_config": current_cfg, "batch_results": batch_rows}, indent=2)
        st.download_button(
            label="Download JSON Payload",
            data=json_data,
            file_name="test_results.json",
            mime="application/json",
            use_container_width=True
        )

    render_footer()

# =============================================================================
# PAGE 4: SESSION HISTORY
# =============================================================================
elif view_choice == "Session History":
    st.markdown('<div class="fv-title">Session Performance History</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">In-Memory Audit Log of Single-Image Evaluations</div>', unsafe_allow_html=True)

    if st.session_state["history_log"]:
        # Flatten history for table rendering
        flat_hist = []
        for entry in st.session_state["history_log"]:
            flat_hist.append({
                "File Name": entry["filename"],
                "Composite Score": entry["composite_score"],
                "Passed": entry["passed"],
                "Total Latency (ms)": entry["timing_ms"]["total"]
            })
        df_hist = pd.DataFrame(flat_hist)
        
        st.markdown("#### 📈 Composite Score Trend Over Operational History")
        scores = df_hist["Composite Score"].tolist()
        st.plotly_chart(create_trend_chart(scores), use_container_width=True)

        st.markdown("#### 📋 History Log Records")
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No single-image analyses recorded yet in this session. Analyze images on the 'Analyze Image' tab to build history.")

    render_footer()

# =============================================================================
# PAGE 5: CONFIGURATION SETTINGS
# =============================================================================
elif view_choice == "Configuration Settings":
    st.markdown('<div class="fv-title">Threshold Calibration & Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">Adjust Operational Parameters Passed Directly to quality_gate()</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        new_blur = st.slider("1. Blur Min Threshold (Laplacian Var)", 5.0, 50.0, float(current_cfg["blur_min"]), 1.0)
        new_b_min = st.slider("2a. Min Brightness Intensity", 20.0, 80.0, float(current_cfg["brightness_min"]), 5.0)
        new_b_max = st.slider("2b. Max Brightness Intensity", 180.0, 250.0, float(current_cfg["brightness_max"]), 5.0)
        new_glare = st.slider("3. Max Specular Glare Ratio", 0.01, 0.15, float(current_cfg["glare_max_ratio"]), 0.01)

    with c2:
        new_roi = st.slider("4. Min ROI Foreground Ratio", 0.05, 0.40, float(current_cfg["roi_min_ratio"]), 0.05)
        new_ridge = st.slider("5. Min Ridge Score (Gabor Var / 100)", 5.0, 30.0, float(current_cfg["ridge_min_score"]), 1.0)
        new_composite = st.slider("🎯 Target Pass Boundary Score", 40.0, 80.0, float(current_cfg["composite_pass_score"]), 5.0)

    st.session_state["threshold_config"] = {
        "blur_min": new_blur,
        "brightness_min": new_b_min,
        "brightness_max": new_b_max,
        "glare_max_ratio": new_glare,
        "roi_min_ratio": new_roi,
        "ridge_min_score": new_ridge,
        "composite_pass_score": new_composite
    }

    if st.button("Reset to Default Assignment 4 Thresholds", use_container_width=True):
        st.session_state["threshold_config"] = DEFAULT_THRESHOLDS.copy()
        st.success("Reset to Assignment 4 Reference Defaults!")
        st.rerun()

    render_footer()

# =============================================================================
# PAGE 6: HELP & DOCUMENTATION
# =============================================================================
elif view_choice == "Help & Documentation":
    st.markdown('<div class="fv-title">Help & Core Documentation</div>', unsafe_allow_html=True)
    st.markdown('<div class="fv-subtitle">Metric Descriptions & Assignment Reference Mapping Note</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="fv-card">
        <h3 style="color:#2CF6C3; margin-top:0;">📐 Quality Assessment Metric Formulations</h3>
        <ol style="font-size:0.9rem; line-height:1.6;">
            <li><strong>Spatial Blur Inspection:</strong> <code>cv2.Laplacian(gray, cv2.CV_64F).var()</code>. Rejects if variance &lt; 10.0.</li>
            <li><strong>Brightness Check:</strong> <code>np.mean(gray)</code>. Rejects if &lt; 50.0 (Too Dark) or &gt; 210.0 (Too Bright).</li>
            <li><strong>Glare Detection:</strong> Overexposed pixel fraction <code>&gt; 240</code>. Rejects if fraction &gt; 0.05.</li>
            <li><strong>ROI Completeness:</strong> GaussianBlur(5,5) + Otsu Thresholding. Rejects if foreground ratio &lt; 0.15.</li>
            <li><strong>Ridge Clarity:</strong> Gabor kernel convolution (21x21, sigma=5.0, theta=pi/4, lambd=10.0, gamma=0.5). Score = <code>var(filtered) / 100.0</code>. Rejects if score &lt; 15.0.</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="fv-card">
        <h3 style="color:#2CF6C3; margin-top:0;">🎯 Composite Score & Binary Pass/Fail Rule</h3>
        <p style="font-size:0.9rem; color:#7CF7D4;">
            Metrics are normalized to [0,1]:
            <br><code>n_blur = min(1.0, blur_score / 50.0)</code>
            <br><code>n_bright = max(0.0, 1.0 - abs(brightness - 128.0) / 128.0)</code>
            <br><code>n_glare = max(0.0, 1.0 - (glare_fraction / 0.05))</code>
            <br><code>n_roi = min(1.0, roi_fraction / 0.35)</code>
            <br><code>n_ridge = min(1.0, ridge_score / 30.0)</code>
            <br><br>
            <strong>Composite Score Formula:</strong><br>
            <code>composite = (0.25*n_blur + 0.15*n_bright + 0.15*n_glare + 0.20*n_roi + 0.25*n_ridge) * 100.0</code>
            <br><br>
            <strong>Decision Rule:</strong> <code>passed = (composite &gt;= 60.0) and (not has_hard_failure)</code>
        </p>
    </div>
    """, unsafe_allow_html=True)

    render_footer()
