"""
FingerVision Theme Deck & CSS Styling Rules (ui/theme.py)
Enforces Emerald Glassmorphic Design Paradigm, Dark Header Bar Fix, and Dark File Uploader Box.
"""

COLOR_DECK = {
    "background": "#08120F",
    "card_bg": "#11211D",
    "primary": "#2CF6C3",
    "secondary": "#7CF7D4",
    "high_accent": "#D7FF64",
    "success": "#3AFF9A",
    "warning": "#FFC857",
    "danger": "#FF5A76",
    "text": "#F7FFFB"
}

def inject_custom_theme():
    """Returns CSS block for injecting glassmorphic layout, header fix, and navigation pill styles."""
    return """
    <style>
        /* Streamlit Top Header Bar Fix (removes bright white top bar) */
        header[data-testid="stHeader"], [data-testid="stHeader"] {
            background-color: #08120F !important;
            background: #08120F !important;
        }

        /* Global App Background */
        .stApp {
            background-color: #08120F !important;
            color: #F7FFFB !important;
            font-family: 'Inter', system-ui, sans-serif;
        }
        
        /* Sidebar Container */
        section[data-testid="stSidebar"] {
            background-color: #0C1A16 !important;
            border-right: 1px solid rgba(44, 246, 195, 0.15);
        }

        /* Sidebar Navigation Radio Buttons (Glass Pill Style) */
        div[data-testid="stSidebar"] div[role="radiogroup"] {
            gap: 8px;
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] label {
            background: rgba(17, 33, 29, 0.7) !important;
            border: 1px solid rgba(44, 246, 195, 0.2) !important;
            border-radius: 8px !important;
            padding: 10px 14px !important;
            color: #F7FFFB !important;
            font-weight: 600 !important;
            font-size: 0.92rem !important;
            transition: all 0.2s ease-in-out !important;
            width: 100% !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
            background: rgba(44, 246, 195, 0.15) !important;
            border-color: #2CF6C3 !important;
            color: #2CF6C3 !important;
            transform: translateX(4px);
        }
        div[data-testid="stSidebar"] div[role="radiogroup"] label[data-baseweb="radio"] div:first-child {
            background-color: #2CF6C3 !important;
        }
        div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] label {
            color: #F7FFFB !important;
            font-weight: 600 !important;
        }

        /* File Uploader Dark Glassmorphism Styling (removes white box) */
        [data-testid="stFileUploader"] {
            background-color: rgba(17, 33, 29, 0.85) !important;
            border: 1px solid rgba(44, 246, 195, 0.3) !important;
            border-radius: 12px !important;
            padding: 16px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        [data-testid="stFileUploaderDropzone"] {
            background-color: rgba(8, 18, 15, 0.9) !important;
            border: 2px dashed rgba(44, 246, 195, 0.4) !important;
            border-radius: 10px !important;
            color: #F7FFFB !important;
        }
        [data-testid="stFileUploaderDropzone"] * {
            color: #F7FFFB !important;
        }
        [data-testid="stFileUploadDropzoneInstructions"] {
            color: #7CF7D4 !important;
        }
        
        /* Titles & Headings */
        .fv-title {
            font-size: 2.2rem;
            font-weight: 900;
            background: linear-gradient(135deg, #2CF6C3 0%, #7CF7D4 50%, #D7FF64 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 2px;
        }
        
        .fv-subtitle {
            font-size: 0.85rem;
            color: #7CF7D4;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }
        
        /* Glassmorphic Cards */
        .fv-card {
            background: rgba(17, 33, 29, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(44, 246, 195, 0.2);
            border-radius: 12px;
            padding: 18px;
            margin-bottom: 16px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }
        
        .fv-card-pass {
            background: rgba(17, 33, 29, 0.9);
            border: 1px solid rgba(58, 255, 154, 0.4);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .fv-card-fail {
            background: rgba(30, 15, 20, 0.9);
            border: 1px solid rgba(255, 90, 118, 0.4);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 12px;
        }
        
        .badge-pass {
            background-color: rgba(58, 255, 154, 0.15);
            color: #3AFF9A;
            border: 1px solid #3AFF9A;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.8rem;
        }
        
        .badge-fail {
            background-color: rgba(255, 90, 118, 0.15);
            color: #FF5A76;
            border: 1px solid #FF5A76;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.8rem;
        }

        .banner-pass {
            background: linear-gradient(90deg, rgba(58,255,154,0.15) 0%, rgba(17,33,29,0.9) 100%);
            border-left: 6px solid #3AFF9A;
            border: 1px solid rgba(58,255,154,0.3);
            border-left-width: 6px;
            padding: 16px;
            border-radius: 8px;
            font-size: 1.05rem;
            font-weight: 600;
            color: #3AFF9A;
            margin-bottom: 20px;
        }
        
        .banner-fail {
            background: linear-gradient(90deg, rgba(255,90,118,0.15) 0%, rgba(30,15,20,0.9) 100%);
            border-left: 6px solid #FF5A76;
            border: 1px solid rgba(255,90,118,0.3);
            border-left-width: 6px;
            padding: 16px;
            border-radius: 8px;
            font-size: 1.05rem;
            font-weight: 600;
            color: #FF5A76;
            margin-bottom: 20px;
        }

        .scanner-container {
            position: relative;
            overflow: hidden;
            border: 2px solid #2CF6C3;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(44, 246, 195, 0.4);
        }
        
        .scanline {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, transparent, #2CF6C3, #D7FF64, #2CF6C3, transparent);
            box-shadow: 0 0 15px #2CF6C3, 0 0 25px #D7FF64;
            animation: scan 2.5s ease-in-out infinite alternate;
            z-index: 10;
        }
        
        @keyframes scan {
            0% { top: 0%; }
            100% { top: 96%; }
        }

        .fv-footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background-color: #060E0C;
            border-top: 1px solid rgba(44, 246, 195, 0.2);
            color: #7CF7D4;
            text-align: center;
            padding: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 1px;
            z-index: 9999;
        }
    </style>
    """
