from discord.ext import commands
from discord import app_commands
import discord
import math
import time
import datetime
import logging

logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Check if the bot is online.')
    async def ping(self, ctx):
        logger.debug(f"Command 'ping' called by user '{ctx.author.name}', id: {ctx.author.id}")
        await ctx.reply("Pong!")

    # See how long the bot has been online
    @commands.hybrid_command(
        name='uptime', 
        description="See how long the bot has been online.",
    )
    async def uptime(self, ctx):
        logger.debug(f"Command 'uptime' called by user '{ctx.author.name}', id: {ctx.author.id}")

        uptime_seconds = math.floor(time.monotonic() - self.bot.monotonic_start_time)
        embed = discord.Embed(title='Bot uptime', color=discord.Color.darker_gray())
        embed.description = '''__Start time:__ <t:{math.floor(self.bot.start_time.timestamp())}>
        
        __Uptime:__ {datetime.timedelta(seconds=uptime_seconds)}
        __in seconds:__ {uptime_seconds}'''
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    
    # Get a user's avatar (profile picture)
    @commands.hybrid_command(
        name='avatar', 
        description='Show the avatar of a user (defaults to yourself).',
    )
    @app_commands.describe(user="The user to show the avatar for")
    async def avatar(
        self,
        ctx: commands.Context,
        user: discord.Member | discord.User | None = None
    ):
        target = user or ctx.author
        logger.debug(
            "Command 'avatar' called by user '%s' (id: %s) for target '%s' (id: %s)",
            ctx.author.name,
            ctx.author.id,
            target.name,
            target.id
        )

        embed = discord.Embed(
            title=f"{target.name}'s avatar",
            color=discord.Color.darker_gray()
        )
        embed.set_image(url=target.display_avatar.url)
        embed.set_footer(text=f'Requested by {ctx.author}', icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=embed)


async def setup(bot):
    await bot.add_cog(General(bot))