import logging

import utils
from bot import AdvancedBot
from random_data import Retriever

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
try:
    # Try to add a lil colors.
    import coloredlogs

    coloredlogs.install(level='INFO')
except ImportError:
    logging.info("No colored logs :(")


def main():
    # Set storage file.
    utils.set_storage("storage")

    # Load basic info.
    config = utils.get_config("config.json")
    bot_name = config["bot_name"]
    bot_token = config["bot_token"]
    custom_commands = config["custom_commands"]
    google_api_key = config["google_api_key"]
    unsplash_api_key = config["unsplash_api_key"]
    del config

    r = Retriever(google_api_key, unsplash_api_key)
    bot = AdvancedBot(bot_name, bot_token, r, custom_commands)
    bot.start()
    bot.idle()


if __name__ == "__main__":
    main()
