import os
from typing import Union
from text_utils import get_text_dimensions
from PIL import Image, ImageDraw, ImageFont, ImageStat


def min_resize(image: Image.Image, min_size: int) -> Image.Image:
    """
    :param image: An image to resize.
    :param min_size: The size of it's smallest dimension.
    :return: A copy of the image resized to have it's smallest dimension at `min_size`.
    """
    w, h = image.size
    # new_h : new_w = h : w
    if w > h:
        new_h = min_size
        new_w = int(min_size * w / h)
    else:
        new_w = min_size
        new_h = int(min_size * h / w)
    return image.resize((new_w, new_h))


def write(image: Image.Image, text: str, font_file: str, min_padding: Union[int, float] = 0) -> Image:
    """
    :param image: The image to write on. Tries to figure out colors to allow good contrast.
    :param text: The text to write on the image. Will attempt to fit it to the image, long lines may lead to small font
    size, use `split_text` if you need to split it.
    :param font_file: The font file to use. Mandatory, otherwise it is not possible to change font size.
    :param min_padding: The minimum padding to keep. int is interpreted as pixels, float as percentage.
    :return: The modified image.
    """
    # Copy the image to avoid modifying it.
    image = image.copy()
    draw = ImageDraw.Draw(image)
    width, height = image.size

    # TODO properly figure out colors.
    """
    mean_color = ImageStat.Stat(image).mean
    min_max = max(mean_color) + min(mean_color)
    comp_color = (
        int(min_max - mean_color[0]),
        int(min_max - mean_color[1]),
        int(min_max - mean_color[2])
    )
    """

    # Compute padding if needed.
    if isinstance(min_padding, int):
        pad_h = min_padding
        pad_v = min_padding
    elif isinstance(min_padding, float):
        pad_h = int(min_padding * width / 100)
        pad_v = int(min_padding * height / 100)
    else:
        raise TypeError("min_padding should be either int or float.")

    # Need to gradually increase font size to fit the sentence.
    ok_font = ImageFont.truetype(font_file)
    ok_size = 1
    # Reduce step to start off easy and slow down near limit.
    for step in [100, 50, 25, 10, 5, 1]:
        for size in range(ok_size, max(image.size), step):
            font = ImageFont.truetype(font_file, size=size)
            text_width, text_height = get_text_dimensions(text, font)
            if (width - text_width) < (2 * pad_h):
                break
            if (height - text_height) < (2 * pad_v):
                break
            # Font is ok at this size.
            ok_font = font
            ok_size = size

    x = image.size[0] / 2
    y = image.size[1] / 2

    # Border.
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Actual white text.
    draw.text(
        (x, y), text, font=ok_font, align='center', anchor="mm",
        stroke_width=max(ok_size // 50, 1), fill=white, stroke_fill=black
    )

    return image
