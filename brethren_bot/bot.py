import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import definitions

load_dotenv()


extensions = [
    'brethren_bot.cogs.general'
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
            synced_commands = self.tree.sync()
            print(f"Synced {len(synced_commands)} commands: {[cmd.name for cmd in synced_commands]}")
        except Exception as e:
            print(e)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

def run_bot():
    token = os.getenv("BOT_TOKEN")
    bot = BrethrenBot()
    bot.run(token)