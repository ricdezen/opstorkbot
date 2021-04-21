import json
import threading
import mimetypes
from pathlib import Path
from typing import Dict, Union, Optional
from tempfile import TemporaryDirectory, NamedTemporaryFile

mimetypes.init()

_STORAGE_FILE: Optional[str] = None
_STORAGE_LOCK = threading.Lock()
_TEMPORARY_DIRECTORY = TemporaryDirectory()


def set_storage(file: str):
    """
    Set file to read and write for persistent data.

    :param file: The file name.
    """
    global _STORAGE_FILE
    _STORAGE_FILE = file


def next_id() -> int:
    """
    Writes and reads to the set storage file to get and set the next id. In case of JSONDecodeError it sets the file to
    an empty dictionary.

    :return: Get the next unique id from the storage file and increment it.
    """
    # Get lock.
    global _STORAGE_LOCK
    _STORAGE_LOCK.acquire()

    # Lock acquired, get file.
    global _STORAGE_FILE

    if _STORAGE_FILE is None:
        _STORAGE_LOCK.release()
        raise RuntimeError("No storage file set.")

    with open(_STORAGE_FILE, 'r') as f:
        try:
            data = json.load(f)
        except json.decoder.JSONDecodeError as e:
            print("wot")
            data = dict()

    with open(_STORAGE_FILE, 'w+') as f:
        # Update value and write to file.
        next_value = (data["id"] + 1) if "id" in data else 0
        data["id"] = next_value
        json.dump(data, f)

    _STORAGE_LOCK.release()
    return next_value


def get_temp_file(suffix: str = None) -> str:
    """
    :return: Returns the name for a new temporary file.
    """
    global _TEMPORARY_DIRECTORY
    f = NamedTemporaryFile(suffix=suffix, dir=_TEMPORARY_DIRECTORY.name, delete=False)
    f.close()
    return f.name


def get_config(file: Union[str, Path]) -> Dict:
    """
    :param file: Name or Path object for the json config file.
    :return: A dict containing what the file contained. Empty dict if file did not exist.
    """
    # Make Path if got a string.
    if isinstance(file, str):
        file = Path(file)
    # If the file does not exist, return an empty dict.
    if not file.exists():
        return dict()

    # Read json file and return.
    with file.open() as f:
        data = json.load(f)
    return data


def markdown_attribution(app_name: str, author: str, profile_url: str) -> str:
    """
    :param app_name: This app's name.
    :param author: Author name.
    :param profile_url: The author's name.
    :return: Markdown string attributing the user at Unsplash for a photo.
    """
    unsplash = "https://unsplash.com/"
    params = f"?utm_source={app_name}&utm_medium=referral"
    return f"Photo by [{author}]({profile_url}{params}) @ [Unsplash]({unsplash}{params})"


def media_type(file: str) -> Optional[str]:
    """
    :param file: The media file.
    :return: 'video' or 'image' if the file is supposed to be a video or image respectively. Returns None otherwise.
    """
    mime = mimetypes.guess_type(file)[0]

    # Unknown or missing type.
    if mime is None:
        return None

    mime = mime.split('/')[0]
    if mime not in ["video", "image"]:
        mime = None
    return mime
