"""
classifier.py
-------------
This is our "intelligent" file classification system.
It uses simple rules (file extensions) to classify files.

This is the ML/AI part of the project — kept simple and rule-based.
No complicated models needed. Rule-based systems are fast, transparent,
and work perfectly for this use case.

File Categories:
  - image:    .jpg, .jpeg, .png, .gif, .bmp, .svg, .webp, .ico
  - code:     .py, .js, .ts, .html, .css, .java, .cpp, .c, .go, .rs, .sh, .json, .yaml
  - document: .pdf, .doc, .docx, .txt, .md, .xlsx, .csv, .pptx, .odt
  - video:    .mp4, .avi, .mov, .mkv, .webm
  - audio:    .mp3, .wav, .flac, .aac, .ogg
  - archive:  .zip, .tar, .gz, .rar, .7z
  - other:    everything else
"""

import os

# Define extension → category mapping
EXTENSION_MAP = {
    # Images
    ".jpg":  "image",
    ".jpeg": "image",
    ".png":  "image",
    ".gif":  "image",
    ".bmp":  "image",
    ".svg":  "image",
    ".webp": "image",
    ".ico":  "image",
    ".tiff": "image",
    ".heic": "image",

    # Code files
    ".py":   "code",
    ".js":   "code",
    ".ts":   "code",
    ".jsx":  "code",
    ".tsx":  "code",
    ".html": "code",
    ".css":  "code",
    ".java": "code",
    ".cpp":  "code",
    ".c":    "code",
    ".h":    "code",
    ".go":   "code",
    ".rs":   "code",
    ".sh":   "code",
    ".bash": "code",
    ".json": "code",
    ".yaml": "code",
    ".yml":  "code",
    ".xml":  "code",
    ".sql":  "code",
    ".php":  "code",
    ".rb":   "code",
    ".swift": "code",
    ".kt":   "code",

    # Documents
    ".pdf":  "document",
    ".doc":  "document",
    ".docx": "document",
    ".txt":  "document",
    ".md":   "document",
    ".xlsx": "document",
    ".xls":  "document",
    ".csv":  "document",
    ".pptx": "document",
    ".ppt":  "document",
    ".odt":  "document",
    ".rtf":  "document",

    # Videos
    ".mp4":  "video",
    ".avi":  "video",
    ".mov":  "video",
    ".mkv":  "video",
    ".webm": "video",
    ".flv":  "video",

    # Audio
    ".mp3":  "audio",
    ".wav":  "audio",
    ".flac": "audio",
    ".aac":  "audio",
    ".ogg":  "audio",
    ".m4a":  "audio",

    # Archives
    ".zip":  "archive",
    ".tar":  "archive",
    ".gz":   "archive",
    ".rar":  "archive",
    ".7z":   "archive",
    ".bz2":  "archive",
}

# Emoji icons for each category (used in frontend display)
CATEGORY_ICONS = {
    "image":    "🖼️",
    "code":     "💻",
    "document": "📄",
    "video":    "🎬",
    "audio":    "🎵",
    "archive":  "📦",
    "other":    "📎",
}


def classify_file(filename: str) -> str:
    """
    Classify a file based on its extension.
    
    This is the core "ML" logic — simple, fast, and accurate.
    Real-world note: You could replace this with a magic-byte reader
    (checks the actual binary content) for even more accuracy.
    
    Args:
        filename: The name of the file (e.g., "report.pdf")
    
    Returns:
        Category string: "image", "code", "document", "video", "audio", "archive", or "other"
    
    Examples:
        classify_file("photo.jpg")     → "image"
        classify_file("script.py")     → "code"
        classify_file("report.pdf")    → "document"
        classify_file("unknown.xyz")   → "other"
    """
    # Get the file extension (lowercased)
    _, ext = os.path.splitext(filename.lower())
    
    # Look it up in our map
    category = EXTENSION_MAP.get(ext, "other")
    
    print(f"[Classifier] {filename} → {category} (ext: {ext})")
    return category


def get_backup_priority(file_type: str, access_count: int) -> str:
    """
    Determine backup priority based on file type and access frequency.
    
    This is the "intelligent backup scheduling" logic:
    - High priority: backed up every hour
    - Medium priority: backed up every 6 hours  
    - Low priority: backed up once a day
    
    Rules:
    1. Frequently accessed files (>10 accesses) → High priority
    2. Code and documents → High priority (valuable data)
    3. Images accessed often → Medium priority
    4. Archives and rarely accessed files → Low priority
    
    Args:
        file_type: Category of the file
        access_count: How many times it's been downloaded
    
    Returns:
        Priority string: "high", "medium", or "low"
    """
    # Rule 1: Very frequently accessed files are high priority
    if access_count > 10:
        return "high"
    
    # Rule 2: Code and documents are always high priority (valuable!)
    if file_type in ("code", "document"):
        return "high"
    
    # Rule 3: Images with some accesses are medium priority
    if file_type == "image" and access_count > 2:
        return "medium"
    
    # Rule 4: Videos and audio — medium priority
    if file_type in ("video", "audio"):
        return "medium"
    
    # Default: low priority
    return "low"


def get_category_icon(file_type: str) -> str:
    """Return the emoji icon for a file category."""
    return CATEGORY_ICONS.get(file_type, "📎")