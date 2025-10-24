# This script creates a simple Discord bot command that responds with "Pong!" when a user types "!ping".
# The only use is for bot testing purposes.
import discord
from discord.ext import commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="``Função de testes.``")
    async def ping(self, ctx):
        await ctx.send("🏓 Pong!")

async def setup(bot):
    await bot.add_cog(Ping(bot))
