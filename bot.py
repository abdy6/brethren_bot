import os
from dotenv import load_dotenv
import time
import datetime
import logging
from definitions import load_config, Config

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

load_dotenv()


extensions = [
    'cogs.general',
    'cogs.fun',
    # 'cogs.fun2',
]


class BrethrenBot(commands.Bot):
    """BrethrenBot class."""
    def __init__(self, bot_config: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        self.config = bot_config

        self.start_time = datetime.datetime.now()
        # Used to count the bot's uptime
        self.monotonic_start_time = time.monotonic()

        super().__init__(command_prefix=self.config.command_prefix, intents=intents)

    async def setup_hook(self):
        # Load cogs
        for ext in extensions:
            await self.load_extension(ext)
            print(f"Loaded extension {ext}")
            logger.debug(f"Loaded extension {ext}")

        try:
            synced_commands = await self.tree.sync()
            print(f"Synced {len(synced_commands)} commands: {[cmd.name for cmd in synced_commands]}")
            logger.debug("Synced %s commands: %s", len(synced_commands), [cmd.name for cmd in synced_commands])
        except Exception as e:
            logger.error("Error", exc_info=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")


if __name__ == '__main__':
    logging.basicConfig(
        filename='brethren_bot.log', 
        level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
    )
    config = load_config()

    token = os.getenv("BOT_TOKEN")
    bot = BrethrenBot(bot_config=config)
    bot.run(token)
