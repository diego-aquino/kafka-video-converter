import sys
import json
from kafka import KafkaProducer, KafkaConsumer
from yt_dlp import YoutubeDL

from constants import (
    KAFKA_BOOTSTRAP_SERVERS,
    VIDEO_DOWNLOAD_TOPIC,
    VIDEO_CONVERSION_TOPIC,
    VIDEO_DOWNLOAD_DIRECTORY,
    VIDEO_TEMPORARY_DIRECTORY,
)

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

video_download_consumer = KafkaConsumer(
    VIDEO_DOWNLOAD_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id="downloader",
    enable_auto_commit=False,
)


def download_video(ydl, youtube_video_url):
    print(f"Downloading: '{youtube_video_url}'")
    download_code = ydl.download([youtube_video_url])

    if download_code == 1:
        print(
            f"Could not download video: {youtube_video_url}",
            file=sys.stderr,
        )
        return None

    print(f"Downloaded: '{youtube_video_url}'")
    video_path = ydl.prepare_filename(ydl.extract_info(youtube_video_url))
    return video_path


def send_video_to_conversion(conversion_id, video_path):
    video_conversion_message = {
        "conversion_id": conversion_id,
        "original_video_path": video_path,
    }

    producer.send(
        VIDEO_CONVERSION_TOPIC,
        json.dumps(video_conversion_message).encode("utf-8"),
    )


def run_video_downloader():

    with YoutubeDL(
        {
            "outtmpl": "%(title)s [%(id)s].%(ext)s",
            "paths": {
                "home": VIDEO_DOWNLOAD_DIRECTORY,
                "temp": VIDEO_TEMPORARY_DIRECTORY,
            },
            "quiet": True,
        }
    ) as ydl:
        try:
            print("Waiting for video download requests...")

            for message in video_download_consumer:
                video_download_message = json.loads(message.value.decode("utf-8"))
                youtube_video_url = video_download_message["youtube_video_url"]

                video_path = download_video(ydl, youtube_video_url)
                if video_path is None:
                    continue

                send_video_to_conversion(
                    video_download_message["conversion_id"], video_path
                )

                video_download_consumer.commit()

        except KeyboardInterrupt:
            return


if __name__ == "__main__":
    run_video_downloader()
