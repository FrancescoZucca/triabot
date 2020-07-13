from urllib.parse import urlparse
from os.path import basename
from typing import NamedTuple

from discord import Colour
from random import choice
from itertools import zip_longest


def get_color() -> Colour:
    """Get a random :code:`Color` object."""

    return getattr(Colour, choice([
        'teal', 'dark_teal', 'green', 'dark_green', 'blue', 'dark_blue', 'purple', 'dark_purple', 'magenta',
        'dark_magenta', 'gold', 'dark_gold', 'orange', 'dark_orange', 'red', 'dark_red', 'lighter_grey',
        'darker_grey', 'blurple', 'greyple']))()


def get_member_color(member) -> Colour:
    """Get the final rendered color of a guild member as of its highest role."""
    return getattr(subscript(member.roles, -1), 'colour', None) or Colour.default()


def subscript(o, sub, default=None):
    """Safely subscript silencing :code:`KeyError` or :code:`IndexError`, if given a default return upon failure else
    :code:`None`."""

    try:
        return o[sub]
    except:
        return default


def call(func, default=None, *args, **kwargs):
    """Safely call a callable if fails or not callable returns the default."""

    if not callable(func):
        return default

    try:
        return func(*args, **kwargs)
    except:
        return default


def grouper(iterable, n, fixed=True, fillvalue=None):
    """Collect data as chunks or blocks, optionally fixed length."""

    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue) if fixed else zip(*args)


async def aenumerate(iterable, start=0):
    index = start
    async for element in iterable:
        yield index, element
        index += 1


class Filename(NamedTuple):
    """Represents a structure of a general filename, each filename has a optional extension to hint about the
    file-type without reading the file itself which is obviously for convenience purposes."""

    name: str
    ext: str

    @staticmethod
    def from_str(path: str):
        """Given a path-compatible string, it builds a filename object by extracting out the filename
        and discarding the whole path.

        :param path: file path to be used to build
        :return: an instance of this class
        """

        path = str(path)  # force convert to a string.
        name, _, ext = basename(path).rpartition('.')

        return Filename(name, ext)

    @staticmethod
    def from_url(url: str):
        """Same as `filename.from_str()` but constructs from a URL."""
        return Filename.from_str(urlparse(url)[2])

    def __str__(self):
        return f'{self.name}.{self.ext}'
