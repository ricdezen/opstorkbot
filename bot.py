import telegram
import logging
from telegram.ext import Updater, CommandHandler
from typing import Callable, List
from PIL import Image

import image_utils
import utils
from random_data import Retriever


class Bot(object):
    START_MESSAGE = "Hello, I am a bot, nice to meet you. You may use /help to read what my commands do."
    # Each command is a tuple: (name, usage, explanation).
    COMMANDS = [
        ("frame", "/frame <text>",
         "Provide text or reply to a message. Text will be put on random stock image with random font.")
    ]
    CUSTOM_COMMANDS = list()

    def __init__(self, bot_name: str, token: str, retriever: Retriever, custom_commands: List[str]):
        """
        :param token: The token to run the bot on.
        :param retriever: The random data retriever.
        :param custom_commands: List of strings in the form "command text".
        """
        self._bot_name = bot_name
        self._retriever = retriever

        self._updater = Updater(token=token, use_context=True)
        self._updater.dispatcher.add_handler(CommandHandler("start", self._start_callback))
        self._updater.dispatcher.add_handler(CommandHandler("help", self._help_callback))
        # TODO frame command.
        # self._updater.dispatcher.add_handler(CommandHandler("frame", self._frame_callback))

        for item in custom_commands:
            # "command_SPACE_text"
            command = item.split(' ')[0]
            text = item[len(command)::]
            self._updater.dispatcher.add_handler(CommandHandler(
                # Set custom callback.
                command, lambda up, co, c=command, t=text: self._custom_callback(c, t, up, co)
            ))

        # TODO make help message.
        self._help_message = "This is supposed to be the help message. But I have not set it up yet. Buzz off."

        logging.info(f"{self._bot_name} created.")

    def start(self):
        self._updater.start_polling()
        logging.info(f"{self._bot_name} started.")

    def idle(self):
        self._updater.idle()

    def _start_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for start command. Just answer with a basic message.
        """
        user = update.effective_chat.id
        context.bot.send_message(chat_id=user, text=self.START_MESSAGE)
        logging.info(f"/start command received by user: {user}.")

    def _help_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for help command. Send help message.
        """
        user = update.effective_chat.id
        context.bot.send_message(chat_id=user, text=self._help_message, parse_mode="markdown")
        logging.info(f"Sent help to user: {user}.")

    def _custom_callback(
            self, command: str, text: str,
            update: telegram.Update,
            context: telegram.ext.CallbackContext
    ):
        """
        You can make a lambda for a callback to this method with a specific text.

        :param command: The command that triggered the callback. Debug purposes.
        :param text: The text the image should contain.
        """
        user = update.effective_chat.id
        self._send_image(text, update, context)
        logging.info(f"Answered command {command} ({text}) of user {user} with an image.")

    def _send_image(
            self, text: str,
            update: telegram.Update,
            context: telegram.ext.CallbackContext
    ):
        """
        :param text: The text the image should contain.
        """
        user = update.effective_chat.id

        image_file, author, profile = self._retriever.random_image()
        image = Image.open(image_file)
        result = image_utils.write(
            image,
            text,
            self._retriever.random_font(),
            10.0
        )
        # TODO see if it makes sense to overwrite file.
        result.save(image_file)

        # Send back image with attribution caption.
        with open(image_file, 'rb') as f:
            context.bot.send_photo(
                chat_id=user, photo=f, parse_mode="markdown",
                caption=utils.markdown_attribution(self._bot_name, author, profile)
            )

    def __del__(self):
        # Stop za bot.
        self._updater.stop()
