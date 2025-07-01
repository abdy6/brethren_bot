import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


class Leaderboard(commands.Cog):
    """
    Cog to track and report message counts per user using the shared Database instance.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return
        # Increment count in the database
        await self.bot.db.increment_message_count(
            guild_id=str(message.guild.id),
            user_id=str(message.author.id)
        )
        # Allow other cogs/commands to process this message
        # await self.bot.process_commands(message)

    @commands.hybrid_command(
        name="stats",
        help="Show message count for a user. Defaults to the author if no member is provided."
    )
    async def stats(self, ctx: commands.Context, member: discord.Member = None):
        target = member or ctx.author
        row = await self.bot.db.conn.execute(
            "SELECT message_count FROM message_counts WHERE guild_id = ? AND user_id = ?;",
            (str(ctx.guild.id), str(target.id))
        )
        result = await row.fetchone()
        count = result[0] if result else 0
        await ctx.send(f"{target.display_name} has sent {count} message{'s' if count != 1 else ''} in this server.")

    @commands.hybrid_command(
        name="leaderboard",
        help="""
        Display the top message senders in this server.
        Usage: !leaderboard [limit]
        """
    )
    async def leaderboard(self, ctx: commands.Context, limit: int = 10):
        
        rows = await self.bot.db.get_leaderboard(str(ctx.guild.id), limit=limit)
        if not rows:
            return await ctx.send("No message data available yet.")

        # Build a simple numbered list
        lines = []
        for i, (user_id, count) in enumerate(rows, start=1):
            member = ctx.guild.get_member(int(user_id))
            name = member.name if member else f"<@{user_id}>"
            lines.append(f"{i}. {name} - {count} messages")

        # Join and send as one message
        leaderboard_text = "\n".join(lines)
        await ctx.send(f"**Message Leaderboard**```\n{leaderboard_text}```")

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
