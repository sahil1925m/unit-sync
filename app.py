"""
Unit-Sync - Hierarchical Note Consolidation Tool
=================================================
A Streamlit web application that manages study notes by Subject and Unit.

Core Rule: Each Unit has ONE consolidated PDF. New notes are appended with timestamps.

Features:
- Subject folder management (real directories)
- Unit PDF consolidation with pypdf merging
- Timestamp headers for each addition
- Material You dark theme
- AI-powered Select-to-Define

Author: Senior Full-Stack Developer
Tech Stack: Streamlit, pypdf, markdown2, xhtml2pdf, google-generativeai
"""

import streamlit as st
import streamlit.components.v1 as components
import markdown2
from xhtml2pdf import pisa
# Handle different pypdf/PyPDF2 versions
try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from PyPDF2 import PdfMerger
    except ImportError:
        from PyPDF2 import PdfFileMerger as PdfMerger
import io
import os
import shutil
from datetime import datetime
from pathlib import Path
try:
    from github_sync import GithubSync
except ImportError:
    GithubSync = None

# =============================================================================
# CONFIGURATION
# =============================================================================
ROOT_DIR = Path("My_Study_Notes")
MAX_UNITS = 10

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="Unit-Sync | Smart Notes",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# PWA / MOBILE CONFIGURATION
# =============================================================================
st.markdown("""
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="application-name" content="Unit-Sync">
<meta name="theme-color" content="#FAF8F5">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<style>
/* Mobile Optimizations */
@media (max-width: 768px) {
    .stApp { padding-top: 20px; }
    button { min-height: 44px; } /* Touch friendly */
}
</style>
""", unsafe_allow_html=True)

# =============================================================================
# MATERIAL YOU DARK THEME CSS
# =============================================================================
st.markdown("""
<style>
    /* Import Inter + Poppins for modern feel */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
    
    /* ============ WARM SCHOLAR PALETTE ============ */
    :root {
        /* Warm cream backgrounds */
        --bg-primary: #FAF8F5;
        --bg-secondary: #FFFFFF;
        --bg-card: #FFFFFF;
        --bg-elevated: #F5F2EE;
        /* Modern accents */
        --accent-primary: #2D7A72;
        --accent-secondary: #4DB6AC;
        --accent-warm: #E8985E;
        --accent-warm-light: #FBE8D9;
        /* Typography */
        --text-primary: #2C3E50;
        --text-secondary: #5D6D7E;
        --text-muted: #95A5A6;
        /* Borders & Effects */
        --border-subtle: #E8E4DF;
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.08);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.12);
        --radius: 16px;
        --radius-sm: 10px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ============ SMOOTH ANIMATIONS ============ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    /* ============ GLOBAL STYLES ============ */
    .stApp {
        background: var(--bg-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    /* ============ MAIN HEADER ============ */
    .main-header {
        color: var(--accent-primary);
        font-size: 2.4rem;
        font-weight: 700;
        text-align: center;
        padding: 0.5rem 0 0.5rem 0;
        letter-spacing: -0.02em;
        animation: fadeIn 0.6s ease-out;
    }
    
    .sub-header {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 400;
        animation: fadeIn 0.6s ease-out 0.1s both;
    }
    
    /* ============ LIBRARY CARD STYLES ============ */
    .library-card {
        background: var(--bg-card);
        border-radius: var(--radius);
        padding: 20px 24px;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-subtle);
        margin-bottom: 1rem;
        transition: var(--transition);
        animation: fadeIn 0.4s ease-out;
    }
    
    .library-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: var(--accent-secondary);
    }
    
    .library-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .library-meta {
        font-size: 0.85rem;
        color: var(--text-muted);
    }
    
    /* ============ SIDEBAR STYLES ============ */
    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-subtle);
    }
    
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: var(--text-primary) !important;
        font-family: 'Poppins', sans-serif !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown p {
        color: var(--text-secondary) !important;
    }

    /* Expander Styling in Sidebar */
    section[data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: var(--bg-elevated) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }
    
    /* ============ INPUT STYLES ============ */
    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition);
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-primary) !important;
        box-shadow: 0 0 0 3px rgba(45, 122, 114, 0.15) !important;
    }
    
    /* ============ BUTTON STYLES ============ */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent-primary) 0%, var(--accent-secondary) 100%) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.7rem 1.6rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition);
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-md) !important;
        filter: brightness(1.05);
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Success button variant */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--accent-warm) 0%, #D97B4A 100%) !important;
        color: #FFFFFF !important;
    }
    
    /* ============ DOWNLOAD BUTTON ============ */
    .stDownloadButton > button {
        background: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border: 2px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        transition: var(--transition);
    }
    
    .stDownloadButton > button:hover {
        border-color: var(--accent-primary) !important;
        color: var(--accent-primary) !important;
    }
    
    /* ============ RADIO BUTTONS (Mode Toggle) ============ */
    .stRadio > div {
        background: var(--bg-elevated);
        border-radius: var(--radius-sm);
        padding: 4px;
        display: flex;
        gap: 4px;
    }
    
    .stRadio label {
        border-radius: var(--radius-sm) !important;
        padding: 8px 16px !important;
        transition: var(--transition);
    }
    
    .stRadio label[data-checked="true"] {
        background: var(--accent-primary) !important;
        color: white !important;
    }
    
    /* ============ EXPANDER STYLES ============ */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
    }
    
    /* ============ SUCCESS/ERROR MESSAGES ============ */
    .stSuccess {
        background: rgba(45, 122, 114, 0.1) !important;
        border-left: 4px solid var(--accent-primary) !important;
        border-radius: var(--radius-sm) !important;
        animation: slideIn 0.3s ease-out;
    }
    
    .stError {
        background: rgba(220, 53, 69, 0.1) !important;
        border-left: 4px solid #DC3545 !important;
        border-radius: var(--radius-sm) !important;
        animation: slideIn 0.3s ease-out;
    }
    
    .stInfo {
        background: rgba(232, 152, 94, 0.1) !important;
        border-left: 4px solid var(--accent-warm) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* ============ STATS CARDS ============ */
    .stat-card {
        background: var(--bg-card);
        border-radius: var(--radius-sm);
        padding: 16px;
        text-align: center;
        border: 1px solid var(--border-subtle);
        transition: var(--transition);
    }
    
    .stat-card:hover {
        box-shadow: var(--shadow-sm);
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: var(--accent-primary);
    }
    
    .stat-label {
        font-size: 0.8rem;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* ============ COLUMN TRANSITIONS ============ */
    [data-testid="column"] {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* ============ MARKDOWN STYLING ============ */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: var(--text-primary) !important;
    }
    
    .stMarkdown p {
        color: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# DIRECTORY MANAGEMENT
# =============================================================================
def ensure_root_dir():
    """Create the root directory if it doesn't exist."""
    ROOT_DIR.mkdir(exist_ok=True)

def get_subjects():
    """Get list of all subject folders."""
    ensure_root_dir()
    subjects = [d.name for d in ROOT_DIR.iterdir() if d.is_dir()]
    return sorted(subjects)

def create_subject(subject_name):
    """Create a new subject folder."""
    ensure_root_dir()
    # Sanitize folder name
    safe_name = "".join(c for c in subject_name if c.isalnum() or c in (' ', '_', '-')).strip()
    safe_name = safe_name.replace(' ', '_')
    
    if not safe_name:
        return False, "Invalid subject name"
    
    subject_path = ROOT_DIR / safe_name
    if subject_path.exists():
        return False, f"Subject '{safe_name}' already exists"
    
    subject_path.mkdir(parents=True)
    return True, f"Created '{safe_name}'"

def get_unit_files(subject):
    """Get list of unit PDF files for a subject."""
    subject_path = ROOT_DIR / subject
    if not subject_path.exists():
        return []
    
    units = []
    for i in range(1, MAX_UNITS + 1):
        unit_file = subject_path / f"Unit_{i}.pdf"
        if unit_file.exists():
            size_kb = unit_file.stat().st_size / 1024
            units.append({"unit": i, "size": f"{size_kb:.1f} KB", "path": unit_file})
    return units

def delete_subject(subject_name):
    """Delete a subject folder and all its contents."""
    subject_path = ROOT_DIR / subject_name
    if subject_path.exists():
        shutil.rmtree(subject_path)
        return True
    return False

def rename_subject(old_name, new_name):
    """Rename a subject folder."""
    import os
    old_path = ROOT_DIR / old_name
    new_name_safe = "".join(c if c.isalnum() or c in " _-" else "_" for c in new_name).strip()
    new_path = ROOT_DIR / new_name_safe
    
    if not old_path.exists():
        return False, "Subject not found"
    if new_path.exists():
        return False, f"Subject '{new_name_safe}' already exists"
    
    os.rename(old_path, new_path)
    return True, f"Renamed to '{new_name_safe}'"

def delete_unit(subject, unit):
    """Delete a specific unit's PDF and markdown files."""
    pdf_path = ROOT_DIR / subject / f"Unit_{unit}.pdf"
    md_path = ROOT_DIR / subject / f"Unit_{unit}.md"
    
    deleted = False
    if pdf_path.exists():
        pdf_path.unlink()
        deleted = True
    if md_path.exists():
        md_path.unlink()
        deleted = True
    
    return deleted

def get_pdf_base64(subject, unit):
    """Get PDF file as base64 for embedding."""
    import base64
    pdf_path = ROOT_DIR / subject / f"Unit_{unit}.pdf"
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

# =============================================================================
# MARKDOWN STORAGE (For Library Reading)
# =============================================================================
def save_markdown_source(subject, unit, markdown_content):
    """Save markdown source file alongside PDF for in-app reading."""
    subject_path = ROOT_DIR / subject
    subject_path.mkdir(exist_ok=True)
    
    md_path = subject_path / f"Unit_{unit}.md"
    
    # Add timestamp header to new content
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    timestamped_content = f"\n\n---\n\n**📅 Added on: {timestamp}**\n\n---\n\n{markdown_content}"
    
    if md_path.exists():
        # Append to existing markdown
        existing = md_path.read_text(encoding='utf-8')
        md_path.write_text(existing + timestamped_content, encoding='utf-8')
    else:
        # Create new markdown file
        md_path.write_text(timestamped_content.strip(), encoding='utf-8')
    
    return True

def load_markdown_source(subject, unit):
    """Load markdown source for reading in Library."""
    md_path = ROOT_DIR / subject / f"Unit_{unit}.md"
    if md_path.exists():
        return md_path.read_text(encoding='utf-8')
    return None

def get_units_with_content(subject):
    """Get list of units that have markdown source files for reading."""
    subject_path = ROOT_DIR / subject
    if not subject_path.exists():
        return []
    
    units = []
    for i in range(1, MAX_UNITS + 1):
        md_file = subject_path / f"Unit_{i}.md"
        if md_file.exists():
            size_kb = md_file.stat().st_size / 1024
            units.append({"unit": i, "size": f"{size_kb:.1f} KB", "path": md_file})
    return units

# =============================================================================
# PDF GENERATION & CONSOLIDATION
# =============================================================================
def convert_markdown_to_pdf(markdown_text):
    """Convert Markdown to PDF bytes with Paper White theme for printing."""
    # Add timestamp header
    timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    timestamped_md = f"---\n\n**📅 Added on: {timestamp}**\n\n---\n\n{markdown_text}"
    
    # Convert to HTML
    html_content = markdown2.markdown(
        timestamped_md,
        extras=["fenced-code-blocks", "tables", "strike", "header-ids"]
    )
    
    # Process key points (bold text before colons with Peach)
    import re
    html_content = re.sub(
        r'(\>)([^<:]+)(:)',
        r'\1<span style="color: #CC9A4E; font-weight: 600;">\2</span>\3',
        html_content
    )
    
    # Paper White Theme for Professional Printing
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Georgia', 'Times New Roman', serif;
                font-size: 11pt;
                line-height: 1.7;
                color: #4A5568;
                background: #FFFFFF;
            }}
            
            /* Paper White Headers - Teal inspired */
            h1 {{
                font-size: 22pt;
                font-weight: 700;
                color: #2D7A72;
                border-bottom: 2px solid #B2DFDB;
                padding-bottom: 8px;
                margin-bottom: 16px;
            }}
            
            h2 {{
                font-size: 16pt;
                font-weight: 600;
                color: #2D7A72;
                margin-top: 1.5em;
                padding-left: 10px;
                border-left: 3px solid #80CBC4;
            }}
            
            h3 {{
                font-size: 13pt;
                font-weight: 600;
                color: #4A5568;
                margin-top: 1.2em;
            }}
            
            /* Key points - Peach accent for print */
            strong {{
                color: #CC9A4E;
                font-weight: 600;
            }}
            
            em {{
                color: #718096;
                font-style: italic;
            }}
            
            code {{
                background: #F7FAFC;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Consolas', monospace;
                font-size: 10pt;
                color: #4A5568;
                border: 1px solid #E2E8F0;
            }}
            
            pre {{
                background: #F7FAFC;
                border: 1px solid #E2E8F0;
                border-radius: 6px;
                padding: 14px;
                overflow-x: auto;
                margin: 1em 0;
            }}
            
            pre code {{
                background: transparent;
                border: none;
                color: #4A5568;
            }}
            
            blockquote {{
                border-left: 3px solid #80CBC4;
                margin: 1em 0;
                padding: 10px 14px;
                background: #F0FDFA;
                border-radius: 0 6px 6px 0;
            }}
            
            /* Tables */
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 1em 0;
            }}
            
            th {{
                background: #80CBC4;
                color: #1A202C;
                font-weight: 600;
                padding: 10px;
                text-align: left;
            }}
            
            td {{
                border: 1px solid #E2E8F0;
                padding: 8px 10px;
            }}
            
            tr:nth-child(even) {{
                background: #F7FAFC;
            }}
            
            hr {{
                border: none;
                border-top: 1px solid #E2E8F0;
                margin: 1.5em 0;
            }}
            
            ul li::marker {{
                color: #80CBC4;
            }}
            
            ol li::marker {{
                color: #2D7A72;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Generate PDF
    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(styled_html, dest=pdf_buffer)
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()

def consolidate_pdf(subject, unit, markdown_content, overwrite=False):
    """
    Consolidate notes into a Unit PDF.
    
    - If overwrite=True: Replace existing PDF entirely
    - If PDF doesn't exist: Create new PDF
    - If PDF exists and overwrite=False: Append new content to end
    
    Returns: (success: bool, message: str)
    """
    ensure_root_dir()
    subject_path = ROOT_DIR / subject
    subject_path.mkdir(exist_ok=True)
    
    unit_path = subject_path / f"Unit_{unit}.pdf"
    md_path = subject_path / f"Unit_{unit}.md"
    
    # Convert new content to PDF
    new_pdf_bytes = convert_markdown_to_pdf(markdown_content)
    
    try:
        if overwrite or not unit_path.exists():
            # OVERWRITE or CREATE: New PDF
            with open(unit_path, 'wb') as f:
                f.write(new_pdf_bytes)
            
            # Also overwrite markdown file
            timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            timestamped_content = f"**📅 Created on: {timestamp}**\n\n---\n\n{markdown_content}"
            md_path.write_text(timestamped_content, encoding='utf-8')
            
            if overwrite:
                return True, f"✅ Overwrote Unit {unit} PDF"
            else:
                return True, f"✅ Created new Unit {unit} PDF"
        else:
            # APPEND: Add to existing PDF
            merger = PdfMerger()
            
            # Add existing PDF
            merger.append(str(unit_path))
            
            # Add new content
            new_pdf_buffer = io.BytesIO(new_pdf_bytes)
            merger.append(new_pdf_buffer)
            
            # Write merged PDF
            output_buffer = io.BytesIO()
            merger.write(output_buffer)
            merger.close()
            
            # Save to file
            output_buffer.seek(0)
            with open(unit_path, 'wb') as f:
                f.write(output_buffer.getvalue())
            
            # Save markdown source for Library reading (append)
            save_markdown_source(subject, unit, markdown_content)
            
            return True, f"✅ Appended to Unit {unit} PDF"
        
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

# Note: API key is now hardcoded in main() function at line 1394

# =============================================================================
# LIVE PREVIEW HTML WITH SELECT-TO-DEFINE
# =============================================================================
def process_html_for_styling(html_content):
    """
    Post-process HTML to add handmade-style formatting:
    - Key Points: Bold and color text before colons (Orange/Teal accent)
    - Analogies: Wrap analogy paragraphs in yellow sticky-note cards
    - Concept Boxes: Detect Summary, Example, Mechanism keywords
    - Technical Terms: Style inline code as gray pills
    """
    import re
    
    # Key Point Logic: Bold text before colons in paragraphs
    # Match pattern like "Definition:" or "Security Risk:" at start of paragraph
    def style_key_points(text):
        # Only match word(s) before colon when it's at the start of a paragraph
        # Pattern: <p>Some Text: rest of paragraph
        pattern = r'<p>([A-Za-z][A-Za-z\s]+):'
        replacement = r'<p><span class="key-point">\1</span>:'
        return re.sub(pattern, replacement, text)
    
    # Analogy/Real-World Detection: Wrap in yellow sticky note
    def wrap_analogies(text):
        patterns = [
            (r'<p>([^<]*Analogy:[^<]*)</p>', r'<div class="sticky-note"><p>\1</p></div>'),
            (r'<p>([^<]*\([^)]*Analogy[^)]*\)[^<]*)</p>', r'<div class="sticky-note"><p>\1</p></div>'),
            (r'<p>([^<]*Real-World[^<]*)</p>', r'<div class="sticky-note"><p>\1</p></div>'),
            (r'<p>([^<]*Real World[^<]*)</p>', r'<div class="sticky-note"><p>\1</p></div>'),
        ]
        for pattern, replacement in patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text
    
    # Concept Box Detection: Wrap paragraphs with keywords in colored cards
    def wrap_concept_boxes(text):
        # Summary → Blue card
        text = re.sub(
            r'<h2>([^<]*Summary[^<]*)</h2>',
            r'<h2 class="concept-header summary">\1</h2>',
            text, flags=re.IGNORECASE
        )
        text = re.sub(
            r'<h3>([^<]*Summary[^<]*)</h3>',
            r'<h3 class="concept-header summary">\1</h3>',
            text, flags=re.IGNORECASE
        )
        
        # Example → Green card
        text = re.sub(
            r'<h2>([^<]*Example[^<]*)</h2>',
            r'<h2 class="concept-header example">\1</h2>',
            text, flags=re.IGNORECASE
        )
        text = re.sub(
            r'<h3>([^<]*Example[^<]*)</h3>',
            r'<h3 class="concept-header example">\1</h3>',
            text, flags=re.IGNORECASE
        )
        
        # Mechanism/How it Works → Purple card
        text = re.sub(
            r'<h2>([^<]*Mechanism[^<]*)</h2>',
            r'<h2 class="concept-header mechanism">\1</h2>',
            text, flags=re.IGNORECASE
        )
        text = re.sub(
            r'<h2>([^<]*How [iI]t [wW]orks[^<]*)</h2>',
            r'<h2 class="concept-header mechanism">\1</h2>',
            text, flags=re.IGNORECASE
        )
        
        return text
    
    # Wrap blockquotes in info cards
    def wrap_sections_in_cards(text):
        text = text.replace('<blockquote>', '<div class="info-card"><blockquote>')
        text = text.replace('</blockquote>', '</blockquote></div>')
        return text
    
    # Highlight text in double quotes
    def highlight_quoted_text(text):
        import re
        # Match text inside double quotes and wrap in highlight span
        text = re.sub(
            r'"([^"]+)"',
            r'<span class="quoted-text">"\1"</span>',
            text
        )
        return text
    
    # Terminology Pills: Wrap technical terms in styled pills
    def add_terminology_pills(text):
        import re
        # Common technical terms to highlight as pills
        terms = [
            'SMTP', 'Botnet', 'Botnets', 'Malware', 'Phishing', 'Ransomware',
            'Firewall', 'VPN', 'DNS', 'HTTP', 'HTTPS', 'SSL', 'TLS', 'API',
            'SQL', 'XSS', 'DDoS', 'DoS', 'IP', 'TCP', 'UDP', 'HTML', 'CSS',
            'Harvesting', 'Spoofing', 'Encryption', 'Decryption', 'Authentication',
            'Authorization', 'Trojan', 'Worm', 'Spyware', 'Adware', 'Keylogger'
        ]
        for term in terms:
            # Case-insensitive replacement, preserve original case
            pattern = rf'\b({term})\b'
            text = re.sub(pattern, r'<span class="term-pill">\1</span>', text, flags=re.IGNORECASE)
        return text
    
    # Apply transformations
    html_content = wrap_analogies(html_content)
    html_content = wrap_concept_boxes(html_content)
    html_content = wrap_sections_in_cards(html_content)
    html_content = highlight_quoted_text(html_content)
    html_content = add_terminology_pills(html_content)
    
    return html_content


def get_preview_html(html_content, api_key=None):
    """
    Generate premium preview HTML with handmade-style student notes.
    
    Features:
    - Neon-glow headers with gradient underlines
    - Key Point highlighting (text before colons in Mint Green)
    - Sticky-note style for analogies
    - Card layouts for sections
    - Modern Inter/Montserrat typography
    - Select-to-Define AI feature
    """
    js_api_key = api_key if api_key else ""
    
    # Post-process HTML for styling
    styled_html = process_html_for_styling(html_content)
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Montserrat:wght@600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
            /* ============================================================
               HANDMADE-STYLE STUDENT NOTES CSS
               ============================================================ */
            
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            
            body {{
                font-family: 'Inter', -apple-system, sans-serif;
                font-size: 15px;
                line-height: 1.7;
                color: #E0E0E0;
                background: #121212;
                padding: 24px;
                min-height: 100%;
                -webkit-font-smoothing: antialiased;
            }}
            
            /* ============ HEADER HIERARCHY ============ */
            
            h1 {{
                font-family: 'Inter', sans-serif;
                font-size: 2rem;
                font-weight: 700;
                color: #80CBC4;
                text-align: left;
                margin: 0 0 1em 0;
                padding-bottom: 0.5em;
                letter-spacing: -0.02em;
                border-bottom: 2px solid rgba(128, 203, 196, 0.3);
            }}
            
            h2 {{
                font-family: 'Inter', sans-serif;
                font-size: 1.5rem;
                font-weight: 600;
                color: #80CBC4;
                margin: 2em 0 0.7em 0;
                padding-left: 14px;
                position: relative;
            }}
            
            h2::before {{
                content: '';
                position: absolute;
                left: 0;
                top: 0;
                bottom: 0;
                width: 4px;
                background: #80CBC4;
                border-radius: 2px;
            }}
            
            h3 {{
                font-family: 'Inter', sans-serif;
                font-size: 1.4rem;
                font-weight: 600;
                color: #14B8A6;
                margin: 1.5em 0 0.5em 0;
            }}
            
            h4, h5, h6 {{
                font-size: 1.15rem;
                font-weight: 600;
                color: #FFB74D;
                margin: 1.2em 0 0.4em 0;
            }}
            
            /* ============ CONCEPT HEADERS ============ */
            
            h2.concept-header.summary,
            h3.concept-header.summary {{
                background: linear-gradient(135deg, rgba(0, 209, 255, 0.12) 0%, rgba(0, 123, 200, 0.08) 100%);
                border: 1px solid rgba(0, 209, 255, 0.3);
                border-radius: 12px;
                padding: 14px 20px;
                color: #00D1FF;
            }}
            
            h2.concept-header.summary::before,
            h3.concept-header.summary::before {{
                display: none;
            }}
            
            h2.concept-header.example,
            h3.concept-header.example {{
                background: linear-gradient(135deg, rgba(0, 255, 171, 0.12) 0%, rgba(0, 180, 120, 0.08) 100%);
                border: 1px solid rgba(0, 255, 171, 0.3);
                border-radius: 12px;
                padding: 14px 20px;
                color: #00FFAB;
            }}
            
            h2.concept-header.example::before,
            h3.concept-header.example::before {{
                display: none;
            }}
            
            h2.concept-header.mechanism {{
                background: linear-gradient(135deg, rgba(167, 139, 250, 0.12) 0%, rgba(124, 58, 237, 0.08) 100%);
                border: 1px solid rgba(167, 139, 250, 0.3);
                border-radius: 12px;
                padding: 14px 20px;
                color: #A78BFA;
            }}
            
            h2.concept-header.mechanism::before {{
                display: none;
            }}
            
            /* ============ QUOTED TEXT HIGHLIGHT ============ */
            
            .quoted-text {{
                background: rgba(255, 204, 128, 0.2);
                color: #FFCC80;
                padding: 2px 8px;
                border-radius: 4px;
                font-weight: 500;
            }}
            
            /* ============ TERMINOLOGY PILLS ============ */
            
            .term-pill {{
                background: rgba(158, 158, 158, 0.2);
                color: #B0BEC5;
                padding: 2px 10px;
                border-radius: 12px;
                font-size: 0.9em;
                font-weight: 500;
                border: 1px solid rgba(158, 158, 158, 0.3);
                white-space: nowrap;
            }}
            
            /* ============ PARAGRAPHS & TEXT ============ */
            
            p {{
                margin: 0.9em 0;
                color: #E0E0E0;
                font-size: 15px;
            }}
            
            strong, b {{
                color: #FFCC80;
                font-weight: 600;
            }}
            
            em, i {{
                color: #9E9E9E;
                font-style: italic;
            }}
            
            /* ============ STICKY-NOTE ANALOGIES ============ */
            
            .sticky-note {{
                background: linear-gradient(145deg, #FFF59D 0%, #FFEE58 100%);
                color: #333;
                padding: 18px 22px;
                margin: 1.5em 0;
                border-radius: 4px;
                transform: rotate(-0.8deg);
                box-shadow: 
                    4px 4px 0 rgba(0,0,0,0.15),
                    8px 8px 20px rgba(0,0,0,0.2);
                position: relative;
                font-style: italic;
            }}
            
            .sticky-note::before {{
                content: '📌';
                position: absolute;
                top: -10px;
                left: 12px;
                font-size: 1.4em;
                filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));
            }}
            
            .sticky-note p {{
                margin: 0;
                color: #333;
                font-size: 14px;
                line-height: 1.6;
            }}
            
            /* ============ INFO CARDS ============ */
            
            .info-card {{
                background: linear-gradient(135deg, #1E1E1E 0%, #252525 100%);
                border: 1px solid #333;
                border-radius: 15px;
                padding: 4px;
                margin: 1.2em 0;
                box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            }}
            
            .info-card blockquote {{
                margin: 0;
                border-radius: 12px;
            }}
            
            blockquote {{
                margin: 1.2em 0;
                padding: 16px 20px 16px 24px;
                background: linear-gradient(135deg, rgba(0, 209, 255, 0.08) 0%, rgba(124, 77, 255, 0.05) 100%);
                border-left: 5px solid;
                border-image: linear-gradient(180deg, #00D1FF, #7C4DFF) 1;
                border-radius: 0 12px 12px 0;
                position: relative;
            }}
            
            blockquote::before {{
                content: '💡';
                position: absolute;
                top: -10px;
                left: 10px;
                font-size: 1.2em;
                background: #1A1A1A;
                padding: 0 6px;
            }}
            
            blockquote p {{
                margin: 0;
                color: #90CAF9;
                font-style: italic;
            }}
            
            /* ============ LISTS ============ */
            
            ul, ol {{
                margin: 1em 0;
                padding-left: 1.8em;
            }}
            
            li {{
                margin: 0.5em 0;
                color: #C5C5C5;
                position: relative;
            }}
            
            ul li::marker {{
                color: #00D1FF;
                font-size: 1.2em;
            }}
            
            ol li::marker {{
                color: #7C4DFF;
                font-weight: 700;
            }}
            
            li ul, li ol {{
                background: rgba(255,255,255,0.02);
                border-radius: 8px;
                padding: 8px 8px 8px 24px;
                margin-top: 8px;
            }}
            
            /* ============ CODE BLOCKS ============ */
            
            code {{
                font-family: 'JetBrains Mono', 'Fira Code', monospace;
                font-size: 0.88em;
                background: linear-gradient(135deg, #2D2D2D 0%, #1E1E1E 100%);
                color: #FFB74D;
                padding: 3px 10px;
                border-radius: 6px;
                border: 1px solid #333;
            }}
            
            pre {{
                background: linear-gradient(180deg, #0D0D0D 0%, #1A1A1A 100%);
                border: 1px solid #333;
                border-radius: 14px;
                padding: 20px 24px;
                margin: 1.2em 0;
                overflow-x: auto;
                position: relative;
            }}
            
            pre::before {{
                content: '< />';
                position: absolute;
                top: 12px;
                right: 16px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 12px;
                color: #555;
            }}
            
            pre::after {{
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #00D1FF, #7C4DFF, #00FFAB, #FF6B9D);
                border-radius: 14px 14px 0 0;
            }}
            
            pre code {{
                background: transparent;
                border: none;
                padding: 0;
                color: #E8E8E8;
                font-size: 0.9em;
                line-height: 1.6;
            }}
            
            /* ============ TABLES ============ */
            
            table {{
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                margin: 1.5em 0;
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #333;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }}
            
            th {{
                background: linear-gradient(135deg, #00D1FF 0%, #00A5CC 100%);
                color: #000;
                font-weight: 700;
                padding: 14px 16px;
                text-align: left;
                font-size: 0.95em;
            }}
            
            td {{
                padding: 12px 16px;
                border-bottom: 1px solid #2A2A2A;
                color: #C5C5C5;
            }}
            
            tr:last-child td {{
                border-bottom: none;
            }}
            
            tr:hover td {{
                background: rgba(0, 209, 255, 0.05);
            }}
            
            /* ============ HORIZONTAL RULES ============ */
            
            hr {{
                border: none;
                height: 3px;
                background: linear-gradient(90deg, transparent, #333, #00D1FF, #333, transparent);
                margin: 2.5em 0;
                border-radius: 2px;
            }}
            
            /* ============ LINKS ============ */
            
            a {{
                color: #00D1FF;
                text-decoration: none;
                border-bottom: 1px dashed rgba(0, 209, 255, 0.4);
                transition: all 0.2s ease;
            }}
            
            a:hover {{
                color: #00FFAB;
                border-bottom-color: #00FFAB;
            }}
            
            /* ============ SELECTION ============ */
            
            ::selection {{
                background: rgba(0, 209, 255, 0.4);
                color: #FFFFFF;
            }}
            
            /* ============ SCROLLBAR ============ */
            
            ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
            ::-webkit-scrollbar-track {{ background: #0D0D0D; border-radius: 4px; }}
            ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 4px; }}
            ::-webkit-scrollbar-thumb:hover {{ background: #444; }}
            
            /* ============ AI TOOLTIP ============ */
            
            .ai-tooltip {{
                position: fixed;
                background: linear-gradient(145deg, #1E1E1E 0%, #121212 100%);
                border: 2px solid #00D1FF;
                border-radius: 16px;
                max-width: 380px;
                min-width: 280px;
                box-shadow: 
                    0 0 20px rgba(0, 209, 255, 0.2),
                    0 10px 40px rgba(0,0,0,0.5);
                z-index: 10000;
                animation: tooltipPop 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
                overflow: hidden;
            }}
            
            @keyframes tooltipPop {{
                from {{ opacity: 0; transform: translateY(10px) scale(0.9); }}
                to {{ opacity: 1; transform: translateY(0) scale(1); }}
            }}
            
            .tooltip-header {{
                display: flex;
                align-items: center;
                gap: 10px;
                padding: 14px 18px;
                background: linear-gradient(135deg, rgba(0, 209, 255, 0.15) 0%, rgba(124, 77, 255, 0.1) 100%);
                border-bottom: 1px solid rgba(0, 209, 255, 0.2);
            }}
            
            .tooltip-icon {{ font-size: 1.3em; }}
            
            .tooltip-term {{
                font-weight: 600;
                color: #00D1FF;
                flex: 1;
                font-size: 14px;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}
            
            .tooltip-close {{
                cursor: pointer;
                color: #666;
                font-size: 22px;
                width: 28px;
                height: 28px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 8px;
                transition: all 0.15s ease;
            }}
            
            .tooltip-close:hover {{
                background: rgba(255, 82, 82, 0.15);
                color: #FF5252;
            }}
            
            .tooltip-content {{
                padding: 16px 18px;
                color: #E0E0E0;
                font-size: 14px;
                line-height: 1.65;
            }}
            
            .loading {{
                display: flex;
                align-items: center;
                gap: 12px;
                color: #888;
            }}
            
            .loading-dots {{
                display: flex;
                gap: 5px;
            }}
            
            .loading-dots span {{
                width: 8px;
                height: 8px;
                background: #00D1FF;
                border-radius: 50%;
                animation: dotBounce 1.4s ease-in-out infinite;
            }}
            
            .loading-dots span:nth-child(2) {{ animation-delay: 0.16s; }}
            .loading-dots span:nth-child(3) {{ animation-delay: 0.32s; }}
            
            @keyframes dotBounce {{
                0%, 80%, 100% {{ transform: scale(0.7); opacity: 0.4; }}
                40% {{ transform: scale(1.2); opacity: 1; }}
            }}
        </style>
    </head>
    <body>
        <div id="content">{styled_html}</div>
        
        <script>
            const API_KEY = "{js_api_key}";
            let tooltip = null;
            
            function removeTooltip() {{
                if (tooltip) {{
                    tooltip.style.animation = 'tooltipFadeOut 0.15s ease forwards';
                    setTimeout(() => {{ if (tooltip) {{ tooltip.remove(); tooltip = null; }} }}, 150);
                }}
            }}
            
            // Add fade out animation
            const style = document.createElement('style');
            style.textContent = `@keyframes tooltipFadeOut {{ from {{ opacity: 1; }} to {{ opacity: 0; transform: translateY(8px); }} }}`;
            document.head.appendChild(style);
            
            async function getDefinition(term) {{
                if (!API_KEY) return {{ error: "API key not configured" }};
                
                try {{
                    const res = await fetch(
                        'https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=AIzaSyA9NxKDmjUYgTqN5CK4la-VhbpxmG91E7Y',
                        {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{
                                contents: [{{ parts: [{{ text: `Define briefly in 1-2 simple sentences for a student: ${{term}}` }}] }}],
                                generationConfig: {{ temperature: 0.3, maxOutputTokens: 120 }}
                            }})
                        }}
                    );
                    
                    if (!res.ok) {{
                        const errData = await res.json().catch(() => ({{}}));
                        throw new Error(errData.error?.message || 'API unavailable');
                    }}
                    
                    const data = await res.json();
                    return {{ success: data.candidates?.[0]?.content?.parts?.[0]?.text?.trim() || "No definition available" }};
                }} catch (e) {{
                    // Graceful error message for professional UI
                    return {{ error: "Limit reached. Try again tomorrow." }};
                }}
            }}
            
            function createTooltip(x, y, text) {{
                removeTooltip();
                
                const t = document.createElement('div');
                t.className = 'ai-tooltip';
                t.style.left = Math.min(x + 15, window.innerWidth - 400) + 'px';
                t.style.top = (y + 220 > window.innerHeight ? Math.max(y - 200, 10) : y + 20) + 'px';
                
                const displayText = text.length > 35 ? text.substring(0, 35) + '...' : text;
                
                t.innerHTML = `
                    <div class="tooltip-header">
                        <span class="tooltip-icon">📖</span>
                        <span class="tooltip-term">${{displayText}}</span>
                        <span class="tooltip-close" onclick="removeTooltip()">×</span>
                    </div>
                    <div class="tooltip-content">
                        <div class="loading">
                            <div class="loading-dots"><span></span><span></span><span></span></div>
                            <span>Getting definition...</span>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(t);
                tooltip = t;
                
                getDefinition(text).then(r => {{
                    if (!tooltip) return;
                    const c = tooltip.querySelector('.tooltip-content');
                    c.innerHTML = r.success 
                        ? `<div style="color:#E0E0E0">${{r.success}}</div>`
                        : `<div style="color:#FF5252">⚠️ ${{r.error}}</div>`;
                }});
            }}
            
            document.addEventListener('mouseup', e => {{
                setTimeout(() => {{
                    const sel = window.getSelection().toString().trim();
                    if (sel.length >= 2 && sel.length <= 120 && (!tooltip || !tooltip.contains(e.target))) {{
                        createTooltip(e.clientX, e.clientY, sel);
                    }}
                }}, 50);
            }});
            
            document.addEventListener('mousedown', e => {{
                if (tooltip && !tooltip.contains(e.target) && !window.getSelection().toString().trim()) {{
                    removeTooltip();
                }}
            }});
            
            document.addEventListener('keydown', e => {{ if (e.key === 'Escape') removeTooltip(); }});
        </script>
    </body>
    </html>
    '''

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Initialize session state
    if "active_subject" not in st.session_state:
        st.session_state.active_subject = None
    if "markdown_content" not in st.session_state:
        st.session_state.markdown_content = ""
    if "app_mode" not in st.session_state:
        st.session_state.app_mode = "Editor"
    if "library_subject" not in st.session_state:
        st.session_state.library_subject = None
    if "library_unit" not in st.session_state:
        st.session_state.library_unit = None
    if "note_editor" not in st.session_state:
        st.session_state.note_editor = ""
    
    # Ensure root directory exists
    ensure_root_dir()
    
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    # =========================================================================
    # SIDEBAR
    # =========================================================================
    with st.sidebar:
        st.markdown('<div style="text-align: center; margin-bottom: 20px;">', unsafe_allow_html=True)
        st.markdown("# 📚 Unit-Sync")
        st.markdown("*Hierarchical Note Manager*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 1. NAVIGATION (Mode)
        st.markdown("### 🧭 Navigation")
        app_mode = st.radio(
            "Mode",
            ["✏️ Editor", "📖 Library"],
            label_visibility="collapsed",
            horizontal=True,
            key="mode_radio"
        )
        st.session_state.app_mode = app_mode
        st.markdown("---")
        
        # 2. CONTEXT (Selection)
        subjects = get_subjects()
        st.markdown("### 🎯 Active Context")
        
        if subjects:
            # Subject Select
            selected_subject = st.selectbox(
                "📂 Subject",
                subjects,
                index=subjects.index(st.session_state.active_subject) if st.session_state.active_subject in subjects else 0,
                key="subject_select"
            )
            st.session_state.active_subject = selected_subject
            
            # Unit Select
            selected_unit = st.selectbox(
                "📄 Unit",
                list(range(1, MAX_UNITS + 1)),
                format_func=lambda x: f"Unit {x}",
                key="unit_select"
            )
            
            # Write Mode (Only show in Editor)
            if app_mode == "✏️ Editor":
                st.markdown("#### ✍️ Write settings")
                write_mode = st.radio(
                    "Mode",
                    ["Append", "Overwrite"],
                    horizontal=True,
                    label_visibility="collapsed",
                    key="write_mode",
                    help="Append: Add to existing PDF | Overwrite: Replace entire PDF"
                )
        else:
            selected_subject = None
            selected_unit = 1
            write_mode = "Append"
            st.info("⚠️ No subjects found. Create one below.")

        st.markdown("---")

        # 3. MANAGEMENT ACTIONS (Expanders)
        st.markdown("### 🛠️ Management")
        
        with st.expander("➕ Create New Subject", expanded=not subjects):
            new_subject = st.text_input("Name", placeholder="e.g., CyberSecurity...", key="new_subject_input")
            if st.button("Create Subject", use_container_width=True, type="primary"):
                if new_subject:
                    success, msg = create_subject(new_subject)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Enter a name")

        if selected_subject:
            with st.expander(f"⚙️ Manage '{selected_subject}'", expanded=False):
                # Rename
                st.caption("Rename Subject")
                rename_col1, rename_col2 = st.columns([2, 1])
                new_name = rename_col1.text_input("New Name", label_visibility="collapsed", placeholder="New name...", key="rename_sbj_input")
                if rename_col2.button("Rename", key="rename_btn"):
                    if new_name:
                        s, m = rename_subject(selected_subject, new_name)
                        if s: 
                            st.success(m) 
                            st.rerun()
                        else: st.error(m)
                
                st.divider()
                
                # Delete Subject
                if st.button("�️ Delete Entire Subject", type="primary", use_container_width=True):
                    st.session_state.confirm_delete_subject = True
                
                if st.session_state.get("confirm_delete_subject"):
                    st.error("Are you sure? This deletes ALL units!")
                    d_col1, d_col2 = st.columns(2)
                    if d_col1.button("Yes, Delete"):
                        delete_subject(selected_subject)
                        st.session_state.confirm_delete_subject = False
                        st.session_state.active_subject = None
                        st.rerun()
                    if d_col2.button("Cancel"):
                        st.session_state.confirm_delete_subject = False
                        st.rerun()

            with st.expander("📄 Manage Units", expanded=False):
                unit_files = get_unit_files(selected_subject)
                if unit_files:
                    st.caption(f"Existing Units in {selected_subject}")
                    # List units with delete buttons
                    unit_to_del = st.selectbox("Select to delete", [u['unit'] for u in unit_files], format_func=lambda x: f"Unit {x}", key="del_unit_sel")
                    
                    if st.button(f"🗑️ Delete Unit {unit_to_del}", use_container_width=True):
                        delete_unit(selected_subject, unit_to_del)
                        st.success(f"Deleted Unit {unit_to_del}")
                        st.rerun()
                else:
                    st.info("No units created yet.")
        
        st.markdown("---")
        
        # 4. STATS
        if subjects:
            total_units = sum(len(get_unit_files(s)) for s in subjects)
            st.caption(f"📊 Stats: {len(subjects)} Subjects | {total_units} Units")
            
        # 5. CLOUD SYNC
        st.markdown("---")
        with st.expander("☁️ Cloud Sync Setup"):
            st.caption("Sync notes to GitHub for mobile access")
            
            # Use secrets if available, else session state
            token_val = st.secrets.get("GITHUB_TOKEN", "") if "GITHUB_TOKEN" in st.secrets else st.session_state.get("gh_token", "")
            repo_val = st.secrets.get("GITHUB_REPO", "") if "GITHUB_REPO" in st.secrets else st.session_state.get("gh_repo", "")
            
            gh_token = st.text_input("GitHub Token", value=token_val, type="password", key="gh_token_input")
            gh_repo = st.text_input("Repository (user/repo)", value=repo_val, key="gh_repo_input")
            
            if st.button("Save Credentials"):
                if gh_token and gh_repo:
                    st.session_state.gh_token = gh_token
                    st.session_state.gh_repo = gh_repo
                    st.success("Credentials Saved!")
                else:
                    st.error("Missing fields")
            
            if st.session_state.get("gh_token") or "GITHUB_TOKEN" in st.secrets:
                st.success(f"✅ Ready to Sync")

    
    # =========================================================================
    # MAIN CONTENT
    # =========================================================================
    st.markdown('<h1 class="main-header">📚 Unit-Sync</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Hierarchical Note Consolidation Tool</p>', unsafe_allow_html=True)
    
    # =========================================================================
    # LIBRARY MODE
    # =========================================================================
    if st.session_state.app_mode == "📖 Library":
        subjects = get_subjects()
        
        if not subjects:
            st.info("📚 Your library is empty! Switch to Editor mode and create some notes.")
            return
        
        st.markdown("### 📚 Your Library")
        st.markdown("*Browse your notes and use Select-to-Define to learn*")
        st.markdown("---")
        
        # Subject selection for Library
        lib_col1, lib_col2 = st.columns([1, 3])
        
        with lib_col1:
            st.markdown("#### 📂 Subjects")
            for subj in subjects:
                units_count = len(get_unit_files(subj))
                if st.button(f"📁 {subj} ({units_count})", key=f"lib_subj_{subj}", use_container_width=True):
                    st.session_state.library_subject = subj
                    st.session_state.library_unit = None
                    st.rerun()
            
            # Show units for selected subject
            if st.session_state.library_subject:
                st.markdown("---")
                st.markdown(f"#### 📄 Units in {st.session_state.library_subject}")
                units = get_unit_files(st.session_state.library_subject)
                if units:
                    for u in units:
                        if st.button(f"� Unit {u['unit']} ({u['size']})", key=f"lib_unit_{u['unit']}", use_container_width=True):
                            st.session_state.library_unit = u['unit']
                            st.rerun()
                else:
                    st.markdown("*No PDF units yet*")
        
        with lib_col2:
            if st.session_state.library_subject and st.session_state.library_unit:
                # Reader view - PDF Display
                st.markdown(f"#### 📖 {st.session_state.library_subject} - Unit {st.session_state.library_unit}")
                st.markdown("*Your PDF notes*")
                
                # Get PDF as base64 and embed
                pdf_data = get_pdf_base64(st.session_state.library_subject, st.session_state.library_unit)
                
                if pdf_data:
                    # Embed PDF viewer
                    pdf_display = f'''
                    <iframe 
                        src="data:application/pdf;base64,{pdf_data}" 
                        width="100%" 
                        height="750px" 
                        type="application/pdf"
                        style="border: 1px solid #333; border-radius: 8px;">
                    </iframe>
                    '''
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.warning("PDF not available. Try creating notes first.")
            elif st.session_state.library_subject:
                st.info(f"👈 Select a unit from **{st.session_state.library_subject}** to view the PDF")
            else:
                st.info("👈 Select a subject to browse your notes")
        
        return
    
    # =========================================================================
    # EDITOR MODE (Original functionality)
    # =========================================================================
    if not selected_subject:
        st.info("👈 Create a subject in the sidebar to get started!")
        return
    
    # Current context
    st.markdown(f"**Active:** `{selected_subject}` → **Unit {selected_unit}**")
    
    # Editor and Preview columns
    col1, col2 = st.columns([1, 1], gap="medium")
    
    with col1:
        st.markdown("### ✏️ Note Editor")
        st.markdown("*Paste your Markdown notes here*")
        
        markdown_input = st.text_area(
            "Markdown Editor",
            height=400,
            label_visibility="collapsed",
            placeholder="# Your Notes Here\n\nPaste notes from Gemini, ChatGPT, or write your own...",
            key="note_editor"
        )
        
        # Callbacks for cleaner state management
        def clear_editor_callback():
            st.session_state.note_editor = ""
            
        def update_pdf_callback():
             if st.session_state.note_editor.strip():
                try:
                    is_overwrite = (write_mode == "Overwrite")
                    success, msg = consolidate_pdf(selected_subject, selected_unit, st.session_state.note_editor, overwrite=is_overwrite)
                    if success:
                        st.success(msg)
                        st.session_state.note_editor = ""
                        
                        # --- GITHUB SYNC ---
                        token = st.session_state.get("gh_token") or (st.secrets["GITHUB_TOKEN"] if "GITHUB_TOKEN" in st.secrets else None)
                        repo = st.session_state.get("gh_repo") or (st.secrets["GITHUB_REPO"] if "GITHUB_REPO" in st.secrets else None)
                        
                        if GithubSync and token and repo:
                            try:
                                syncer = GithubSync(token, repo)
                                pdf_path = ROOT_DIR / selected_subject / f"Unit_{selected_unit}.pdf"
                                ok, s_msg = syncer.push_file(pdf_path, f"Update {selected_subject} Unit {selected_unit}")
                                if ok: 
                                    st.toast(f"☁️ Synced to GitHub")
                                else: 
                                    st.error(f"Cloud Error: {s_msg}")
                            except Exception as sync_e:
                                st.error(f"Sync Failed: {sync_e}")
                        # -------------------
                    else:
                        st.error(msg)
                except Exception as e:
                    st.error(f"Error: {e}")
             else:
                st.warning("Enter some notes first!")

        # Action buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            # Determine button text based on mode
            mode_text = "Overwrite" if write_mode == "Overwrite" else "Append to"
            st.button(f"� {mode_text} Unit PDF", use_container_width=True, type="primary", on_click=update_pdf_callback)
        
        with btn_col2:
            st.button("🗑️ Clear", use_container_width=True, on_click=clear_editor_callback)
    
    with col2:
        st.markdown("### 👁️ Live Preview")
        st.markdown("*Select text to get AI definitions*")
        
        if markdown_input.strip():
            html_content = markdown2.markdown(
                markdown_input,
                extras=["fenced-code-blocks", "tables", "strike", "header-ids"]
            )
        else:
            html_content = "<p style='color: #666;'>Start typing to see preview...</p>"
        
        # API key hardcoded (user added it in code)
        api_key = "AIzaSyA9NxKDmjUYgTqN5CK4la-VhbpxmG91E7Y"
        preview_html = get_preview_html(html_content, api_key)
        
        components.html(preview_html, height=450, scrolling=True)
    
    # Download existing PDF
    st.markdown("---")
    unit_path = ROOT_DIR / selected_subject / f"Unit_{selected_unit}.pdf"
    if unit_path.exists():
        with open(unit_path, "rb") as f:
            pdf_data = f.read()
        st.download_button(
            f"⬇️ Download Unit {selected_unit} PDF",
            data=pdf_data,
            file_name=f"{selected_subject}_Unit_{selected_unit}.pdf",
            mime="application/pdf"
        )

# =============================================================================
# ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    main()
