import logging
from typing import Optional, Tuple
import definitions
import pprint
import json
import datetime

import discord
from discord.ext import commands
from discord.ui import View, Button

logger = logging.getLogger(__name__)

class Logger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sniped_messages: dict[int, discord.Message] = {} # {channel.id, message}
        self.sniped_messages_debug: dict[str, Tuple[str, str]] = {}

        self.edited_messages: dict[int, Tuple[discord.Message, discord.Message]] = {}
        self.edited_messages_debug: dict[str, Tuple[str, str]] = {}
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild is None:
            return

        guild_cfg = definitions.get_guild_config(message.guild.id)
        # print("IGNORED:", guild_cfg.ignored_channels, "THIS:", message.channel.id)
        # print(type(guild_cfg.ignored_channels[0]))
        # print(f"ignored: {message.channel.id in guild_cfg.ignored_channels}")

        logger.debug(
            'Message deleted in channel %s: %s (%s): %s',
            message.channel.id,
            message.author.name,
            message.author.id,
            message.content
        )

        if guild_cfg.log_channel_id is None:
            return

        if message.channel.id in guild_cfg.ignored_channels:
            return

        # Store deleted message for sniping
        self.sniped_messages[message.channel.id] = message
        self.sniped_messages_debug[message.channel.name] = (message.author.name, message.content)

        attachments = [att.url for att in message.attachments]

        reply_author = None
        reply_content = None
        if message.reference and message.reference.message_id:
            try:
                ref = message.reference.resolved
                if ref is None:
                    ref = await message.channel.fetch_message(message.reference.message_id)
                reply_author = str(ref.author)
                reply_content = ref.content
            except Exception:  # pylint: disable=broad-except
                reply_author = "Unknown"
                reply_content = None

        await self.bot.db.store_snipe(
            channel_id=str(message.channel.id),
            message_id=str(message.id),
            author_id=str(message.author.id),
            author_name=str(message.author),
            content=message.content,
            created_at=message.created_at.timestamp(),
            attachments=json.dumps(attachments),
            reply_author=reply_author,
            reply_content=reply_content,
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
            if reply_author:
                reply_text = reply_content or "*No text content*"
                embed.add_field(
                    name="Replying to",
                    value=f"{reply_author}: {reply_text}",
                    inline=False
                )
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

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # only care about guild messages, non-bot, and real content changes
        if before.guild is None or before.author.bot:
            return
        if before.content == after.content:
            return

        guild_cfg = definitions.get_guild_config(before.guild.id)
        if guild_cfg.log_channel_id is None:
            return
        if before.channel.id in guild_cfg.ignored_channels:
            return

        # cache for editsnipe
        self.edited_messages[before.channel.id] = (before, after)
        self.edited_messages_debug[before.channel.name] = (before.content, after.content)

        attachments = [att.url for att in before.attachments]

        reply_author = None
        reply_content = None
        if before.reference and before.reference.message_id:
            try:
                ref = before.reference.resolved
                if ref is None:
                    ref = await before.channel.fetch_message(before.reference.message_id)
                reply_author = str(ref.author)
                reply_content = ref.content
            except Exception:  # pylint: disable=broad-except
                reply_author = "Unknown"
                reply_content = None

        await self.bot.db.store_edit_snipe(
            channel_id=str(before.channel.id),
            message_id=str(before.id),
            author_id=str(before.author.id),
            author_name=str(before.author),
            before_content=before.content,
            after_content=after.content,
            created_at=before.created_at.timestamp(),
            edited_at=(after.edited_at or after.created_at).timestamp(),
            attachments=json.dumps(attachments),
            reply_author=reply_author,
            reply_content=reply_content,
        )

        # send to your log channel
        log_channel = before.guild.get_channel(guild_cfg.log_channel_id)
        if not log_channel:
            return

        embed = discord.Embed(
            title="Message Edited",
            color=discord.Color.orange(),
            timestamp=after.edited_at or after.created_at
        )
        embed.set_author(name=str(before.author), icon_url=before.author.display_avatar.url)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)
        embed.add_field(
            name="Before",
            value=before.content or "*No text content*",
            inline=False
        )
        embed.add_field(
            name="After",
            value=after.content or "*No text content*",
            inline=False
        )
        if reply_author:
            reply_text = reply_content or "*No text content*"
            embed.add_field(
                name="Replying to",
                value=f"{reply_author}: {reply_text}",
                inline=False,
            )
        embed.set_footer(text=f"User ID: {before.author.id}")

        # build a View with a link button
        view = View()
        jump_url = f"https://discord.com/channels/{before.guild.id}/{before.channel.id}/{after.id}"
        view.add_item(
            Button(
                label="Jump to Message",
                style=discord.ButtonStyle.link,
                url=jump_url
            )
        )

        attachment_links = []
        image_set = False

        for url in attachments:
            attachment_links.append(f"[Attachment]({url})")
            if not image_set and any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                embed.set_image(url=url)
                image_set = True

        if attachment_links:
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_links),
                inline=False,
            )

        await log_channel.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="snipe", help="Show the most recently deleted message in this channel.")
    @commands.has_permissions(manage_messages=True)
    async def snipe(self, ctx: commands.Context):
        msg: Optional[discord.Message] = self.sniped_messages.get(ctx.channel.id)
        reply_author = None
        reply_content = None
        attachments = []

        if msg is None:
            row = await self.bot.db.get_snipe(str(ctx.channel.id))
            if row is None:
                await ctx.reply("There's nothing to snipe.")
                return

            (
                _msg_id,
                author_id,
                author_name,
                content,
                created_at,
                attach_json,
                reply_author,
                reply_content,
            ) = row

            attachments = json.loads(attach_json) if attach_json else []
            timestamp = datetime.datetime.fromtimestamp(created_at, tz=datetime.timezone.utc)

            user = ctx.guild.get_member(int(author_id))
            if user is None:
                try:
                    user = await self.bot.fetch_user(int(author_id))
                except Exception:  # pylint: disable=broad-except
                    user = None

            embed = discord.Embed(
                description=content or "*No text content*",
                color=discord.Color.red(),
                timestamp=timestamp,
            )
            if user:
                embed.set_author(name=str(user), icon_url=user.display_avatar.url)
            else:
                embed.set_author(name=author_name)
        else:
            content = msg.content
            attachments = [att.url for att in msg.attachments]
            timestamp = msg.created_at
            author_id = msg.author.id
            user = msg.author
            if msg.reference and msg.reference.message_id:
                try:
                    ref = msg.reference.resolved
                    if ref is None:
                        ref = await msg.channel.fetch_message(msg.reference.message_id)
                    reply_author = str(ref.author)
                    reply_content = ref.content
                except Exception:  # pylint: disable=broad-except
                    reply_author = "Unknown"

            embed = discord.Embed(
                description=content or "*No text content*",
                color=discord.Color.red(),
                timestamp=timestamp,
            )
            embed.set_author(name=str(user), icon_url=user.display_avatar.url)

        embed.set_footer(text=f"Sniped from #{ctx.channel.name}")

        # Handle attachments
        image_set = False
        attachment_links = []

        for url in attachments:
            attachment_links.append(f"[Attachment]({url})")
            if not image_set and any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                embed.set_image(url=url)
                image_set = True

        if attachment_links:
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_links),
                inline=False
            )

        if reply_author:
            reply_text = reply_content or "*No text content*"
            embed.add_field(
                name="Replying to",
                value=f"{reply_author}: {reply_text}",
                inline=False,
            )

        await ctx.send(embed=embed)
    
    @commands.hybrid_command(
        name="editsnipe", 
        help="Show the most recent edited message in this channel.",
        aliases=['esnipe']
    )
    @commands.has_permissions(manage_messages=True)
    async def editsnipe(self, ctx: commands.Context):
        pair = self.edited_messages.get(ctx.channel.id)
        reply_author = None
        reply_content = None
        attachments = []

        if pair is None:
            row = await self.bot.db.get_edit_snipe(str(ctx.channel.id))
            if row is None:
                await ctx.reply("There's nothing to editsnipe.")
                return

            (
                _msg_id,
                author_id,
                author_name,
                before_content,
                after_content,
                created_at,
                edited_at,
                attach_json,
                reply_author,
                reply_content,
            ) = row

            attachments = json.loads(attach_json) if attach_json else []
            timestamp = datetime.datetime.fromtimestamp(edited_at, tz=datetime.timezone.utc)

            user = ctx.guild.get_member(int(author_id))
            if user is None:
                try:
                    user = await self.bot.fetch_user(int(author_id))
                except Exception:  # pylint: disable=broad-except
                    user = None

            embed = discord.Embed(
                color=discord.Color.orange(),
                timestamp=timestamp,
            )
            if user:
                embed.set_author(name=str(user), icon_url=user.display_avatar.url)
            else:
                embed.set_author(name=author_name)
            embed.set_footer(text=f"Edited in #{ctx.channel.name}")
            embed.add_field(name="Before", value=before_content or "*No text content*", inline=False)
            embed.add_field(name="After", value=after_content or "*No text content*", inline=False)
        else:
            before, after = pair
            attachments = [att.url for att in before.attachments]
            timestamp = after.edited_at or after.created_at
            user = before.author
            if before.reference and before.reference.message_id:
                try:
                    ref = before.reference.resolved
                    if ref is None:
                        ref = await before.channel.fetch_message(before.reference.message_id)
                    reply_author = str(ref.author)
                    reply_content = ref.content
                except Exception:  # pylint: disable=broad-except
                    reply_author = "Unknown"

            embed = discord.Embed(
                color=discord.Color.orange(),
                timestamp=timestamp,
            )
            embed.set_author(name=str(user), icon_url=user.display_avatar.url)
            embed.set_footer(text=f"Edited in #{ctx.channel.name}")
            embed.add_field(name="Before", value=before.content or "*No text content*", inline=False)
            embed.add_field(name="After", value=after.content or "*No text content*", inline=False)

        if reply_author:
            reply_text = reply_content or "*No text content*"
            embed.add_field(
                name="Replying to",
                value=f"{reply_author}: {reply_text}",
                inline=False,
            )

        attachment_links = []
        image_set = False
        for url in attachments:
            attachment_links.append(f"[Attachment]({url})")
            if not image_set and any(url.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif"]):
                embed.set_image(url=url)
                image_set = True

        if attachment_links:
            embed.add_field(
                name="Attachments",
                value="\n".join(attachment_links),
                inline=False,
            )

        await ctx.send(embed=embed)

    # For debug purposes
    @commands.hybrid_command(name="snipelist", help="Show sniped message dictionary (debug)", aliases=['sl'])
    @definitions.is_bot_owner()
    async def snipelist(self, ctx):
        await ctx.send(f"```Deletes: {pprint.pformat(self.sniped_messages_debug)}\n"
                       f"Edits:   {pprint.pformat(self.edited_messages_debug)}```")
    

async def setup(bot):
    await bot.add_cog(Logger(bot))
