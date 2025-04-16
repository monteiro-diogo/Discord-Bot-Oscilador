
# === Imports necessários ===
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# === Intents obrigatórias ===
intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.guilds = True
intents.members = True

# === Instanciar o bot ===
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# === Evento de inicialização ===
@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    
    # Definir o status do bot
    activity = discord.Game(name="Forex")
    await bot.change_presence(activity=activity)

@bot.event
async def setup_hook():
    if os.path.exists("./comandos"):
        for filename in os.listdir("./comandos"):
            if filename.endswith(".py"):
                await bot.load_extension(f"comandos.{filename[:-3]}")
    
    if os.path.exists("./extensoes"):
        for filename in os.listdir("./extensoes"):
            if filename.endswith(".py"):
                await bot.load_extension(f"extensoes.{filename[:-3]}")

# === Rodar o bot ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: Token do bot não encontrado na variável de ambiente 'DISCORD_BOT_TOKEN'.")
