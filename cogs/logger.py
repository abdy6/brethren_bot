import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        # Only messages deleted in the specified guild should be logged
        if message.guild is None or message.guild.id != self.bot.config.log_guild_id:
            return
        
        logger.debug(
            'Message deleted in channel %s: %s (%s): "%s"',
            message.channel.id,
            message.author.name,
            message.author.id,
            message.content
        )
        log_channel = message.guild.get_channel(self.bot.config.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="🗑️ Message Deleted",
                description=message.content or "*No text content*",
                color=discord.Color.red()
            )
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            embed.add_field(name="Channel", value=message.channel.mention)
            embed.set_footer(text=f"Message ID: {message.id}")
            await log_channel.send(embed=embed)
