import discord
from discord.ext import commands

# Comando ping separado
class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="``Função de testes.``")
    async def ping(self, ctx):
        await ctx.send("🏓 Pong!")

# Função para adicionar o Cog ao bot
async def setup(bot):
    await bot.add_cog(Ping(bot))
