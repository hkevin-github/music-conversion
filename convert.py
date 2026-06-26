#!/usr/bin/env python3
import argparse
import shutil
import subprocess
from pathlib import Path
import sys

try:
    import yt_dlp
except ImportError:
    yt_dlp = None

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None


def require_command(name):
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} is required but was not found in PATH.")


def convert_audio(input_path: Path, output_path: Path, bitrate: str = "192k"):
    require_command("ffmpeg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(input_path), "-vn", "-ab", bitrate, "-ar", "44100", str(output_path)],
        check=True,
    )
    print(f"Converted: {input_path.name} → {output_path.name}")


def convert_mp3_to_m4b(input_path: Path, output_path: Path, bitrate: str = "128k"):
    require_command("ffmpeg")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(input_path), "-c:a", "aac", "-b:a", bitrate, str(output_path)],
        check=True,
    )
    print(f"Converted: {input_path.name} → {output_path.name}")


def mp3_folder_to_m4b(input_dir: Path, output_path: Path, bitrate: str = "128k"):
    require_command("ffmpeg")
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Source folder not found: {input_dir}")

    mp3_files = sorted(input_dir.glob("*.mp3"))
    if not mp3_files:
        raise ValueError(f"No .mp3 files found in folder: {input_dir}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with input_dir.joinpath("files.txt").open("w", encoding="utf-8") as f:
        for mp3 in mp3_files:
            f.write(f"file '{mp3.resolve()}'\n")

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(input_dir / "files.txt"),
                "-c:a",
                "aac",
                "-b:a",
                bitrate,
                str(output_path),
            ],
            check=True,
        )
        print(f"Converted: {input_dir} → {output_path.name}")
    finally:
        try:
            (input_dir / "files.txt").unlink()
        except FileNotFoundError:
            pass


def download_mp3(url: str, output_dir: Path):
    if yt_dlp is None:
        raise RuntimeError("yt_dlp is required. Install it with: pip install yt-dlp")

    output_dir.mkdir(parents=True, exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(output_dir / "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


def pdf_to_markdown(input_path: Path, output_path: Path):
    if PdfReader is None:
        raise RuntimeError("PyPDF2 is required. Install it with: pip install PyPDF2")

    reader = PdfReader(str(input_path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())
        else:
            print(f"Warning: page {page_number} contains no extractable text.")

    content = "\n\n---\n\n".join(pages)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"Converted: {input_path.name} → {output_path.name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal converter for audio and PDF files.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    m4a = subparsers.add_parser("m4a-to-mp3", help="Convert a single .m4a file to .mp3")
    m4a.add_argument("input", type=Path, help="Source .m4a file")
    m4a.add_argument("output", type=Path, nargs="?", help="Output .mp3 file")
    m4a.add_argument("--bitrate", default="192k", help="Output bitrate for mp3")

    flac = subparsers.add_parser("flac-to-mp3", help="Convert a single .flac file to .mp3")
    flac.add_argument("input", type=Path, help="Source .flac file")
    flac.add_argument("output", type=Path, nargs="?", help="Output .mp3 file")
    flac.add_argument("--bitrate", default="192k", help="Output bitrate for mp3")

    mp3 = subparsers.add_parser("mp3-to-m4b", help="Convert a single .mp3 file to .m4b")
    mp3.add_argument("input", type=Path, help="Source .mp3 file")
    mp3.add_argument("output", type=Path, nargs="?", help="Output .m4b file")
    mp3.add_argument("--bitrate", default="128k", help="Output bitrate for m4b")

    mp3_folder = subparsers.add_parser("mp3-folder-to-m4b", help="Convert all .mp3 files in a folder into one .m4b")
    mp3_folder.add_argument("input_dir", type=Path, help="Source folder containing .mp3 files")
    mp3_folder.add_argument("output", type=Path, nargs="?", help="Output .m4b file")
    mp3_folder.add_argument("--bitrate", default="128k", help="Output bitrate for m4b")

    sc = subparsers.add_parser("soundcloud-to-mp3", help="Download SoundCloud URL as .mp3")
    sc.add_argument("url", help="SoundCloud track or playlist URL")
    sc.add_argument("--output-dir", type=Path, default=Path("mp3_files"), help="Directory for downloaded mp3 files")

    yt = subparsers.add_parser("youtube-to-mp3", help="Download YouTube URL as .mp3")
    yt.add_argument("url", help="YouTube video or playlist URL")
    yt.add_argument("--output-dir", type=Path, default=Path("mp3_files"), help="Directory for downloaded mp3 files")

    pdf = subparsers.add_parser("pdf-to-md", help="Convert PDF to Markdown")
    pdf.add_argument("input", type=Path, help="Source PDF file")
    pdf.add_argument("output", type=Path, nargs="?", help="Output Markdown file")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "m4a-to-mp3":
        output = args.output or args.input.with_suffix(".mp3")
        convert_audio(args.input, output, args.bitrate)

    elif args.command == "flac-to-mp3":
        output = args.output or args.input.with_suffix(".mp3")
        convert_audio(args.input, output, args.bitrate)

    elif args.command == "mp3-to-m4b":
        output = args.output or args.input.with_suffix(".m4b")
        convert_mp3_to_m4b(args.input, output, args.bitrate)

    elif args.command == "mp3-folder-to-m4b":
        output = args.output or args.input_dir.with_suffix(".m4b")
        mp3_folder_to_m4b(args.input_dir, output, args.bitrate)

    elif args.command == "soundcloud-to-mp3":
        download_mp3(args.url, args.output_dir)

    elif args.command == "youtube-to-mp3":
        download_mp3(args.url, args.output_dir)

    elif args.command == "pdf-to-md":
        output = args.output or args.input.with_suffix(".md")
        pdf_to_markdown(args.input, output)

    else:
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
