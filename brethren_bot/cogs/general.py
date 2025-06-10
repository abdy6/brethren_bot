from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='ping', description='Responds with pong')
    async def ping(self, ctx):
        await ctx.send("Pong!")

async def setup(bot):
    await bot.add_cog(General(bot))