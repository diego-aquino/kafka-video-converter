import os

KAFKA_HOSTNAME = "localhost"
KAFKA_PORT = "9092"
KAFKA_BOOTSTRAP_SERVERS = f"{KAFKA_HOSTNAME}:{KAFKA_PORT}"

VIDEO_DOWNLOAD_TOPIC = "video_downloads"
VIDEO_CONVERSION_TOPIC = "video_conversions"
VIDEO_RESULT_TOPIC = "video_results"

VIDEO_CONVERSION_RESOLUTIONS = ["1920:1080", "1280:720", "640:360", "256:144"]

VIDEO_DOWNLOAD_DIRECTORY = os.path.join(os.getcwd(), "videos", "downloads")
VIDEO_TEMPORARY_DIRECTORY = os.path.join(os.getcwd(), "videos", "tmp")
VIDEO_CONVERSION_DIRECTORY = os.path.join(os.getcwd(), "videos", "converted")
