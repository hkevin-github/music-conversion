from pathlib import Path
from mutagen.id3 import ID3, APIC, error

# Folder containing MP3s
MP3_DIR = "mp3s"

# Single cover image used for ALL MP3s
COVER_IMAGE = "mp3s/162591-boxing-day.jpg"

mp3_files = list(Path(MP3_DIR).glob("*.mp3"))

if not mp3_files:
    raise ValueError("No MP3 files found.")

with open(COVER_IMAGE, "rb") as img:
    cover_data = img.read()

for mp3_path in mp3_files:
    try:
        audio = ID3(mp3_path)
    except error:
        audio = ID3()

    # Remove existing cover art
    audio.delall("APIC")

    # Add new cover art
    audio.add(
        APIC(
            encoding=3,          # UTF-8
            mime="image/jpeg",
            type=3,              # Front cover
            desc="Cover",
            data=cover_data
        )
    )

    audio.save(mp3_path)

    print(f"Tagged: {mp3_path.name}")

print("Done.")
