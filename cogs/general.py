from discord.ext import commands
from discord import app_commands
import discord
import math
import time
import datetime
import asyncio
import logging
import definitions
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Debug commands

    @commands.hybrid_command(name='ping', help='Check if the bot is online.')
    async def ping(self, ctx):
        logger.debug(f"Command ping called by user {ctx.author.name}, id: {ctx.author.id}")
        await ctx.reply(f"Pong! {(self.bot.latency * 1000):.2f} ms")

    @commands.hybrid_command(name='echo', help='Send the passed string in chat.')
    @app_commands.describe(message='What to send')
    @definitions.is_bot_owner()
    async def echo(self, ctx, *, message: str):
        await ctx.send(message)

    # See how long the bot has been online
    @commands.hybrid_command(
        name='uptime', 
        help="See how long the bot has been online.",
    )
    async def uptime(self, ctx):
        logger.debug(f"Command uptime called by user {ctx.author.name}, id: {ctx.author.id}")

        uptime_seconds = math.floor(time.monotonic() - self.bot.monotonic_start_time)
        days, rem = divmod(uptime_seconds, 86400)
        hours, rem = divmod(rem, 3600)           
        minutes, seconds = divmod(rem, 60)        

        parts = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        # Always show seconds (or if total was 0)
        if seconds or not parts:
            parts.append(f"{seconds}s")

        uptime_string = " ".join(parts)

        embed = discord.Embed(title='Bot uptime', color=discord.Color.darker_gray())
        embed.description = f'''__Start time:__ <t:{int(self.bot.start_time.timestamp())}>
        
        __Uptime:__ {uptime_string}
        __in seconds:__ {uptime_seconds}'''
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='shutdown', help="Shut down the bot.")
    @definitions.is_bot_owner()
    async def shutdown(self, ctx):
        await ctx.reply("Shutting down.")
        await self.bot.close()


    # Actually useful commands probably

    # Get a user's avatar (profile picture)
    @commands.hybrid_command(
        name='avatar',
        help='Show the avatar of a user (defaults to yourself).',
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
            "Command avatar called by user %s (id: %s) for target '%s' (id: %s)",
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
    @commands.hybrid_command(name="banner", help="Show a user's banner image")
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
    
    # Show general information about the guild.
    @commands.hybrid_command(
        name='serverinfo', 
        help="Show information about the server you're in.",
        aliases=['guildinfo', 'si']
    )
    async def serverinfo(self, ctx):
        guild = ctx.guild

        name = guild.name
        server_id = guild.id
        icon_url = guild.icon.url if guild.icon else "No icon"
        banner_url = guild.banner.url if guild.banner else "No banner"
        splash_url = guild.splash.url if guild.splash else "No splash"
        member_count = guild.member_count
        roles = [role.name for role in guild.roles]
        channels = guild.channels
        text_channels = guild.text_channels
        voice_channels = guild.voice_channels
        owner = guild.owner
        boost_level = guild.premium_tier
        boosters = guild.premium_subscription_count

        await ctx.send(
            f"```Server Name:    {name}\n"
            f"Server ID:      {server_id}\n"
            # f"Icon:           {icon_url}\n"
            f"Banner:         {banner_url}\n"
            f"Splash:         {splash_url}\n"
            f"Owner:          {owner}\n"
            f"Members:        {member_count}\n"
            f"Roles:          {len(roles)} roles\n"
            f"Text Channels:  {len(text_channels)}\n"
            f"Voice Channels: {len(voice_channels)}\n"
            f"Boost Level:    {boost_level}\n"
            f"Boosts:         {boosters}```"
        )

    @commands.hybrid_command(
        name="timeat",
        help="Get the time at the specified city."
    )
    async def timeat(self, ctx, *, city: str):
        """Returns current time in the specified city."""
        try:
            # normalize the key
            key = city.strip().lower()

            # look in cache first
            cached = await self.bot.db.get_cached_location(key)
            if cached:
                print(f"City {city} found in db")
                lat, lon, tz_name, resolved_name = cached

            else:
                #  ── HERE: apply override if present ──
                query = definitions.CITY_OVERRIDES.get(key, city)
                print(f"Geocoding query: {query!r} (requested: {city!r})")

                # blocking call → run in executor
                geolocator = Nominatim(user_agent="discord-time-bot")
                location = await asyncio.get_event_loop().run_in_executor(
                    None,
                    geolocator.geocode,
                    query
                )
                if not location:
                    print(f"Couldn't find city for query: {query}")
                    return await ctx.send(f"Could not find '{city}'.")

                lat, lon = location.latitude, location.longitude

                # pick a friendly resolved name
                # if we overrode, show the override; otherwise the full address
                # resolved_name = definitions.CITY_OVERRIDES.get(key, location.address)
                resolved_name = location.address

                tf = TimezoneFinder()
                tz_name = tf.timezone_at(lat=lat, lng=lon)
                if not tz_name:
                    return await ctx.send("Could not determine time zone for that location.")

                # cache under the normalized user‐input key
                await self.bot.db.store_cached_location(
                    key, lat, lon, tz_name, resolved_name
                )
                print(f"Stored city {city} ({resolved_name}) in db")

            # format and send
            now = datetime.datetime.now(ZoneInfo(tz_name))
            time_str = now.strftime("%Y-%m-%d %H:%M:%S")

            embed = discord.Embed(title="Time at Location")
            embed.add_field(name="Location", value=resolved_name, inline=False)
            embed.add_field(
                name="Time and Date",
                value=f"{now.strftime('%A, %B %d, %Y')}\n{now.strftime('%I:%M:%S %p')}",
                inline=False
            )

            await ctx.send(
                embed=embed
            )

        except GeocoderTimedOut:
            logger.exception("An error occurred in timeat")
            await ctx.send("Geocoder timed out.")
        except Exception as e:
            logger.exception("Something went wrong", exc_info=True)
            print(e)
            await ctx.send("Something went wrong, check logs.")

    @commands.hybrid_command(
        name="about",
        help="Get information about the bot."
    )
    async def about(self, ctx):
        count = len(self.bot.guilds)
        embed = discord.Embed(
            title="About Brethren Bot",
            color=discord.Color.dark_orange()
        )
        embed.description = f"Made by @a3dm on discord. I'm currently in `{count}` server{'s' if count != 1 else ''}."
        embed.add_field(name="GitHub", value="[Link](https://github.com/abdy6/brethren_bot)")
        embed.add_field(
            name="Socials", 
            value="[Twitter (X)](https://x.com/getinglouderig)\n" \
            "[Youtube](https://www.youtube.com/@abdyrobloxer)"
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/icons/1158077169348661330/975a3f58835f656e71d10ff61dfd2bd8.webp")
        
        await ctx.send(embed=embed)
    

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        # If the user lacked a required permission
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply("You don’t have permission to use this command.")
        # If a custom check failed (e.g. your own @commands.check predicate)
        elif isinstance(error, commands.CheckFailure):
            await ctx.reply("You don’t meet the requirements to run this command.")
        # Otherwise, re-raise so it can be logged or handled elsewhere
        else:
            raise error


async def setup(bot):
    await bot.add_cog(General(bot))
