from pytube import YouTube
from sys import argv
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

link = argv[1]
yt = YouTube(link)

print("Title: ", yt.title)
print("Views: ", yt.views)

youtube_download = yt.streams.get_highest_resolution()

youtube_download.download("/Users/jasonojulari/Desktop/RAA-projects/API-Practice/mini-projects bvc")