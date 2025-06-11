from discord.ext import commands
from discord import app_commands
import discord
import logging
import random
import asyncio
import datetime

logger = logging.getLogger(__name__)

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='coinflip', description='Do a coin flip (50/50).', aliases=['cf'])
    async def coinflip(self, ctx):
        await ctx.reply(random.choice(["Heads", "Tails"]))

    @commands.hybrid_command(
        name='random',
        description="Get a random number between a and b (inclusive).",
        aliases=['rand']
    )
    async def random_number(self, ctx, a: int, b: int):
        await ctx.reply(random.randint(a, b))
    

    @commands.hybrid_command(name='timer', description="Send a message after a certain amount of time.")
    async def timer(self, ctx, seconds: int):
        if seconds > 43200:
            await ctx.reply("Timer must be under 12 hours (43200 seconds)")
            return
        
        mention = ctx.author.mention
        future_ts = int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=seconds)).timestamp())
        embed = discord.Embed(
            title='Timer', 
            color=discord.Color.darker_gray(),
            description=f"You'll get a ping {seconds} seconds from now. (<t:{future_ts}> - <t:{future_ts}:R>)"
        )
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
        logger.debug("Timer set for %s seconds (%s) by %s (%s)", seconds, future_ts, ctx.author.name, ctx.author.id)
        await asyncio.sleep(seconds)
        await ctx.send(f"{mention} - Timer finished. ({seconds}s)")
    
async def setup(bot):
    await bot.add_cog(Fun(bot))
