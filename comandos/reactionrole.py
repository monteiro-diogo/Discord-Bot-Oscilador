# comandos/reactionrole.py

import discord
from discord.ext import commands
import asyncio
import json
import os

DATA_FILE = "reaction_roles.json"

# Carregar as configurações
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        reaction_roles = json.load(f)
else:
    reaction_roles = {}

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # === Comando de configurar reaction role ===
    @commands.command(name="rr", help="`<link> <emoji> <role> <true or false>` - ``Dá um role de acordo com uma reação criada``")
    @commands.has_permissions(administrator=True)
    async def rr(self, ctx, message_link, emoji, role: discord.Role, exclusive: bool):
        parts = message_link.split('/')
        guild_id = int(parts[-3])
        channel_id = int(parts[-2])
        message_id = int(parts[-1])

        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(message_id)

        if not message.channel.permissions_for(ctx.guild.me).add_reactions:
            return await ctx.send("❌ Não tenho permissão para adicionar reações nessa mensagem.")
        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.send("❌ Não tenho permissão para gerenciar cargos.")

        preview = (
            f"**Prévia de configuração:**\n"
            f"Mensagem: [Link]({message_link}) "
            f"Emoji: {emoji} "
            f"Role: {role.mention} "
            f"Exclusivo: {'Sim' if exclusive else 'Não'}\n\n"
            f"✅ Para confirmar ou ❌ Para cancelar."
        )
        preview_message = await ctx.send(preview)

        await preview_message.add_reaction("✅")
        await preview_message.add_reaction("❌")

        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message.id == preview_message.id and
                str(reaction.emoji) in ["✅", "❌"]
            )

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("⏰ Tempo de confirmação esgotado. Cancelei a configuração.")
            return

        if str(reaction.emoji) == "❌":
            await ctx.send("❌ Configuração cancelada.")
            return

        await message.add_reaction(emoji)

        if str(message_id) not in reaction_roles:
            reaction_roles[str(message_id)] = {}
        reaction_roles[str(message_id)][emoji] = {
            "role_id": role.id,
            "exclusive": exclusive
        }

        with open(DATA_FILE, "w") as f:
            json.dump(reaction_roles, f, indent=4)

        await ctx.send(f"✅ Configuração feita para reação {emoji} com role {role.name}")

    # === Evento para adicionar role ===
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        user = payload.member
        if not user:
            guild = self.bot.get_guild(payload.guild_id)
            user = guild.get_member(payload.user_id)
        if not user or user.bot:
            return

        data = reaction_roles.get(str(payload.message_id))
        if not data:
            return

        emoji = str(payload.emoji)
        if emoji not in data:
            return

        guild = self.bot.get_guild(payload.guild_id)
        role = guild.get_role(data[emoji]["role_id"])
        exclusive = data[emoji]["exclusive"]

        if exclusive:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            for other_emoji in data:
                if other_emoji != emoji:
                    await message.remove_reaction(other_emoji, user)
                    other_role = guild.get_role(data[other_emoji]["role_id"])
                    if other_role:
                        await user.remove_roles(other_role)

        await user.add_roles(role)

    # === Evento para remover role ===
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        guild = self.bot.get_guild(payload.guild_id)
        user = guild.get_member(payload.user_id)
        if not user:
            return

        data = reaction_roles.get(str(payload.message_id))
        if not data:
            return

        emoji = str(payload.emoji)
        if emoji not in data:
            return

        role = guild.get_role(data[emoji]["role_id"])
        if role:
            await user.remove_roles(role)

# Setup para o bot carregar o cog
async def setup(bot):
    await bot.add_cog(ReactionRole(bot))

