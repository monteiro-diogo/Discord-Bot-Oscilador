import discord
from discord.ext import commands
import json
import os

STATUS_PATH = "status.json"


def guardar_status(tipo, texto):
    """Guarda as alterações no ficheiro JSON."""
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump({"type": tipo, "text": texto}, f, indent=4, ensure_ascii=False)


def criar_activity(tipo, texto):
    """Cria o objeto Activity certo com base no tipo."""
    tipo = tipo.lower()
    if tipo == "playing":
        return discord.Game(name=texto)
    elif tipo == "listening":
        return discord.Activity(type=discord.ActivityType.listening, name=texto)
    elif tipo == "watching":
        return discord.Activity(type=discord.ActivityType.watching, name=texto)
    elif tipo == "competing":
        return discord.Activity(type=discord.ActivityType.competing, name=texto)
    else:
        return None


class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def status(self, ctx, tipo: str = None, *, texto: str = None):
        """
        Atualiza o status do bot em tempo real e grava no status.json.
        Uso:
          !status playing Minecraft
          !status listening Lofi beats
          !status watching o servidor
          !status reset (remove o status)
          !status -> mostra o atual
        """

        # Mostrar o status atual
        if not tipo and not texto:
            if not os.path.exists(STATUS_PATH):
                await ctx.send("⚠️ Ficheiro status.json não encontrado.")
                return

            try:
                with open(STATUS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                await ctx.send(f"📄 Status atual: **{data.get('type', '?')} {data.get('text', '?')}**")
            except Exception:
                await ctx.send("❌ Erro ao ler o ficheiro status.json.")
            return

        tipo = tipo.lower()

        # Resetar status
        if tipo == "reset":
            guardar_status("", "")
            await self.bot.change_presence(activity=None)
            await ctx.send("🧹 Status removido (sem atividade).")
            return

        # Validar tipo
        if tipo not in ["playing", "listening", "watching", "competing"]:
            await ctx.send("❌ Tipo inválido! Usa: playing, listening, watching, competing ou reset.")
            return

        texto = texto or ""

        # Criar e aplicar status
        activity = criar_activity(tipo, texto)
        await self.bot.change_presence(activity=activity)
        guardar_status(tipo, texto)

        await ctx.send(f"✅ Status atualizado para **{tipo} {texto}** (aplicado em tempo real).")


async def setup(bot):
    await bot.add_cog(Status(bot))
