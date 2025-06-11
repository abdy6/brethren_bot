from discord.ext import commands
from discord import app_commands
import math
import time

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Responds with pong.')
    async def ping(self, ctx):
        await ctx.send("Pong!")

    @commands.hybrid_command(name='uptime', description="Get the bot uptime.")
    async def uptime(self, ctx):
        uptime_seconds = math.floor(time.monotonic() - self.bot.monotonic_start_time)
        await ctx.reply(f"This bot has been online for {uptime_seconds} seconds.")

async def setup(bot):
    await bot.add_cog(General(bot))