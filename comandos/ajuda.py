import discord
from discord.ext import commands

class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda", help="``Mostra a lista de comandos disponíveis.``")
    async def ajuda(self, ctx):
        prefixo = (await self.bot.get_prefix(ctx.message))[0]
        comandos = ""
        for command in self.bot.commands:
            comandos += f"{prefixo}{command.name} {command.help or 'Sem descrição'}\n"

        await ctx.send(f"=== **Lista de comandos disponíveis** ===\n{comandos}============================")

async def setup(bot):
    await bot.add_cog(Ajuda(bot))

