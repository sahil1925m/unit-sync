# Unit-Sync - Folder Synchronization Guide

A hierarchical note consolidation tool for managing study notes by Subject and Unit.

## 📁 Directory Structure

When you use Unit-Sync, it creates a folder structure like this:

```
My_Study_Notes/                 ← Root directory (auto-created)
├── DBMS/                       ← Subject folder
│   ├── Unit_1.pdf              ← Consolidated notes
│   ├── Unit_2.pdf
│   └── Unit_3.pdf
├── Python/
│   ├── Unit_1.pdf
│   └── Unit_2.pdf
└── Operating_Systems/
    └── Unit_1.pdf
```

## 🔄 How Consolidation Works

### First Time Adding Notes to a Unit:
1. Select Subject (e.g., "DBMS")
2. Select Unit (e.g., "Unit 1")
3. Paste your Markdown notes
4. Click "Update Unit PDF"
5. **Result:** Creates `My_Study_Notes/DBMS/Unit_1.pdf`

### Adding More Notes to Same Unit:
1. Select the same Subject and Unit
2. Paste NEW notes (don't repeat old notes)
3. Click "Update Unit PDF"
4. **Result:** New notes are APPENDED to the end of the existing PDF

### Timestamp Headers
Every time you add notes, a timestamp header is automatically inserted:

```
───────────────────────────────
📅 Added on: December 25, 2025 at 01:15 AM
───────────────────────────────

[Your new notes appear here]
```

This helps you track when each section was added!

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

Then open `http://localhost:8501`

## 📋 Requirements

- `streamlit` - Web UI
- `pypdf` - PDF merging
- `markdown2` - Markdown parsing
- `xhtml2pdf` - PDF generation
- `google-generativeai` - AI definitions

## 💡 Tips

1. **One Subject = One Folder** - Keep related notes together
2. **Don't Duplicate** - Only add NEW notes; old ones are already in the PDF
3. **Use the Preview** - Check formatting before saving
4. **AI Definitions** - Highlight any term to get an instant explanation
