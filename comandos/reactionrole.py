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

    # Comando para configurar reaction role
    @commands.command(
        name="rr",
        aliases=["reactionrole"],
        help="Configura um role baseado em uma reação a uma mensagem.\nUso: `!rr <link> <emoji> <role> <true or false>`"
    )
    @commands.has_permissions(administrator=True)
    async def rr(self, ctx, message_link, emoji, role: discord.Role, exclusive: bool):
        try:
            # Extrair IDs da URL
            parts = message_link.split('/')
            guild_id = int(parts[-3])
            channel_id = int(parts[-2])
            message_id = int(parts[-1])

            # Obter a mensagem
            channel = self.bot.get_channel(channel_id)
            message = await channel.fetch_message(message_id)

            # Verificar permissões
            if not message.channel.permissions_for(ctx.guild.me).add_reactions:
                return await ctx.send("❌ Não tenho permissão para adicionar reações nessa mensagem.")
            if not ctx.guild.me.guild_permissions.manage_roles:
                return await ctx.send("❌ Não tenho permissão para gerenciar cargos.")

            # Mostrar pré-visualização
            preview = (
                f"**Prévia de configuração:**\n"
                f"Mensagem: [Link]({message_link})\n"
                f"Emoji: {emoji}\n"
                f"Role: {role.mention}\n"
                f"Exclusivo: {'Sim' if exclusive else 'Não'}\n\n"
                f"✅ Para confirmar ou ❌ Para cancelar."
            )
            preview_message = await ctx.send(preview)
            await preview_message.add_reaction("✅")
            await preview_message.add_reaction("❌")

            # Esperar pela reação
            def check(reaction, user):
                return user == ctx.author and reaction.message.id == preview_message.id and str(reaction.emoji) in ["✅", "❌"]

            reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

            if str(reaction.emoji) == "❌":
                await ctx.send("❌ Configuração cancelada.")
                return

            # Adicionar a reação
            await message.add_reaction(emoji)

            # Armazenar a configuração
            if str(message_id) not in reaction_roles:
                reaction_roles[str(message_id)] = {}
            reaction_roles[str(message_id)][emoji] = {
                "role_id": role.id,
                "exclusive": exclusive
            }

            # Salvar a configuração
            with open(DATA_FILE, "w") as f:
                json.dump(reaction_roles, f, indent=4)

            await ctx.send(f"✅ Configuração feita para reação {emoji} com role {role.name}")

        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro: {str(e)}")

    # Evento para adicionar role com a reação
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

    # Evento para remover role com a reação
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

# Setup para carregar o cog
async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
