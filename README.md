# music-conversion

Minimal conversion utility for audio and PDF files.

Supported conversions:
- `.m4a` → `.mp3`
- `.flac` → `.mp3`
- `.mp3` → `.m4b`
- SoundCloud URLs → `.mp3`
- YouTube URLs → `.mp3`
- PDF → Markdown (`.md`)

Quick install:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install yt-dlp PyPDF2
```

Basic usage:
```bash
python convert.py m4a-to-mp3 path/to/song.m4a
python convert.py flac-to-mp3 path/to/song.flac
python convert.py mp3-to-m4b path/to/audio.mp3
python convert.py mp3-folder-to-m4b path/to/folder
python convert.py soundcloud-to-mp3 https://soundcloud.com/track
python convert.py youtube-to-mp3 https://youtube.com/watch?v=...
python convert.py pdf-to-md document.pdf
```

Notes:
- `ffmpeg` is required for audio conversions.
- Downloaded MP3 files are saved to `mp3_files/` by default.
