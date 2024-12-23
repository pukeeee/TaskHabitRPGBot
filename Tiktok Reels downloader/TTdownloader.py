import yt_dlp
import os

def downloadTiktokReels(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(os.path.dirname(__file__), '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        print(f"Video successfully uploaded!")
def main():
    url = input("Enter the Tiktok URL: ")
    downloadTiktokReels(url)

main()