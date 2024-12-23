import yt_dlp
import os

def download_and_convert_video(url):
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': os.path.join(os.path.dirname(__file__), '%(title)s.%(ext)s'),
        'merge_output_format': 'mp4',
        'postprocessors': [
            {
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            },
            {
                'key': 'FFmpegEmbedSubtitle',
            },
            {
                'key': 'FFmpegVideoRemuxer',
                'preferedformat': 'mp4',
            },
        ],
        'postprocessor_args': [
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-strict', 'experimental'
        ],
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            title = info_dict.get('title', 'video')
            print(f"Video '{title}' successfully uploaded!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    video_url = input("Enter a link to the YouTube video: ").strip()
    download_and_convert_video(video_url)