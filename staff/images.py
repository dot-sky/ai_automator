import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests

from config.const import WAIT
from core.logger import log


def download_staff_images(staff_data, base_url, local_folder):
    log.title("Downloading staff images ")
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
    Path(local_folder).mkdir(parents=True, exist_ok=True)

    for member in staff_data:
        image_url = member.get("image_url", "").strip()

        if not image_url or image_url == 'N/A':
            continue

        # If the URL is relative, prepend the base domain
        if image_url.startswith("/"):
            image_url = base_url.rstrip("/") + image_url

        filename = get_image_file_name(member.get("name"), image_url)

        file_path = Path(local_folder) / filename
        try:
            # Download image
            response = requests.get(image_url, stream=True, timeout=WAIT.MEDIUM)
            response.raise_for_status()

            # Save to file
            with open(file_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            log.success(f"Downloaded {filename}")

        except requests.RequestException as e:
            log.error(f"Failed to download {image_url}: {e}")

    log.end_title()

def get_image_file_name(staff_name, image_url):
    parsed_url = urlparse(image_url)
    file_extension = os.path.splitext(parsed_url.path)[1] or ".jpg"

    # Create file path
    name = staff_name.replace(" ", "")
    filename = f"{name}{file_extension}"
    return filename

