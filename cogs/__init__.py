from discord.ext.commands import Cog
from discord.ext.commands.errors import (
    BadArgument,
    CheckAnyFailure,
    CommandNotFound,
    CommandOnCooldown,
    NoPrivateMessage,
    MissingPermissions,
    UnexpectedQuoteError,
    BotMissingPermissions,
    MaxConcurrencyReached,
    MissingRequiredArgument,
    ExpectedClosingQuoteError,
    InvalidEndOfQuotedStringError,
)

from typing import Iterator
from itertools import chain
from importlib import import_module
from os.path import dirname, basename
from pathlib import Path
from ._utils import Filename
from traceback import print_exception


def _getall_cogs() -> Iterator[Cog]:
    """Collects all the cogs which are available in this module from all those python modules which have a
    :code:`__cogexport__` property in the global scope."""

    moddir_path = dirname(__file__)
    moddir_name = basename(moddir_path)

    def cogextract(module):
        module = import_module(f'.{module}', moddir_name)

        cogs = getattr(module, '__cogexport__', None)
        try:
            return [*filter(lambda cog: issubclass(cog, Cog), cogs)]
        except TypeError:
            return []

    return chain(*map(lambda mod: cogextract(Filename.from_str(mod).name),
                      Path(moddir_path).glob('*.py')))


def setup(bot):
    @bot.event
    async def on_command_error(ctx, exception):
        """Custom exception handler for Discord.py that handles exception(s), either send them
        to **stderr** for logging or as a Discord message to the invoker for information."""

        if isinstance(exception, (BadArgument, CommandNotFound, CommandOnCooldown, CheckAnyFailure, NoPrivateMessage,
                                  MissingPermissions, UnexpectedQuoteError, BotMissingPermissions,
                                  MaxConcurrencyReached, MissingRequiredArgument, ExpectedClosingQuoteError,
                                  InvalidEndOfQuotedStringError)):
            await ctx.send(str(exception))  # use the default text from exception.
        else:
            print_exception(exception.__class__, exception, exception.__traceback__)

    # extract all Cogs from files and add them to the bot.
    for cog in _getall_cogs():
        bot.add_cog(cog())
