from datetime import datetime
from typing import Optional
import discord
from discord import Embed, Member
from discord.ext.commands import Cog
from discord.ext.commands import command
import random

class Info(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="infousuario", 
	description="un comando para checar la informacion de un usuario o tuya",
	usage="[ID persona (opcional)]", 
	aliases=["memberinfo", "ui", "mi"])
	async def infousuario(self, ctx, target: Optional[Member]):
		target = target or ctx.author

		embed = Embed(title="Informacion Usuario",
					  color=random.choice(self.bot.color_list),
					  timestamp=datetime.utcnow())

		embed.set_thumbnail(url=target.avatar_url)

		fields = [("Nombre", str(target), True),
				  ("ID", target.id, True),
				  ("Bot?", target.bot, True),
				  ("Rol Top", target.top_role.mention, True),
				  ("estatus", str(target.status).title(), True),
				  ("Actividad", f"{str(target.activity.type).split('.')[-1].title() if target.activity else 'N/A'} {target.activity.name if target.activity else ''}", True),
				  ("Creado el", target.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Unido el", target.joined_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Booster?", bool(target.premium_since), True)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)

	@command(name="infoservidor", 
	description="un comando para checar la informacion del servidor",usage = '\u200b',aliases=["guildinfo", "si", "gi"])
	async def server_info(self, ctx):
		embed = Embed(title="Server informacion",
					  color=random.choice(self.bot.color_list),
					  timestamp=datetime.utcnow())

		embed.set_thumbnail(url=ctx.guild.icon_url)

		statuses = [len(list(filter(lambda m: str(m.status) == "online", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "idle", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "dnd", ctx.guild.members))),
					len(list(filter(lambda m: str(m.status) == "offline", ctx.guild.members)))]

		fields = [("ID", ctx.guild.id, True),
				  ("Creador", ctx.guild.owner, True),
				  ("Creado el", ctx.guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), True),
				  ("Miembros", len(ctx.guild.members), True),
				  ("Humanos", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
				  ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
				  ("\u200b", "\u200b", True)]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)


def setup(bot):
	bot.add_cog(Info(bot))