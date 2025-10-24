import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

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
    
    # === Ler configuração do status de ficheiro JSON ===
    try:
        with open("status.json", "r", encoding="utf-8") as f:
            status_data = json.load(f)

        tipo = status_data.get("type", "").lower()
        texto = status_data.get("text", "")

        # === Mapear o tipo para a classe correspondente ===
        if tipo == "playing":
            activity = discord.Game(name=texto)
        elif tipo == "listening":
            activity = discord.Activity(type=discord.ActivityType.listening, name=texto)
        elif tipo == "watching":
            activity = discord.Activity(type=discord.ActivityType.watching, name=texto)
        elif tipo == "competing":
            activity = discord.Activity(type=discord.ActivityType.competing, name=texto)
        else:
            activity = None

        # === Aplicar o status apenas se existir ===
        if activity:
            await bot.change_presence(activity=activity)
            print(f"Status definido para: {tipo.capitalize()} {texto}")
        else:
            print("Aviso: tipo de status inválido no ficheiro JSON.")

    except FileNotFoundError:
        print("Aviso: ficheiro status.json não encontrado. Nenhum status foi definido.")
    except json.JSONDecodeError:
        print("Erro: ficheiro status.json mal formatado.")
        
@bot.event
@bot.event
async def setup_hook():
    comandos_dir = "./comandos"

    # Percorrer todas as subpastas
    for root, _, files in os.walk(comandos_dir):
        for filename in files:
            if filename.endswith(".py"):
                # Gerar caminho completo no formato Python package
                relative_path = os.path.relpath(os.path.join(root, filename), comandos_dir)
                module_path = relative_path.replace(os.sep, ".")[:-3]  # remover ".py"
                module = os.path.splitext(filename)[0]  # apenas o nome do módulo
                await bot.load_extension(f"comandos.{module_path}")
                print(f"✅ Comando carregado: {module}")

# === Rodar o bot ===
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if TOKEN:
    bot.run(TOKEN)
else:
    print("Erro: Token do bot não encontrado na variável de ambiente 'DISCORD_BOT_TOKEN'.")
