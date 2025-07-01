import os
from dotenv import load_dotenv
import time
import datetime
import logging

from definitions import load_config, Config
from database import Database

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

load_dotenv()


extensions = [
    'cogs.general',
    'cogs.fun',
    # 'cogs.fun2',
    'cogs.logger',
    'cogs.math',
    'cogs.server_config',
    'cogs.leaderboard'
]


class BrethrenBot(commands.Bot):
    """BrethrenBot class."""
    def __init__(self, bot_config: Config):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        super().__init__(command_prefix=bot_config.command_prefix, intents=intents)

        self.config = bot_config
        self.db = Database()  # singleton DB manager
        self.start_time = datetime.datetime.now()
        self.monotonic_start_time = time.monotonic()

    async def setup_hook(self):
        await self.db.connect()

        # Load cogs
        for ext in extensions:
            await self.load_extension(ext)
            print(f"Loaded extension {ext}")
            logger.debug(f"Loaded extension {ext}")

        try:
            synced_commands = await self.tree.sync()
            print(f"Synced {len(synced_commands)} commands: {[cmd.name for cmd in synced_commands]}")
            logger.debug("Synced %s commands: %s", len(synced_commands), [cmd.name for cmd in synced_commands])
        except Exception as e: # pylint: disable=W0612,W0718
            logger.error("Error", exc_info=True)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def close(self):
        # Close the bot and the database connection
        await super().close()
        await self.db.close()


if __name__ == '__main__':
    logging.basicConfig(
        filename='brethren_bot.log', 
        level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
    )
    config = load_config()

    token = os.getenv("BOT_TOKEN")
    bot = BrethrenBot(bot_config=config)
    bot.run(token)
