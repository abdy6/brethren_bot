import json
import logging
from discord.ext import commands

logger = logging.getLogger(__name__)


class GuildConfig:
    """Configuration specific to a Discord guild."""

    def __init__(self, data: dict | None = None):
        self.log_channel_id: int | None = None
        self.ignored_channels: list[int] = []

        if data:
            self.log_channel_id = data.get('log_channel_id')
            self.ignored_channels = data.get('ignored_channels', [])

    def to_dict(self) -> dict:
        return {
            'log_channel_id': self.log_channel_id,
            'ignored_channels': self.ignored_channels,
        }


class Config:
    def __init__(self, data: dict):
        self.command_prefix = data.get('command_prefix', ';')
        self.owner_id = data.get('owner_id', 424970840015110145)

        self.guilds: dict[int, GuildConfig] = {
            int(gid): GuildConfig(gcfg) for gid, gcfg in data.get('guilds', {}).items()
        }

    def to_dict(self) -> dict:
        return {
            'command_prefix': self.command_prefix,
            'owner_id': self.owner_id,
            'guilds': {str(gid): cfg.to_dict() for gid, cfg in self.guilds.items()},
        }

    def save(self, path: str = 'config.json') -> None:
        with open(path, 'w') as file:  # pylint: disable=unspecified-encoding
            json.dump(self.to_dict(), file, indent=4)


def load_config(path='config.json') -> Config:
    """Return the bot's configuration from ``path``."""
    with open(path, 'r') as file:  # pylint: disable=unspecified-encoding
        data = json.load(file)

    logger.debug("Loaded config: %s", data)
    print(f"Loaded config: {data}")
    return Config(data=data)


_config = load_config()

def get_guild_config(guild_id: int) -> GuildConfig:
    """Return the :class:`GuildConfig` for ``guild_id``.

    If a configuration entry does not exist yet for the guild it will be
    created and stored in memory (and will be written to disk on the next
    :func:`save_config` call).
    """
    if guild_id not in _config.guilds:
        _config.guilds[guild_id] = GuildConfig()
    return _config.guilds[guild_id]


def save_config(path: str = 'config.json') -> None:
    """Persist the current configuration to ``path``."""
    _config.save(path)

def is_bot_owner():
    """Check whether command issuer is me (adam.2006)"""
    def predicate(ctx):
        return ctx.message.author.id == _config.owner_id
    return commands.check(predicate)
