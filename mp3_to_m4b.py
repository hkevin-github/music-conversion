import os
import subprocess
from pathlib import Path

# ---------------------------------------------------
# SETTINGS
# ---------------------------------------------------

# Folder containing MP3s
INPUT_DIR = "mp3s"

# Output audiobook
OUTPUT_FILE = "Unnamable.m4b"

# Metadata
BOOK_TITLE = "The Unnamable"
AUTHOR = "Samuel Beckett"

# Cover image (.jpg or .png)
COVER_IMAGE = "cover.jpg"

# ---------------------------------------------------
# GET MP3 FILES
# ---------------------------------------------------

mp3_files = sorted(Path(INPUT_DIR).glob("*.mp3"))

if not mp3_files:
    raise ValueError("No MP3 files found.")

if not Path(COVER_IMAGE).exists():
    raise ValueError(f"Cover image not found: {COVER_IMAGE}")

# ---------------------------------------------------
# CREATE CONCAT FILE
# ---------------------------------------------------

with open("files.txt", "w", encoding="utf-8") as f:
    for mp3 in mp3_files:
        f.write(f"file '{mp3.resolve()}'\n")

# ---------------------------------------------------
# BUILD CHAPTER METADATA
# ---------------------------------------------------

current_ms = 0

metadata = [
    ";FFMETADATA1",
    f"title={BOOK_TITLE}",
    f"artist={AUTHOR}",
    f"album={BOOK_TITLE}",
    f"album_artist={AUTHOR}",
    "genre=Audiobook"
]

for mp3 in mp3_files:
    # Get duration using ffprobe
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            str(mp3)
        ],
        capture_output=True,
        text=True
    )

    duration_sec = float(result.stdout.strip())
    duration_ms = int(duration_sec * 1000)

    start = current_ms
    end = current_ms + duration_ms

    chapter_title = mp3.stem

    metadata.extend([
        "[CHAPTER]",
        "TIMEBASE=1/1000",
        f"START={start}",
        f"END={end}",
        f"title={chapter_title}"
    ])

    current_ms = end

with open("chapters.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(metadata))

# ---------------------------------------------------
# CREATE M4B
# ---------------------------------------------------

cmd = [
    "ffmpeg",
    "-y",

    # Audio files
    "-f", "concat",
    "-safe", "0",
    "-i", "files.txt",

    # Metadata / chapters
    "-i", "chapters.txt",

    # Cover image
    "-i", COVER_IMAGE,

    # Use metadata from chapters file
    "-map_metadata", "1",

    # Map audio + cover
    "-map", "0:a",
    "-map", "2",

    # Audio encoding
    "-c:a", "aac",
    "-b:a", "128k",

    # Cover art encoding
    "-c:v", "mjpeg",
    "-disposition:v", "attached_pic",

    OUTPUT_FILE
]

print("Running ffmpeg...")
subprocess.run(cmd, check=True)

print(f"\nCreated: {OUTPUT_FILE}")