import subprocess
from pathlib import Path

FLAC_DIR = Path("flac_files")
MP3_DIR = Path("mp3_files")
MP3_DIR.mkdir(exist_ok=True)

for flac in FLAC_DIR.glob("*.flac"):
    mp3 = MP3_DIR / (flac.stem + ".mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(flac), "-ab", "320k", str(mp3)],
        check=True
    )

print("Done! Check mp3_files/")
