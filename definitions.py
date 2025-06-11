import json
import logging
from discord.ext import commands

logger = logging.getLogger(__name__)


class Config:
    def __init__(self, data):
        self.command_prefix = data.get('command_prefix', ';') # Default value: ";"
        self.owner_id = data.get('owner_id', 424970840015110145) # Default owner: adam.2006


def load_config(path='config.json') -> Config:
    """Return the bot's configuration."""
    with open(path, 'r') as file:
        data = json.load(file)

    logger.debug(f"Loaded config: {data}")
    print(f"Loaded config: {data}")
    return Config(data=data)


_config = load_config()

def is_bot_owner():
    """Check whether command issuer is me (adam.2006)"""
    def predicate(ctx):
        return ctx.message.author.id == _config.owner_id
    return commands.check(predicate)
