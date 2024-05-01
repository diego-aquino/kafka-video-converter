import os
import uuid
import json
from kafka import KafkaProducer, KafkaConsumer

from constants import (
    KAFKA_BOOTSTRAP_SERVERS,
    VIDEO_DOWNLOAD_TOPIC,
    VIDEO_RESULT_TOPIC,
    VIDEO_CONVERSION_RESOLUTIONS,
)

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

video_result_consumer = KafkaConsumer(
    VIDEO_RESULT_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id="cli",
    enable_auto_commit=False,
)


def send_video_to_download(conversion_id, youtube_video_url):
    video_download_message = {
        "conversion_id": conversion_id,
        "youtube_video_url": youtube_video_url,
    }

    producer.send(
        VIDEO_DOWNLOAD_TOPIC,
        json.dumps(video_download_message).encode("utf-8"),
    )


def log_converted_video_results(conversion_id):
    pending_resolutions = set(VIDEO_CONVERSION_RESOLUTIONS)

    for message in video_result_consumer:
        video_result_message = json.loads(message.value.decode("utf-8"))

        if (
            "conversion_id" not in video_result_message
            or video_result_message["conversion_id"] != conversion_id
        ):
            continue

        resolution = video_result_message["resolution"]
        converted_video_file_name = os.path.basename(
            video_result_message["converted_video_path"]
        )
        print(f"    {converted_video_file_name}")

        if resolution in pending_resolutions:
            pending_resolutions.remove(resolution)

        video_result_consumer.commit()

        if len(pending_resolutions) == 0:
            break


def cli():
    try:
        while True:
            youtube_video_url = input("> YouTube video URL: ")

            conversion_id = str(uuid.uuid4())
            send_video_to_download(conversion_id, youtube_video_url)
            log_converted_video_results(conversion_id)

    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    cli()
