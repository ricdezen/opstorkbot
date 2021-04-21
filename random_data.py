import random
import requests
from typing import Tuple

import utils


class Retriever(object):
    """
    Tiny class to facilitate retrieving random fonts and images.
    Stores them into temporary files, deleted when the object is deleted.
    """

    def __init__(self, google_api_key: str, unsplash_api_key: str):
        """
        :param google_api_key: Used for Google Fonts api.
        :param unsplash_api_key: Used for Unsplash stock photos.
        """
        self._google_api_key = google_api_key
        self._unsplash_api_key = unsplash_api_key

        # Caching font list to heavily limit api calls.
        self._font_list = None
        self._font_requests = 0

    def random_font(self) -> str:
        """
        Downloads a font and provides a temporary file for it.

        :return: Filename for a random font from Google font.
        """
        self._get_font_list()

        # Choose and download random font.
        family = random.choice(self._font_list)
        font = random.choice(list(family["files"].items()))
        response = requests.get(font[1])

        if response.status_code != 200:
            raise RuntimeError(f"Could not retrieve font at {font[1]}")

        filename = utils.get_temp_file()
        with open(filename, 'wb') as f:
            f.write(response.content)

        return filename

    def random_image(self) -> Tuple[str, str, str]:
        """
        Download a random image and provide a temporary file for it.

        :return: Filename for a random image. Author name, author profile url.
        """
        url_params = {"client_id": self._unsplash_api_key}

        orientation = random.choice(["landscape", "portrait", "squarish"])
        meta = requests.get(f"https://api.unsplash.com/photos/random?orientation={orientation}", url_params).json()

        # Photo info.
        download_loc: str = meta["links"]["download_location"]
        author: str = meta["user"]["name"]
        profile: str = meta["user"]["links"]["html"]

        download_link = requests.get(download_loc, url_params).json()["url"]
        response = requests.get(download_link, url_params)

        filename = utils.get_temp_file(".jpg")
        with open(filename, 'wb') as f:
            f.write(response.content)

        return filename, author, profile

    def _get_font_list(self):
        """
        Update font list.
        """
        if self._font_list is not None:
            return
        response = requests.get(
            "https://www.googleapis.com/webfonts/v1/webfonts",
            {"key": self._google_api_key, "sort": "date"}
        )
        self._font_list = response.json()["items"]
