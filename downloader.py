import yt_dlp
import os

class VideoDownloader:
    def __init__(self):
        self.output_dir = "indirilenler"
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def download_segment(self, url, start_time, end_time):
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'external_downloader': 'ffmpeg',
            'external_downloader_args': {
                'ffmpeg_i': ['-ss', start_time, '-to', end_time]
            },
            'outtmpl': f'{self.output_dir}/%(title)s.%(ext)s',
            'quiet': True, # Terminal kalabalığını gizle
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            print(f"Hata: {e}")
            return False