import yt_dlp
import os

def download_tiktok(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(os.path.dirname(__file__), '%(title)s.%(ext)s'),
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        
def main():
    url = input("Enter the Tiktok URL: ")
    download_tiktok(url)

main()