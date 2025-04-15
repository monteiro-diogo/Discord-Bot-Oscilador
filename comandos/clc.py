import discord
from discord.ext import commands
from datetime import datetime, timedelta

class Limpar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="clc",
        aliases=["clearchat"],
        help="Limpa mensagens. Uso: `!clc <num> <h|d>` ou `!clc max`"
    )
    @commands.has_permissions(manage_messages=True)
    async def clc(self, ctx, *args):
        MAX_TEMPO = 14  # 14 dias

        # Tratar o caso !clc max
        if len(args) == 1 and args[0].lower() == "max":
            tempo = MAX_TEMPO
            label = "14 dias"
        # Tratar o caso !clc <número> <h|d>
        elif len(args) == 2:
            quantidade, unidade = args[0], args[1].lower()

            if not quantidade.isdigit():
                return await ctx.send("❌ A quantidade deve ser um número.")
            quantidade = int(quantidade)

            if unidade == "h":
                tempo = quantidade  # Tempo em horas
                label = f"{quantidade} hora(s)"
            elif unidade == "d":
                tempo = quantidade * 24  # Converter dias para horas
                label = f"{quantidade} dia(s)"
            else:
                return await ctx.send("❌ Unidade inválida. Usa `h` (horas) ou `d` (dias).")
        else:
            return await ctx.send("❌ Uso inválido. Ex: `!clc 10 h`, `!clc 2 d`, `!clc max`")

        if tempo <= 0:
            return await ctx.send("❌ A quantidade de tempo deve ser maior que 0.")
        if tempo > MAX_TEMPO * 24:
            return await ctx.send(f"❌ Só posso apagar mensagens com menos de 14 dias ({MAX_TEMPO} dias).")

        # Apagar a mensagem de comando
        await ctx.message.delete()

        # Calcular o limite de tempo
        agora = datetime.utcnow()
        limite_tempo = agora - timedelta(hours=tempo)

        # Purge
        apagadas = await ctx.channel.purge(after=limite_tempo)

        # Confirmação temporária
        confirm = await ctx.send(f"🧹 Apagadas {len(apagadas)} mensagens dos últimos {label}.")
        await confirm.delete(delay=5)

async def setup(bot):
    await bot.add_cog(Limpar(bot))
