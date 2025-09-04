import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

import requests

from config.const import WAIT
from core.logger import log


def download_staff_images(driver, staff_data, base_url, local_folder):
    log.title("Download Staff Photos")
    if os.path.exists(local_folder):
        shutil.rmtree(local_folder)
    Path(local_folder).mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])

    # Add headers so request looks like a real browser
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        ),
        "Referer": base_url,  
    })


    has_img = len(staff_data)
    downloaded = 0
    failed_download = []

    for member in staff_data:
        image_url = member.get("image_url", "").strip()

        if not image_url or image_url == 'N/A':
            has_img -= 1
            continue

        if image_url.startswith("/"):
            image_url = base_url.rstrip("/") + image_url

        filename = get_image_file_name(member.get("name"), image_url)

        file_path = Path(local_folder) / filename
        try:
            response = session.get(image_url, stream=True, timeout=WAIT.MEDIUM)
            response.raise_for_status()

            with open(file_path, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)

            log.success(f"Downloaded {filename}")
            downloaded += 1

        except requests.RequestException as e:
            log.error(f"Failed to download {image_url}: {e}")
            failed_download.append({
                "name": member.get("name"),
                "image_url": member.get("image_url")
            })

    log.plain(f"Downloaded {downloaded} of {has_img} images")
    if downloaded != has_img:
        raise Exception(f"Failed to download {len(failed_download)} images: {failed_download}")

    log.end_title()

def get_image_file_name(staff_name, image_url):
    parsed_url = urlparse(image_url)
    file_extension = os.path.splitext(parsed_url.path)[1] or ".jpg"

    # Create file path
    name = staff_name.replace(" ", "")
    filename = f"{name}{file_extension}"
    return filename

