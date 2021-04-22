import os
import logging
import telegram
from PIL import Image
from typing import Dict
from telegram.ext import Updater, CommandHandler

import image_utils
import text_utils
import utils
from random_data import Retriever


class Bot(object):
    MAX_LINE_LENGTH = 40
    MAX_IMAGE_SHORTEST_SIZE = 2160

    START_MESSAGE = "Hello, I am a bot, nice to meet you. You may use /help to read what my commands do."
    # Each command is a tuple: (name, usage, explanation).
    COMMANDS = [
        ("frame", "/frame <text>",
         "Provide text or reply to a message. Text will be put on random stock image with random font.")
    ]

    def __init__(self, bot_name: str, token: str, retriever: Retriever, custom_commands: Dict[str, str]):
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
        self._updater.dispatcher.add_handler(CommandHandler("frame", self._frame_callback))

        for command, text in custom_commands.items():
            self._updater.dispatcher.add_handler(CommandHandler(
                # Set custom callback.
                command, lambda up, co, c=command, t=text: self._custom_callback(c, t, up, co)
            ))

        # Build help message.
        self._help_message = f"*{self._bot_name}*\n"

        # Default list.
        for _, usage, explanation in Bot.COMMANDS:
            self._help_message += f"\n{usage}\n{explanation}\n"

        # Custom command list.
        self._help_message += f"\n*Custom Commands*\n"
        for command, text in custom_commands.items():
            self._help_message += f"\n/{command} : \"{text}\"\n"

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

    def _frame_callback(self, update: telegram.Update, context: telegram.ext.CallbackContext):
        """
        Callback for frame command. Take either text or the message that was replied to and send back image.
        """
        user = update.effective_chat.id

        # Text is everything except first word.
        text = update.message.text[len(update.message.text.split(' ')[0])::].lstrip()
        text = text_utils.split_text(text, Bot.MAX_LINE_LENGTH)

        if text:
            # Got text, send image.
            logging.info(f"Got /frame from {user} with text \"{text}\".")
            self._send_image(text, update, context)
        else:
            reply = update.message.reply_to_message
            if reply is None:
                # No text and message was not a reply. Bye bye.
                logging.info(f"Got /frame from {user} with no text or reply.")
                update.message.reply_text("Hey man, I'd like to help you but you gave me nothing to work on.")
            else:
                # Message was a reply.
                text = update.message.reply_to_message.text
                if text is None:
                    # Empty text -> either message was empty or the bot is set in privacy mode. Check BotFather.
                    logging.info(f"Sorry bruv, the message may be empty or my privacy mode might be enabled idk.")
                text = text_utils.split_text(text, Bot.MAX_LINE_LENGTH)
                logging.info(f"Got /frame from {user} which replied to \"{text}\".")
                self._send_image(text, update, context)

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
        logging.info(f"Will try to generate image for user {user}.")

        image_file, author, profile = self._retriever.random_image()
        image = Image.open(image_file)
        # Resize to avoid breaching Telegram size limit.
        if min(image.size) > Bot.MAX_IMAGE_SHORTEST_SIZE:
            image = image_utils.min_resize(image, Bot.MAX_IMAGE_SHORTEST_SIZE)

        # Try multiple fonts in case you get a faulty one.
        result = None
        while True:
            font = self._retriever.random_font()
            try:
                result = image_utils.write(image, text, font, 10.0)
                break
            except TypeError:
                continue

        result.save(image_file)
        logging.info(f"Generated image {image_file} ({os.path.getsize(image_file)} bytes) for user {user}.")

        # Send back image with attribution caption.
        with open(image_file, 'rb') as f:
            context.bot.send_photo(
                chat_id=user, photo=f, parse_mode="markdown", reply_to_message_id=update.message.message_id,
                caption=utils.markdown_attribution(self._bot_name, author, profile)
            )

        logging.info(f"Sent image to user {user}.")

    def __del__(self):
        # Stop za bot.
        self._updater.stop()


class AdvancedBot(object):
    MAX_LINE_LENGTH = 40
    MAX_IMAGE_SHORTEST_SIZE = 2160

    START_MESSAGE = "Hello, I am a bot, nice to meet you. You may use /help to read what my commands do."
    # Each command is a tuple: (name, usage, explanation).
    COMMANDS = [
        ("frame", "/frame <text>",
         "Provide text or reply to a message. Text will be put on random stock image with random font.")
    ]

    def __init__(self, bot_name: str, token: str, retriever: Retriever, custom_commands: Dict[str, Dict]):
        """
        :param token: The token to run the bot on.
        :param retriever: The random data retriever.
        :param custom_commands: List of strings in the form "command text".
        """
        from command import make_command
        self._bot_name = bot_name
        self._retriever = retriever

        self._updater = Updater(token=token, use_context=True)
        self._updater.dispatcher.add_handler(CommandHandler("start", self._start_callback))
        self._updater.dispatcher.add_handler(CommandHandler("help", self._help_callback))
        self._updater.dispatcher.add_handler(make_command(
            self._bot_name, "frame", self._retriever
        ))

        for command, params in custom_commands.items():
            self._updater.dispatcher.add_handler(make_command(
                self._bot_name, command, self._retriever, **params
            ))

        # Build help message.
        self._help_message = f"*{self._bot_name}*\n"

        # Default list.
        for _, usage, explanation in Bot.COMMANDS:
            self._help_message += f"\n{usage}\n{explanation}\n"

        # Custom command list.
        self._help_message += f"\n*Custom Commands*\n"
        for command, params in custom_commands.items():
            description = params.get("description", None)
            self._help_message += f"\n/{command}" + (f" : \"{description}\"\n" if description else "\n")

        logging.info(f"\n{self._help_message}")
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

    def __del__(self):
        # Stop za bot.
        self._updater.stop()
