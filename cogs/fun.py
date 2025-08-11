from discord.ext import commands
from discord import app_commands
import discord
import logging
import random
import asyncio
import datetime
import aiohttp
import io
from PIL import Image

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
            description=f"You'll get a ping {seconds} seconds from now. (<t:{future_ts}:R>)"
        )
        embed.set_footer(text=f'Requested by {ctx.author.name}', icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)
        logger.debug("Timer set for %s seconds (%s) by %s (%s)", seconds, future_ts, ctx.author.name, ctx.author.id)
        await asyncio.sleep(seconds)
        await ctx.send(f"{mention} - Timer finished. ({seconds}s)")

    @commands.command(name="togif", description="Reply to an image and convert it to a GIF.")
    async def togif(self, ctx):
        # Make sure user is replying to a message
        if not ctx.message.reference:
            return await ctx.send("You must reply to a message with an image!")

        try:
            replied_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        except Exception:
            return await ctx.send("Could not fetch the replied message.")

        if not replied_msg.attachments:
            return await ctx.send("The replied message has no attachments.")

        # Filter for image attachment
        attachment = next((a for a in replied_msg.attachments if a.filename.lower().endswith((".png", ".jpg", ".jpeg"))), None)
        if not attachment:
            return await ctx.send("No valid image found to convert, or the attachment is already a GIF.")

        # Download the image
        async with aiohttp.ClientSession() as session:
            async with session.get(attachment.url) as resp:
                if resp.status != 200:
                    return await ctx.send("Failed to download image.")
                data = await resp.read()

        try:
            img = Image.open(io.BytesIO(data)).convert("RGBA")
            output = io.BytesIO()
            img.save(output, format="GIF", save_all=True, loop=0)
            output.seek(0)
        except Exception as e:
            logger.exception("Exception in togif")
            print(e)
            return await ctx.send("Failed to convert image, check logs")

        # 6. Send the GIF back
        file = discord.File(fp=output, filename=f"converted_{datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S')}.gif")
        await ctx.reply(file=file)
    
async def setup(bot):
    await bot.add_cog(Fun(bot))
