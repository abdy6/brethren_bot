import discord
from discord.ext import commands
import definitions

class ServerConfig(commands.Cog):
    """Commands to configure guild specific settings."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="setlogchannel", help="Set the log channel for this server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_log_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        cfg = definitions.get_guild_config(ctx.guild.id)
        cfg.log_channel_id = channel.id
        definitions.save_config()
        await ctx.reply(f"Log channel set to {channel.mention}")

    @commands.hybrid_command(name="ignorechannel", help="Toggle logging for a channel.")
    @commands.has_guild_permissions(manage_guild=True)
    async def ignore_channel(self, ctx: commands.Context, channel: discord.TextChannel):
        cfg = definitions.get_guild_config(ctx.guild.id)
        if channel.id in cfg.ignored_channels:
            cfg.ignored_channels.remove(channel.id)
            action = "removed from"
        else:
            cfg.ignored_channels.append(channel.id)
            action = "added to"
        definitions.save_config()
        await ctx.reply(f"{channel.mention} {action} the ignore list")

    @commands.hybrid_command(name="ignoredchannels", help="List channels ignored by the logger.")
    async def list_ignored(self, ctx: commands.Context):
        cfg = definitions.get_guild_config(ctx.guild.id)
        if not cfg.ignored_channels:
            await ctx.reply("No ignored channels.")
            return
        channels = [f"<#{cid}>" for cid in cfg.ignored_channels]
        await ctx.reply("Ignored channels: " + ", ".join(channels))

async def setup(bot):
    await bot.add_cog(ServerConfig(bot))
