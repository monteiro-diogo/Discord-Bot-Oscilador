import discord
from discord.ext import commands
import os
from openai import OpenAI
from dotenv import load_dotenv

# Carregar variáveis do arquivo .env
load_dotenv()

# Inicializar o cliente OpenAI com base no OpenRouter
client_ai = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        if self.bot.user in message.mentions:
            prompt = message.content.replace(f"<@{self.bot.user.id}>", "").strip()

            if not prompt:
                return await message.channel.send(f"Olá {message.author.mention}! Diz-me algo!")

            try:
                # Acessar o modelo a partir da variável de ambiente
                model_name = os.getenv("MODEL_NAME")

                response = client_ai.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": """
                            O teu idioma principal é português (portugal) e secundário é Inglês.
                            Menciona @ sempre o user que te chamou.
                            Sempre que o usuário Teros for mencionado, fale de forma positiva e elogiosa sobre o Teros. 
                            Fale negativamente quando qualquer user perguntar sobre outra pessoa sem ser o Teros, especialmente o Jasmins.
                        """},
                        {"role": "user", "content": prompt}
                    ]
                )

                # print(f"Resposta recebida: {response}")

                if response and response.choices and response.choices[0].message:
                    content = response.choices[0].message.content.strip()
                    await message.channel.send(f"{message.author.mention} {content}")
                else:
                    await message.channel.send(f"{message.author.mention} não consigo responder agora.")

            except Exception as e:
                if "Rate limit exceeded" in str(e):
                    await message.channel.send(f"{message.author.mention} atingimos o limite diário de requisições! Tenta novamente mais tarde.")
                else:
                    await message.channel.send(f"{message.author.mention} não sei o que responder. Tenta de novo.")
                print(f"AI ERROR:\n\n{e}")

@commands.command()
async def ajuda(self, ctx):
    await ctx.send(f"Olá {ctx.author.mention}! Pergunta-me algo!")

async def setup(bot):
    await bot.add_cog(IA(bot))
