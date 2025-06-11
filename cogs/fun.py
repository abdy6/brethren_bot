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

    @commands.hybrid_command(name='coinflip', description='Do a coin flip (50/50).', aliases=['cf'])
    async def coinflip(self, ctx):
        await ctx.reply(random.choice(["Heads", "Tails"]))
    
async def setup(bot):
    await bot.add_cog(Fun(bot))