import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import definitions
import time
import datetime

load_dotenv()


extensions = [
    'cogs.general'
]


class BrethrenBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=definitions.COMMAND_PREFIX, intents=intents)

    async def setup_hook(self):
        # Load cogs
        for ext in extensions:
            await self.load_extension(ext)
            print(f"Loaded extension {ext}")

        try:
            synced_commands = await self.tree.sync()
            print(f"Synced {len(synced_commands)} commands: {[cmd.name for cmd in synced_commands]}")
        except Exception as e:
            print(e)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        
        self.start_time = datetime.datetime.now()
        # Used to count the bot's uptime
        self.monotonic_start_time = time.monotonic()

def run_bot():
    token = os.getenv("BOT_TOKEN")
    bot = BrethrenBot()
    bot.run(token)