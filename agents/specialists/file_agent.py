"""
agents/specialists/file_agent.py
Organises the local filesystem — categorises, moves, and cleans up files.
"""

from __future__ import annotations
import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

# Default download folder
DOWNLOADS = Path.home() / "Downloads"

# Category rules: extension -> target folder name
CATEGORIES = {
    "images":     [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico"],
    "videos":     [".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv"],
    "audio":      [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "documents":  [".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"],
    "spreadsheets": [".xls", ".xlsx", ".csv", ".ods"],
    "presentations": [".ppt", ".pptx", ".odp"],
    "archives":   [".zip", ".tar", ".gz", ".rar", ".7z"],
    "code":       [".py", ".js", ".ts", ".html", ".css", ".json", ".yml", ".yaml"],
    "installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm"],
}


async def organise_downloads(params: dict) -> dict:
    folder = Path(params.get("folder", str(DOWNLOADS)))
    delete_older_than_days = params.get("delete_older_than_days", 30)
    dry_run = params.get("dry_run", False)

    if not folder.exists():
        return {"error": f"Folder not found: {folder}"}

    moved = []
    deleted = []
    skipped = []
    cutoff = datetime.now() - timedelta(days=delete_older_than_days)

    for file in folder.iterdir():
        if not file.is_file():
            continue

        ext = file.suffix.lower()
        mtime = datetime.fromtimestamp(file.stat().st_mtime)

        # Delete old files
        if mtime < cutoff:
            if not dry_run:
                file.unlink()
            deleted.append(str(file.name))
            continue

        # Find category
        category = "misc"
        for cat, exts in CATEGORIES.items():
            if ext in exts:
                category = cat
                break

        target_dir = folder / category
        if not dry_run:
            target_dir.mkdir(exist_ok=True)
            shutil.move(str(file), str(target_dir / file.name))
        moved.append({"file": file.name, "category": category})

    logger.info("file.organised", moved=len(moved), deleted=len(deleted), dry_run=dry_run)
    return {
        "folder": str(folder),
        "moved": moved,
        "deleted": deleted,
        "dry_run": dry_run,
        "summary": f"Moved {len(moved)} files, deleted {len(deleted)} old files.",
    }
