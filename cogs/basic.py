from discord.ext.commands import (
    Cog,
    BadArgument,
    group,
    command,
)

import random
from ._utils import grouper
from functools import reduce


class Basic(Cog):
    """Basic commands for doing mostly funny stuff."""

    @command()
    async def test(self, ctx):
        """Verify that the bot is usable, tells the current WebSocket delay"""

        await ctx.send(f"{round(ctx.bot.latency * 1000, 2)}ms")

    @command()
    async def random(self, ctx, min: float, max: float):
        """Generate a pseudorandom decimal in bound of (min..max]"""

        await ctx.send(random.uniform(min, max))

    @command()
    async def pick(self, ctx, *options):
        """Pick pseudorandomly from given list of options"""

        await ctx.send(random.choice(options))

    @command()
    async def space(self, ctx, spaces: int, *, text: str):
        """Spaces characters with a defined amount to emphasize a text"""

        if len(text) * spaces > 2000:
            raise BadArgument("Disallowing 2000 character limit of Discord")

        await ctx.send(''.join(c + ' ' * spaces for c in text))

    @command()
    async def altcap(self, ctx, *, text: str):
        """Randomly capitalizes each English letter of a text as if it was wrong in a ironic way"""

        await ctx.send(''.join(random.choice([c.upper, c.lower])() for c in text))

    @group(name='5igi0')
    async def sigio(self, _):
        """A morse-code like binary interchange format, that consists of `-` and `'` characters"""
        pass

    @sigio.command(name='encode')
    async def sigio_encode(self, ctx, *, text: str):
        """Encode from UTF-8 characters into 5IGI0 (maximum chars: 250)"""

        text = text.encode('utf-8')  # single-byte encoding.
        if len(text) * 8 > 2000:
            return

        await ctx.send(''.join(''.join("-'"[c >> b & 1] for b in range(7, -1, -1)) for c in text))

    @sigio.command(name='decode')
    async def sigio_decode(self, ctx, sigi0: str):
        """Decode from 5IGI0 to UTF-8 characters"""

        if len(sigi0) % 8 != 0:
            raise BadArgument("Input length isn't multiple of 8")

        data = bytes(reduce(lambda c, b: c | "-'".index(b[1]) << b[0], zip(range(7, -1, -1), bits), 0) for bits in
                     grouper(sigi0, 8))

        try:
            await ctx.send(data.decode('utf-8'))
        except UnicodeDecodeError:
            raise BadArgument("5IGI0 sequence cannot be converted using UTF-8")


__cogexport__ = [Basic]
