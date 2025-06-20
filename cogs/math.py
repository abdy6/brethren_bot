import decimal
import fractions

import discord
from discord.ext import commands

class Math(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="multiply", help="Multiply two numbers.")
    async def multiply(
        self,
        ctx: commands.Context,
        x: str,
        y: str
    ):
        try:
            a = decimal.Decimal(x)
            b = decimal.Decimal(y)
        except decimal.InvalidOperation:
            await ctx.reply("`Invalid input`")
            return

        await ctx.reply(f"`{a * b}`")

    @commands.hybrid_command(name="divide", help="Divide two numbers.")
    async def divide(
        self,
        ctx: commands.Context,
        x: str,
        y: str
    ):
        try:
            a = decimal.Decimal(x)
            b = decimal.Decimal(y)
        except decimal.InvalidOperation:
            await ctx.reply("`Invalid input`")
            return
        
        if b == 0:
            await ctx.reply("`Can't divide by zero!`")
            return

        await ctx.reply(f"`{a / b}`")

    @commands.hybrid_command(
        name="tofraction",
        help="Convert a decimal to a fraction.",
        aliases=['tofrac']
    )
    async def decimal_to_fraction(
        self,
        ctx: commands.Context,
        value: str
    ):
        try:
            # Make sure it's a valid decimal
            decimal.Decimal(value)
            frac = fractions.Fraction(value).limit_denominator()
        except (decimal.InvalidOperation, ValueError, ZeroDivisionError):
            await ctx.reply("`Invalid input`")
            return

        await ctx.reply(f"`{frac}`")



async def setup(bot):
    await bot.add_cog(Math(bot))
