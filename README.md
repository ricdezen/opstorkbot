# StorkBot

> **WARNING**: Docs for the `develop` branch are not up to date.

Telegram bot made for fun for me and my friends. Allows framing a message or phrase onto a stock photo, taken
from [Unsplash](https://unsplash.com/) and using some random font from [Google Fonts](https://fonts.google.com/).

```gitignore
# Bot will reply with an image having the given text.
/frame [Your incredibly unoriginal Joe Mama joke.]

# Bot will use the text from the original message.
User 1: [Slightly funnier Joe Mama joke.]
    User 2 replies: /frame 
```

There is no guarantee I'll actually keep this bot public and/or running. The bot is registered as an Unsplash app in
demo version, meaning it only has 50 requests per hour. I allow and actually encourage you to take the code and host an
analogous bot somewhere of your liking.

## Setup

### Dependencies

This bot has a few external dependencies, found in `requirements.txt`:

- [Pillow](https://pillow.readthedocs.io/en/stable/): used for manipulating images.
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot): duh.

### Config

Since I have been using Unsplash for this, you need to sign up and register your app to get a key. In theory, you also
need to provide referrals when you use a picture, so I implemented that. Peek into the code if you want to disable that.

You will need a configuration file `config.json` in your working directory:

```json
{
  "bot_name": "Ideally the name of your app on Unsplash. Won't blow up if you use something else.",
  "bot_token": "your Telegram bot token, see: https://core.telegram.org/bots",
  "google_api_key": "your Google api key, see: https://developers.google.com/fonts/docs/developer_api",
  "unsplash_api_key": "your Unsplash access token, see: https://unsplash.com/documentation#creating-a-developer-account",
  "custom_commands": {
    "Joke 1": "Your group's inside joke that you don't want to type out every time.",
    "Use-no-spaces-in-the-key!-Cause-it-becomes-a-bot-command!": "Dun dun dun, another one bites the dust."
  }
}
```

Custom commands are basically a static reply. When the bot receives the command's name, it answers with a random
photo and font containing the text.

That's it, you should be good to go.
