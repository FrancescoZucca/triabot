import os
import re
import signal
import asyncio
import logging

from sys import stderr
from _utils import DecoratedHelpCommand
from pymongo import MongoClient
from discord.ext.commands import (
    Bot,
    has_guild_permissions
)
from cogs._utils import subscript


# the configured logger to use, to log all events.
logger = logging.getLogger()
logger.setLevel(os.getenv('DBOT_LOGLEVEL', logging.INFO))
logger.addHandler((hnd := logging.StreamHandler(stderr), hnd.setLevel(logging.DEBUG))[0])

bot_data = MongoClient(os.environ['DBOT_DATASTORE']).get_default_database()
bot_config = next(bot_data.configurations.find())

logger.info('Loaded configuration', bot_config)


def _get_prefix_or_default(guild):
    return subscript(bot_data.prefixes.find_one({'id': guild.id}),
                     'text', bot_config['default_prefix'])


def get_prefix(client, message):
    """Get bot prefix based on the guild configurations, also if the bot user was explicitly mentioned then
    regardless of the guild prefix it responds to the invoker."""

    # get the guild specific prefix or else default to the specified one defined
    # inside a environment variable (it must be defined there).
    prefixes = [_get_prefix_or_default(message.guild)]

    # if there was mention as a prefix then listen to that.
    if _prefix := subscript(re.match(rf'^(<@!{client.user.id}>\s*)', message.content), 0):
        prefixes.append(_prefix)

    return prefixes


# build the Bot for doing handling all the commands and listening to events.
bot = Bot(get_prefix, help_command=DecoratedHelpCommand())
bot.load_extension('cogs')

logger.info('Loaded bot categories %s' % ','.join(bot.cogs))
logger.info('Loaded bot commands %s' % ','.join(map(str, bot.commands)))

# set the data collections to access later on in commands, also the logger.
bot.metadata, bot.config, bot.logger = bot_data, bot_config, logger


@bot.command()
@has_guild_permissions(manage_guild=True)
async def prefix(ctx, text: str=None):
    """Get the current prefix for the guild, if provided one set it as prefix. Though the bot would respond to
    mentions no matter what prefix is set."""

    prev_prefix = _get_prefix_or_default(ctx.guild)

    if text:
        bot_data.prefixes.insert_one({'id': ctx.guild.id, 'text': text})
        await ctx.send(f"Guild prefix changed from `{prev_prefix}` to `{text}`")
    else:
        await ctx.send(f"Guild prefix is `{prev_prefix}`")


bot.run(bot_config['discord_token'])
bot_close = lambda: asyncio.run(bot.logout())

# register signal handlers to do clean up while exiting.
signal.signal(signal.SIGINT, bot_close)
signal.signal(signal.SIGABRT, bot_close)
signal.signal(signal.SIGTERM, bot_close)
