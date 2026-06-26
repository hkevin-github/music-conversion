import sys
import yt_dlp

def download_soundcloud_mp3(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'mp3_files/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python soundcloud_to_mp3.py <soundcloud_link>")
        sys.exit(1)

    link = sys.argv[1]
    download_soundcloud_mp3(link)
