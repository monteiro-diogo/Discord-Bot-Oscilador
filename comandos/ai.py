import discord
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()

LOCAL_URL = os.getenv("LOCAL_URL")

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pergunta")
    async def pergunta(self, ctx, *, pergunta: str):
        """Faz uma pergunta ao modelo local"""
        await self.enviar_para_ollama(ctx, pergunta)

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignorar mensagens do próprio bot
        if message.author == self.bot.user:
            return

        # Só responde se for mencionado diretamente (evita @everyone/@here)
        if (
            self.bot.user in message.mentions and
            not message.mention_everyone and
            not message.content.startswith("!")
        ):
            pergunta = message.content.replace(f"<@{self.bot.user.id}>", "").strip()
            if pergunta:
                ctx = await self.bot.get_context(message)
                await self.enviar_para_ollama(ctx, pergunta)

    async def enviar_para_ollama(self, ctx, pergunta):
        pensando_msg = await ctx.send("🧠 A pensar...")

        try:
            response = requests.post(LOCAL_URL, json={
                "model": "mistral",
                "prompt": pergunta,
                "stream": False
            })
            data = response.json()
            resposta = data.get("response", "❌ Não consegui gerar resposta.")
        except Exception as e:
            resposta = f"Erro ao contactar a IA: `{e}`"

        await pensando_msg.delete()

        await ctx.send(resposta)

async def setup(bot):
    await bot.add_cog(AI(bot))
