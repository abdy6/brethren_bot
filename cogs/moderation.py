import logging

import discord
from discord.ext import commands
from discord import app_commands

logger = logging.getLogger(__name__)

class Moderation(commands.Cog):
    """Cog for server moderation (kicking, banning, etc.)"""
    def __init__(self, bot):
        self.bot = bot


async def setup(bot):
    await bot.add_cog(Moderation(bot))
