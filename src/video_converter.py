import sys
import json
import os

from kafka import KafkaProducer, KafkaConsumer
import ffmpeg

from constants import (
    KAFKA_BOOTSTRAP_SERVERS,
    VIDEO_CONVERSION_TOPIC,
    VIDEO_RESULT_TOPIC,
    VIDEO_CONVERSION_RESOLUTIONS,
    VIDEO_CONVERSION_DIRECTORY,
)

producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

TARGET_RESOLUTION = sys.argv[1]

if TARGET_RESOLUTION not in VIDEO_CONVERSION_RESOLUTIONS:
    print(
        f"Invalid resolution '{TARGET_RESOLUTION}'. "
        + f"Available resolutions: {', '.join(VIDEO_CONVERSION_RESOLUTIONS)}",
        file=sys.stderr,
    )
    sys.exit(1)

video_conversion_consumer = KafkaConsumer(
    VIDEO_CONVERSION_TOPIC,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    group_id=f"converter-{TARGET_RESOLUTION}",
    enable_auto_commit=False,
)


def send_video_result(conversion_id, converted_video_path):
    video_result_message = {
        "conversion_id": conversion_id,
        "resolution": TARGET_RESOLUTION,
        "converted_video_path": converted_video_path,
    }

    producer.send(
        VIDEO_RESULT_TOPIC,
        json.dumps(video_result_message).encode("utf-8"),
    )


def convert_video(video_path):
    video_file_name = os.path.basename(video_path)
    video_file_name_without_extension = os.path.splitext(video_file_name)[0]

    converted_video_file_name = (
        f"{video_file_name_without_extension}.{TARGET_RESOLUTION.replace(':', 'x')}.mp4"
    )
    converted_video_path = os.path.join(
        VIDEO_CONVERSION_DIRECTORY, converted_video_file_name
    )

    conversion_stream = ffmpeg.input(video_path)
    conversion_stream = ffmpeg.output(
        conversion_stream,
        converted_video_path,
        vf=f"scale={TARGET_RESOLUTION}",
        acodec="copy",
        y=None,
        hide_banner=None,
        loglevel="error",
    )

    print(f"Converting: '{video_file_name}' to '{TARGET_RESOLUTION}'")
    ffmpeg.run(conversion_stream)
    print(f"Converted: '{video_file_name}' to '{TARGET_RESOLUTION}'")

    return converted_video_path


def run_video_converter():

    try:
        print("Waiting for video conversion requests...")

        for message in video_conversion_consumer:
            video_conversion_message = json.loads(message.value.decode("utf-8"))

            original_video_path = video_conversion_message["original_video_path"]
            converted_video_path = convert_video(original_video_path)

            send_video_result(
                video_conversion_message["conversion_id"],
                converted_video_path,
            )

            video_conversion_consumer.commit()

    except KeyboardInterrupt:
        return


if __name__ == "__main__":
    run_video_converter()
