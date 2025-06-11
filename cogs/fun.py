from discord.ext import commands
from discord import app_commands
import discord
import logging
import random
import asyncio
import definitions

logger = logging.getLogger(__name__)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    
async def setup(bot):
    await bot.add_cog(Fun(bot))