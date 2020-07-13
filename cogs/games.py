from discord.ext.commands import Cog, command, check
from random import choice
import time


def isSudo(ctx):
    return ctx.message.author.guild.get_role(703942219987419201) in ctx.message.author.roles or ctx.message.author.id == 314491790168424462


class Games(Cog):
    _hg_registeredList = []
    _isStarted = False

    async def start(self, ctx):
        self._isStarted = True
        await ctx.send("Game is starting...")
        while len(self._hg_registeredList) > 1:
            player = choice(self._hg_registeredList)
            if choice(["l", "l", "d"]) == "l":
                life = open("cogs/hg/life.txt", "r")
                lifeList = []
                for line in life:
                    lifeList.append(line)
                await ctx.send(choice(lifeList).replace("$PLAYERNAME", player.mention))
            else:
                death = open("cogs/hg/death.txt", "r")
                deathList = []
                for line in death:
                    deathList.append(line)
                await ctx.send(choice(deathList).replace("$PLAYERNAME", player.mention))
                self._hg_registeredList.remove(player)
            time.sleep(1)
        await ctx.send(self._hg_registeredList[0].mention + " wins!")
        self._isStarted = False

    @command(name="hg!register")
    async def hgRegister(self, ctx):
        if not self._isStarted:
            if not ctx.message.author in self._hg_registeredList:
                await ctx.send("Registered successfully!")
                self._hg_registeredList.append(ctx.message.author)
            else:
                await ctx.send("You're already registered!")
            if len(self._hg_registeredList) >= 4:
                await ctx.send("Starting game in 1 minute...")
                time.sleep(60)
                await self.start(ctx)
        else:
            await ctx.send("Game is already started! Please wait.")

    @command(name="hg!forceStart")
    @check(isSudo)
    async def forceStart(self, ctx):
        await ctx.send("Force starting!")
        await self.start(ctx)
