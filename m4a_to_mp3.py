import subprocess
from pathlib import Path

INPUT_DIR = Path("m4a_files")
OUTPUT_DIR = Path("mp3_files")
BITRATE = "192k"

def batch_convert():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"Input folder not found: {INPUT_DIR}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    m4a_files = list(INPUT_DIR.glob("*.m4a"))

    if not m4a_files:
        print("No .m4a files found.")
        return

    for m4a in m4a_files:
        mp3 = OUTPUT_DIR / (m4a.stem + ".mp3")

        command = [
            "ffmpeg",
            "-y",
            "-i", str(m4a),
            "-vn",
            "-ab", BITRATE,
            "-ar", "44100",
            str(mp3)
        ]

        subprocess.run(command, check=True)
        print(f"Converted: {m4a.name} → {mp3.name}")

if __name__ == "__main__":
    batch_convert()
