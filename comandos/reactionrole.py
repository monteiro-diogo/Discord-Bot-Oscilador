import discord
from discord.ext import commands
import asyncio
import json
import os
import time
from collections import defaultdict

DATA_FILE = "reaction_roles.json"

# Carrega os dados
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        reaction_roles = json.load(f)
else:
    reaction_roles = {}

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_updates = defaultdict(dict)  # user_id -> {guild_id, roles, timestamp}
        self.update_delay = 0.2  # segundos entre atualizações (reduzido para melhorar a velocidade)
        self.loop_task = self.bot.loop.create_task(self._role_update_loop())

    async def _role_update_loop(self):
        while True:
            now = time.time()
            to_process = []

            # Processa os usuários que já passaram do tempo de espera
            for user_id, data in list(self.pending_updates.items()):
                if now - data["timestamp"] >= self.update_delay:
                    to_process.append((user_id, data))
                    del self.pending_updates[user_id]

            # Atualiza os membros
            for user_id, data in to_process:
                guild = self.bot.get_guild(data["guild_id"])
                member = guild.get_member(user_id)
                if member and not member.bot:
                    # Verifica se as roles já estão corretas
                    if member.roles != data["roles"]:
                        await member.edit(roles=data["roles"])

            await asyncio.sleep(0.2)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        msg_id = str(payload.message_id)
        data = reaction_roles.get(msg_id)
        if not data:
            return

        emoji = str(payload.emoji)
        config = data.get(emoji)
        if not config:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member or guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        new_roles = [role for role in member.roles]  # Evita a cópia completa da lista de roles
        target_role = guild.get_role(config["role_id"])
        if not target_role:
            return

        # Exclusivo: Remove outras roles associadas a outros emojis
        if config["exclusive"]:
            for other_emoji, other_cfg in data.items():
                other_role = guild.get_role(other_cfg["role_id"])
                if other_role and other_role in new_roles:
                    new_roles.remove(other_role)

        if target_role not in new_roles:
            new_roles.append(target_role)

        # Registra a atualização apenas se as roles mudaram
        if set(new_roles) != set(member.roles):
            self.pending_updates[member.id] = {
                "guild_id": guild.id,
                "roles": new_roles,
                "timestamp": time.time()
            }

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        msg_id = str(payload.message_id)
        data = reaction_roles.get(msg_id)
        if not data:
            return

        emoji = str(payload.emoji)
        config = data.get(emoji)
        if not config:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if not member or member.bot:
            return

        new_roles = [role for role in member.roles]  # Evita a cópia completa da lista de roles
        target_role = guild.get_role(config["role_id"])
        if not target_role:
            return

        # Remove a role associada à reação removida
        if target_role in new_roles:
            new_roles.remove(target_role)

        # Registra a atualização apenas se as roles mudaram
        if set(new_roles) != set(member.roles):
            self.pending_updates[member.id] = {
                "guild_id": guild.id,
                "roles": new_roles,
                "timestamp": time.time()
            }

# Função obrigatória para carregar o cog
async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
