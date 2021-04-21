import os
import logging
import telegram
import mimetypes
from telegram.ext import CommandHandler, CallbackContext
from moviepy.editor import VideoFileClip
from telegram import Update
from dataclasses import dataclass
from PIL import Image

import text_utils
import image_utils
import utils
from bot import Bot
from random_data import Retriever


def make_image(text: str, image_file: str, retriever: Retriever) -> str:
    """
    Saves the image found at image_file after resizing it based on `Bot.MAX_IMAGE_SHORTEST_SIZE` and printing the text
    on it.

    :param text: The text the image should contain.
    :param image_file: The image file.
    :param retriever: Used to get random fonts.
    :return: The path of the modified image file.
    """
    image = Image.open(image_file)
    # Resize to avoid breaching Telegram size limit.
    if min(image.size) > Bot.MAX_IMAGE_SHORTEST_SIZE:
        image = image_utils.min_resize(image, Bot.MAX_IMAGE_SHORTEST_SIZE)

    # Try multiple fonts in case you get a faulty one.
    result = None
    while True:
        font = retriever.random_font()
        try:
            result = image_utils.write(image, text, font, 10.0)
            break
        except TypeError:
            continue

    # Use same extension or default to .jpg
    _, suffix = os.path.splitext(image_file)
    new_file = utils.get_temp_file(suffix=suffix or '.jpg')
    result.save(new_file)

    return new_file


@dataclass()
class _Command(object):
    """
    Just a wrapper to make it easier to keep original parameters constant.
    """
    bot_name: str
    command_name: str
    retriever: Retriever
    text: str = None
    media_file: str = None
    low_color_key: str = None
    high_color_key: str = None

    def run(self, update: Update, context: CallbackContext):
        # Cache original parameters.
        bot_name = self.bot_name
        command_name = self.command_name
        retriever = self.retriever
        text = self.text
        media_file = self.media_file
        low_color_key = self.low_color_key
        high_color_key = self.high_color_key

        user = update.effective_chat.id

        # No text -> get text from the message's body.
        if text is None:
            # Try to get text from message body.
            text = update.message.text[len(update.message.text.split(' ')[0])::].lstrip()
            text = text_utils.split_text(text, Bot.MAX_LINE_LENGTH)

            # No body, check reply.
            if not text:
                reply = update.message.reply_to_message
                if reply:
                    # Message was a reply.
                    text = reply.text
                    if text is None:
                        # Empty text -> either message was empty or the bot is set in privacy mode. Check BotFather.
                        logging.info(f"Sorry bruv, the message may be empty or my privacy mode might be enabled idk.")
                    text = text_utils.split_text(text, Bot.MAX_LINE_LENGTH)
                    logging.info(f"Got /{command_name} from {user} which replied to \"{text}\".")
                else:
                    # No text and message was not a reply. Bye bye.
                    logging.info(f"Got /{command_name} from {user} with no text or reply.")
                    update.message.reply_text("Hey man, I'd like to help you but you gave me nothing to work on.")
                    return

        # No media -> get a random image.
        caption = None
        if media_file is None:
            logging.info(f"Command /{command_name} has no media. Will get random image for user {user}.")
            media_file, author, profile = retriever.random_image()
            caption = utils.markdown_attribution(bot_name, author, profile)

        # Decide what to do based on file type.
        media_type = utils.media_type(media_file)
        if media_type == "image":
            # Write the text on the image and send it back.
            result_file = make_image(text, media_file, retriever)
            image_bytes = os.path.getsize(result_file)
            logging.info(f"Generated image {result_file} ({image_bytes} bytes) for user {user}.")
            with open(result_file, 'rb') as f:
                context.bot.send_photo(
                    chat_id=user, photo=f, parse_mode="markdown", reply_to_message_id=update.message.message_id,
                    caption=caption
                )
            logging.info(f"Sent image to user {user}.")
        elif media_type == "video":
            # TODO videos bb.
            logging.error(f"Yes, uhm. This is where I would generate the video. If my idiot creator implemented it.")
            pass
        else:
            update.message.reply_text("I'm having trouble with this command's media. My hands are tied.")
            logging.error(f"I can't detect the media type of this file: {media_file}. I don't know what to do with it!")
            logging.error(f"Could not send media back to user {user}.")


def make_command(
        bot_name: str, command_name: str, retriever: Retriever, text: str = None, media_file: str = None,
        low_color_key: str = None, high_color_key: str = None
) -> CommandHandler:
    command = _Command(bot_name, command_name, retriever, text, media_file, low_color_key, high_color_key)
    return CommandHandler(command_name, command.run)
