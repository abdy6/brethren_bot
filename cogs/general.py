from discord.ext import commands
from discord import app_commands
import discord
import math
import time
import datetime
import logging
import definitions

logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Debug commands

    @commands.hybrid_command(name='ping', description='Check if the bot is online.')
    async def ping(self, ctx):
        logger.debug(f"Command 'ping' called by user '{ctx.author.name}', id: {ctx.author.id}")
        await ctx.reply(f"Pong! {(self.bot.latency * 1000):.2f} ms")

    @commands.hybrid_command(name='echo', description='Send the passed string in chat.')
    @app_commands.describe(message='What to send')
    @definitions.is_bot_owner()
    async def echo(self, ctx, *, message: str):
        await ctx.send(message)

    # See how long the bot has been online
    @commands.hybrid_command(
        name='uptime', 
        description="See how long the bot has been online.",
    )
    async def uptime(self, ctx):
        logger.debug(f"Command 'uptime' called by user '{ctx.author.name}', id: {ctx.author.id}")

        uptime_seconds = math.floor(time.monotonic() - self.bot.monotonic_start_time)
        embed = discord.Embed(title='Bot uptime', color=discord.Color.darker_gray())
        embed.description = f'''__Start time:__ <t:{int(self.bot.start_time.timestamp())}>
        
        __Uptime:__ {datetime.timedelta(seconds=uptime_seconds)}
        __in seconds:__ {uptime_seconds}'''
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='shutdown', description="Shut down the bot.")
    @definitions.is_bot_owner()
    async def shutdown(self, ctx):
        await ctx.reply("Shutting down.")
        await self.bot.close()


    # Actually useful commands probably

    # Get a user's avatar (profile picture)
    @commands.hybrid_command(
        name='avatar',
        description='Show the avatar of a user (defaults to yourself).',
        aliases=['av']
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
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=embed)
    
    # Fetch and show a user's banner.
    @commands.hybrid_command(name="banner", description="Show a user's banner image")
    @discord.app_commands.describe(user="User to get the banner of")
    async def banner(self, ctx, user: discord.User = None):
        user = user or ctx.author
        fetched_user = await self.bot.fetch_user(user.id)

        if fetched_user.banner:
            embed = discord.Embed(title=f"{fetched_user.name}'s Banner", color=discord.Color.darker_gray())
            embed.set_image(url=fetched_user.banner.url)
            embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                description=f"{fetched_user.name} does not have a banner.", 
                color=discord.Color.darker_gray()
            )
            embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
            await ctx.send(embed=embed)



async def setup(bot):
    await bot.add_cog(General(bot))
