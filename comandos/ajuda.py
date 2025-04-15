import discord
from discord.ext import commands

class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ajuda", aliases=["h"], help="Mostra a lista de comandos disponíveis.")
    async def ajuda(self, ctx):
        prefixo = (await self.bot.get_prefix(ctx.message))[0]

        # Cria o embed
        embed = discord.Embed(
            title="**Lista de Comandos**",
            description=f"Aqui estão os comandos disponíveis no bot. Use-os com o prefixo `{prefixo}`.",
            color=discord.Color.blue()  # Escolha a cor que preferir
        )

        # Enumera os comandos
        comandos = ""
        for i, command in enumerate(self.bot.commands, 1):
            # Cada comando é listado com um índice e uma breve descrição
            comandos += f"**{i}.** `{prefixo}{command.name}` - {command.help or 'Sem descrição'}\n"
        
        embed.add_field(name="Comandos:", value=comandos, inline=False)

        # Envia o embed
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ajuda(bot))
