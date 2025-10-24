import discord
from discord.ext import commands

class Limpar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="clc",
        aliases=["clearchat"],
        help="Limpa mensagens.\nUso: `!clc <num>` ou `!clc user @utilizador <num>`"
    )
    @commands.has_permissions(administrator=True)
    async def clc(self, ctx, *args):
        if len(args) == 1:
            # === !clc <num> ===
            if not args[0].isdigit():
                return await ctx.send("❌ Indica um número válido. Ex: `!clc 10`")
            quantidade = int(args[0])
            if not 0 < quantidade <= 20:
                return await ctx.send("❌ O número deve estar entre 1 e 20.")

            await ctx.message.delete()
            apagadas = await ctx.channel.purge(limit=quantidade)
            confirm = await ctx.send(f"🧹 Apaguei {len(apagadas)} mensagens.")
            await confirm.delete(delay=5)

        elif len(args) == 3 and args[0].lower() == "user":
            # === !clc user @user <num> ===
            user_input, quantidade = args[1], args[2]
            if not quantidade.isdigit():
                return await ctx.send("❌ Usa: `!clc user @utilizador <num>`")
            quantidade = int(quantidade)
            if not 0 < quantidade <= 100:
                return await ctx.send("❌ Número deve estar entre 1 e 100.")

            membro = None

            # Se for uma menção
            if ctx.message.mentions:
                membro = ctx.message.mentions[0]
            elif user_input.isdigit():
                # Procurar por ID: preferir membro do servidor, caso contrário tentar buscar globalmente via API
                user_id = int(user_input)
                membro = ctx.guild.get_member(user_id)
                if not membro:
                    try:
                        membro = await self.bot.fetch_user(user_id)
                    except Exception:
                        membro = None
            else:
                # Tentar encontrar por nome exato (verificando também o ID se for ambiguo)
                membro = discord.utils.find(
                    lambda m: m.name.lower() == user_input.lower() or m.display_name.lower() == user_input.lower() or str(m.id) == user_input,
                    ctx.guild.members
                )

            if not membro:
                return await ctx.send(f"❌ Utilizador `{user_input}` não encontrado no servidor ou globalmente.")

            await ctx.message.delete()

            # Buscar mensagens
            mensagens = []
            async for msg in ctx.channel.history(limit=100):
                if msg.author == membro:
                    mensagens.append(msg)
                if len(mensagens) >= quantidade:
                    break

            if mensagens:
                await ctx.channel.delete_messages(mensagens)
                display_name = getattr(membro, 'display_name', None) or getattr(membro, 'name', str(membro))
                confirm = await ctx.send(f"🧹 Apagadas {len(mensagens)} mensagens de {display_name}.")
                await confirm.delete(delay=5)
            else:
                await ctx.send(f"ℹ️ Nenhuma mensagem recente de {membro.display_name} encontrada.")

        else:
            await ctx.send("❌ Uso incorreto. Exemplos:\n`!clc 10`\n`!clc user @Alex 5`")

    @clc.error
    async def clc_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Precisas de **permissão de administrador** para isso.")

async def setup(bot):
    await bot.add_cog(Limpar(bot))
