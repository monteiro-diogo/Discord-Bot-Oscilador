import discord
from discord.ext import commands
import json
import os

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_folder = "reaction_roles_data"  # Pasta onde os arquivos serão salvos
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)  # Cria a pasta se não existir

    # Função para carregar os dados do servidor específico
    def load_guild_data(self, guild_id):
        file_path = os.path.join(self.data_folder, f"{guild_id}_reaction_roles.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        return {}

    # Função para salvar os dados do servidor específico
    def save_guild_data(self, guild_id, data):
        file_path = os.path.join(self.data_folder, f"{guild_id}_reaction_roles.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

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

            # Carregar dados do servidor
            guild_data = self.load_guild_data(ctx.guild.id)

            if str(message_id) not in guild_data:
                guild_data[str(message_id)] = {}

            guild_data[str(message_id)][emoji] = {
                "role_id": role.id,
                "exclusive": exclusive
            }

            # Salvar os dados do servidor
            self.save_guild_data(ctx.guild.id, guild_data)

            await ctx.send(f"✅ Configuração feita para reação {emoji} com role {role.name}")

        except Exception as e:
            await ctx.send(f"❌ Ocorreu um erro: {str(e)}")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        # Carregar dados do servidor
        guild_data = self.load_guild_data(payload.guild_id)
        if not guild_data:
            return

        msg_id = str(payload.message_id)
        data = guild_data.get(msg_id)
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

        new_roles = member.roles.copy()
        target_role = guild.get_role(config["role_id"])
        if not target_role:
            return

        if config["exclusive"]:
            for other_emoji, other_cfg in data.items():
                other_role = guild.get_role(other_cfg["role_id"])
                if other_role and other_role in new_roles:
                    new_roles.remove(other_role)

        if target_role not in new_roles:
            new_roles.append(target_role)

        await member.edit(roles=new_roles)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id:
            return

        # Carregar dados do servidor
        guild_data = self.load_guild_data(payload.guild_id)
        if not guild_data:
            return

        msg_id = str(payload.message_id)
        data = guild_data.get(msg_id)
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

        new_roles = member.roles.copy()
        target_role = guild.get_role(config["role_id"])
        if not target_role:
            return

        if target_role in new_roles:
            new_roles.remove(target_role)

        await member.edit(roles=new_roles)


# Função obrigatória para carregar o Cog
async def setup(bot):
    await bot.add_cog(ReactionRole(bot))
