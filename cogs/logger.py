import discord
from discord.ext import commands
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages: dict[int, discord.Message] = {} # {channel.id, message}
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Only messages deleted in the specified guild should be logged
        if message.guild is None or message.guild.id != self.bot.config.log_guild_id:
            return
        
        # Store deleted message for sniping
        self.sniped_messages[message.channel.id] = message
        
        logger.debug(
            'Message deleted in channel %s: %s (%s): %s',
            message.channel.id,
            message.author.name,
            message.author.id,
            message.content
        )
        log_channel = message.guild.get_channel(self.bot.config.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Message Deleted",
                description=message.content or "*No text content*",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            embed.add_field(name="Channel", value=message.channel.mention)
            # embed.add_field(name="Date sent", value=f"<t:{int(message.created_at.timestamp())}>")
            embed.set_footer(text=f"Message ID: {message.id} - User ID: {message.author.id}")
            await log_channel.send(embed=embed)
    
    
    @commands.hybrid_command(name="snipe", help="Show the most recently deleted message in this channel.")
    async def snipe(self, ctx: commands.Context):
        print(f"Sniped messages: {self.sniped_messages}")
        msg: Optional[discord.Message] = self.sniped_messages.get(ctx.channel.id)
        if msg is None:
            await ctx.reply("There's nothing to snipe.")
            return

        embed = discord.Embed(
            description=msg.content or "*No text content*",
            color=discord.Color.red(),
            timestamp=msg.created_at
        )
        embed.set_author(name=str(msg.author), icon_url=msg.author.display_avatar.url)
        embed.set_footer(text=f"Sniped from #{ctx.channel.name}")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Logger(bot))
