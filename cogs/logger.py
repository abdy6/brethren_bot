import discord
from discord.ext import commands
import logging
from typing import Optional
import definitions
import pprint

logger = logging.getLogger(__name__)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages: dict[int, discord.Message] = {} # {channel.id, message}
        self.sniped_messages_debug: dict[str, (str, str)] = {}
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None:
            return

        guild_cfg = definitions.get_guild_config(message.guild.id)

        if guild_cfg.log_channel_id is None:
            return

        if message.channel.id in guild_cfg.ignored_channels:
            return
        
        # Store deleted message for sniping
        self.sniped_messages[message.channel.id] = message
        self.sniped_messages_debug[message.channel.name] = (message.author.name, message.content)
        
        logger.debug(
            'Message deleted in channel %s: %s (%s): %s',
            message.channel.id,
            message.author.name,
            message.author.id,
            message.content
        )
        log_channel = message.guild.get_channel(guild_cfg.log_channel_id)
        if log_channel:
            embed = discord.Embed(
                title="Message Deleted",
                description=message.content or "*No text content*",
                color=discord.Color.red(),
                timestamp=message.created_at
            )
            embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
            embed.add_field(name="Channel", value=message.channel.mention)
            # embed.add_field(name="Message ID", value=message.id)
            # embed.add_field(name="Date sent", value=f"<t:{int(message.created_at.timestamp())}>")
            embed.set_footer(text=f"User ID: {message.author.id}")

            image_set = False
            attachment_links = []

            for attachment in message.attachments:
                # Add link for every attachment
                attachment_links.append(f"[{attachment.filename}]({attachment.url})")

                # Display the first image inline
                if not image_set and attachment.content_type and attachment.content_type.startswith("image/"):
                    embed.set_image(url=attachment.url)
                    image_set = True

            if attachment_links:
                embed.add_field(
                    name="Attachments",
                    value="\n".join(attachment_links),
                    inline=False
                )
                        
            await log_channel.send(embed=embed)
    
    
    @commands.hybrid_command(name="snipe", help="Show the most recently deleted message in this channel.")
    async def snipe(self, ctx: commands.Context):
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

        # Handle attachments
        image_set = False
        attachment_links = []

        for attachment in msg.attachments:
            attachment_links.append(f"[{attachment.filename}]({attachment.url})")

            if not image_set and attachment.content_type and attachment.content_type.startswith("image/"):
                embed.set_image(url=attachment.url)
                image_set = True

        if attachment_links:
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_links),
                inline=False
            )

        await ctx.send(embed=embed)
    
    # For debug purposes
    @commands.hybrid_command(name="snipelist", help="Show sniped message dictionary (debug)", aliases=['sl'])
    @definitions.is_bot_owner()
    async def snipelist(self, ctx):
        await ctx.send(f"```{pprint.pformat(self.sniped_messages_debug)}```")
    

async def setup(bot):
    await bot.add_cog(Logger(bot))
