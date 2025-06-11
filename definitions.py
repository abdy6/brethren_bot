from discord.ext import commands


COMMAND_PREFIX = ";"


def is_bot_owner():
    """Check whether command issuer is me (adam.2006)"""
    def predicate(ctx):
        return ctx.message.author.id == 424970840015110145
    return commands.check(predicate)
