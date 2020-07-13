import random

from discord.ext.commands import BadArgument, Cog, group
from discord import Embed

from .memegen.reddit import RedditMeme
from ._utils import call, get_color


class Fun(Cog):
    """Actually funny things for a good laugh."""

    _generators = {}

    async def cog_before_invoke(self, ctx):
        self._generators.update({
            'reddit': RedditMeme(ctx.bot.config['reddit_clid'],
                                 ctx.bot.config['reddit_clsecret'])
        })

    @group(invoke_without_command=True)
    async def meme(self, ctx, site=None):
        """Fetch a meme from a defined or a random resource (always an image)"""

        if not site:
            site = random.choice([*self._generators.keys()])

        try:
            pic, info = self._generators[site]()
        except KeyError:
            raise BadArgument("Not a valid site from the list of sites")

        await ctx.send(embed=Embed.from_dict({
            'image': {'url': pic},
            'title': info.get('title', ''),
            'author': {'name': info.get('author', '')},
            'timestamp': call(getattr(info.get('creation'), 'isoformat', None), ''),
            'color': get_color().value
        }))

    @meme.command(name='list')
    async def list_generators(self, ctx):
        """List all the available generators to use a resource for memes"""

        await ctx.send(embed=Embed(
            description='\n'.join(map(str.title, self._generators.keys()))))


__cogexport__ = [Fun]
