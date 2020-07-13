from discord import Embed
from discord.ext.menus import MenuPages, ListPageSource
from discord.ext.commands import Cog, Group, BucketType, HelpCommand

from cogs._utils import get_color

# replace newlines in a command/cog/group docstring to spaces.
format_description = lambda data: data.replace('\n', ' ') if data else None


class CogCommandPages(ListPageSource):
    def __init__(self, cog: Cog, prefix: str, *, per_page=3):
        if not isinstance(cog, Cog):
            raise TypeError("a valid cog wasn't passed")

        self._prefix = prefix
        self._doc = Embed(title=cog.qualified_name, description=cog.description, color=get_color())
        super().__init__(cog.get_commands(), per_page=per_page)

    async def format_page(self, _, commands):
        doc = self._doc.copy()

        for command in commands:
            doc.add_field(name=f'{self._prefix}{command.name} {command.signature}',
                          value=format_description(command.help))
        return doc


class GroupCommandPages(ListPageSource):
    def __init__(self, group: Group, prefix: str, *, per_page=3):
        if not isinstance(group, Group):
            raise TypeError("a valid group wasn't passed")

        self._prefix = prefix
        self._doc = Embed(title=f'{prefix}{group.name} {group.signature}',
                          description=format_description(group.help), color=get_color())
        super().__init__(self._flatten_commands(group.commands), per_page=per_page)

    @classmethod
    def _flatten_commands(cls, commands):
        """Flatten commands from a group traversing through all its command and subcommands."""

        def flatten(_commands, res=[]):
            for command_or_group in commands:
                if isinstance(command_or_group, Group):
                    flatten(command_or_group.commands, res)
                else:
                    res.append(command_or_group)

        output = []
        flatten(commands, output)
        return output

    def format_page(self, _, commands):
        doc = self._doc.copy()

        for command in commands:
            doc.add_field(name=f'{self._prefix}{command.qualified_name} {command.signature}',
                          value=format_description(command.help))
        return doc


class DecoratedHelpCommand(HelpCommand):
    async def send_bot_help(self, mapping):
        doc = Embed(color=get_color())
        for cog, commands in mapping.items():
            command_list = '\n'.join(f'{self.clean_prefix}{cmd}' for cmd in commands)

            if not cog:
                doc.description = command_list
            else:
                doc.add_field(name=cog.qualified_name, value=command_list, inline=False)

        await self.get_destination().send(embed=doc)

    async def send_cog_help(self, cog):
        await MenuPages(CogCommandPages(cog, self.clean_prefix)).start(self.context)

    async def send_command_help(self, command):
        doc = Embed.from_dict({
            'title': f'{self.clean_prefix}{command.name} {command.signature}',
            'description': command.help,
            'color': get_color().value
        })

        if command.aliases:
            doc.add_field(name='Aliases', inline=True,
                          value=', '.join(command.aliases))
        if command.cog:
            doc.add_field(name='Category', inline=True,
                          value=command.cog.qualified_name)

        if command._max_concurrency and getattr(command._max_concurrency, 'per', None) != BucketType.default:
            doc.add_field(name='Concurrency',
                          value='**%s** time(s) per **%s**' %
                            (command._max_concurrency.number, command._max_concurrency.per.name),
                          inline=True)

        await self.get_destination().send(embed=doc)

    async def send_group_help(self, group):
        await MenuPages(GroupCommandPages(group, self.clean_prefix)).start(self.context)
