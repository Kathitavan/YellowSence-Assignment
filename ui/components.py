"""
FingerVision Component Library (ui/components.py)
Reusable UI elements for Presentation Layer including crisp Base64 SVG Logo Engine.
"""

import base64
import streamlit as st

def get_logo_svg_b64() -> str:
    """Returns Base64 encoded string of custom minimal FingerVision vector SVG logo."""
    svg_data = """<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="45" stroke="#2CF6C3" stroke-width="3.5" stroke-dasharray="8 4" fill="none" opacity="0.9"/>
        <circle cx="50" cy="50" r="36" stroke="#7CF7D4" stroke-width="2" fill="none" opacity="0.6"/>
        <circle cx="50" cy="50" r="27" stroke="#D7FF64" stroke-width="1.5" fill="none" opacity="0.4"/>
        <path d="M35 50 C35 35, 65 35, 65 50 C65 65, 35 65, 35 80" stroke="#2CF6C3" stroke-width="4.5" stroke-linecap="round" fill="none"/>
        <path d="M42 50 C42 41, 58 41, 58 50 C58 59, 42 59, 42 72" stroke="#7CF7D4" stroke-width="3.8" stroke-linecap="round" fill="none"/>
        <path d="M48 50 C48 46, 52 46, 52 50 C52 54, 48 54, 48 64" stroke="#D7FF64" stroke-width="3" stroke-linecap="round" fill="none"/>
        <line x1="50" y1="4" x2="50" y2="14" stroke="#2CF6C3" stroke-width="3.5" stroke-linecap="round"/>
        <line x1="50" y1="86" x2="50" y2="96" stroke="#2CF6C3" stroke-width="3.5" stroke-linecap="round"/>
        <line x1="4" y1="50" x2="14" y2="50" stroke="#2CF6C3" stroke-width="3.5" stroke-linecap="round"/>
        <line x1="86" y1="50" x2="96" y2="50" stroke="#2CF6C3" stroke-width="3.5" stroke-linecap="round"/>
    </svg>"""
    return base64.b64encode(svg_data.encode('utf-8')).decode('utf-8')

def render_logo_html(width=46, show_text=True):
    """Renders HTML block containing Base64 SVG Logo and Typography."""
    b64 = get_logo_svg_b64()
    img_html = f'<img src="data:image/svg+xml;base64,{b64}" width="{width}" height="{width}" style="vertical-align: middle; filter: drop-shadow(0 0 10px rgba(44, 246, 195, 0.6));" />'
    
    if not show_text:
        return img_html
        
    return f"""
    <div style="display: flex; align-items: center; gap: 14px; padding: 6px 0 14px 0; border-bottom: 1px solid rgba(44, 246, 195, 0.15); margin-bottom: 15px;">
        {img_html}
        <div>
            <div style="font-size: 1.5rem; font-weight: 900; background: linear-gradient(135deg, #2CF6C3 0%, #7CF7D4 50%, #D7FF64 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; line-height: 1.1; letter-spacing: -0.5px;">FingerVision</div>
            <div style="font-size: 0.65rem; color: #7CF7D4; text-transform: uppercase; letter-spacing: 1px; margin-top: 2px;">Quality Control System</div>
        </div>
    </div>
    """

def render_sidebar_brand():
    """Sidebar branding banner."""
    st.sidebar.markdown(render_logo_html(48, show_text=True), unsafe_allow_html=True)

def render_footer():
    """Footer signature line."""
    st.markdown("""
        <div class="fv-footer">
            FingerVision · v1.0
        </div>
    """, unsafe_allow_html=True)

def render_step_timeline():
    """Live processing step timeline block."""
    st.markdown("""
    <div style="background: rgba(17,33,29,0.75); border: 1px solid rgba(44, 246, 195, 0.25); border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; font-size: 0.84rem; color: #7CF7D4; box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
        <strong style="color: #2CF6C3;">Pipeline Stage Timeline:</strong> 
        <span style="color:#3AFF9A;">[✓ Grayscale]</span> → 
        <span style="color:#3AFF9A;">[✓ Blur Inspection]</span> → 
        <span style="color:#3AFF9A;">[✓ Brightness Check]</span> → 
        <span style="color:#3AFF9A;">[✓ Glare Ratio]</span> → 
        <span style="color:#3AFF9A;">[✓ ROI Binarization]</span> → 
        <span style="color:#3AFF9A;">[✓ Gabor Filtering]</span> → 
        <span style="color:#D7FF64;">[✓ Composite Matrix]</span>
    </div>
    """, unsafe_allow_html=True)

def render_metric_card(title: str, is_ok: bool, value_str: str, threshold_str: str, progress_pct: float = 100.0):
    """Renders glassmorphic card for individual metric with badge and animated progress bar."""
    card_class = "fv-card-pass" if is_ok else "fv-card-fail"
    badge_html = '<span class="badge-pass">PASS</span>' if is_ok else '<span class="badge-fail">FAIL</span>'
    bar_color = "#3AFF9A" if is_ok else "#FF5A76"
    pct_clamped = max(0.0, min(100.0, progress_pct))

    st.markdown(f"""
    <div class="{card_class}">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>{title}</strong> {badge_html}
        </div>
        <div style="margin-top: 6px; font-size:0.88rem; color:#F7FFFB;">
            {value_str} | <span style="color:#7CF7D4;">{threshold_str}</span>
        </div>
        <div style="background: rgba(255,255,255,0.1); border-radius: 4px; height: 6px; width: 100%; margin-top: 8px; overflow: hidden;">
            <div style="background: {bar_color}; width: {pct_clamped}%; height: 100%; transition: width 0.5s ease-in-out;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
