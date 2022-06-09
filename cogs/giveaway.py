import re
import random
import asyncio

import discord
from discord.ext import commands

from utils.util import GetMessage

time_regex = re.compile(r"(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


def convert(argument):
    args = argument.lower()
    matches = re.findall(time_regex, args)
    time = 0
    for key, value in matches:
        try:
            time += time_dict[value] * float(key)
        except KeyError:
            raise commands.BadArgument(
                f"{value} es una fecha de tiempo erronea! h|m|s|d son argumentos validos"
            )
        except ValueError:
            raise commands.BadArgument(f"{key} no es un numero!")
    return round(time)


class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="giveaway",
        description="para crear un giveaway!",
        usage="giveaway"
    )
    @commands.guild_only()
    async def giveaway(self, ctx):
        await ctx.send("Empezemos este giveaway , primero respondeme estas preguntas.")

        questionList = [
            ["En que canal sera?", "Menciona el canal"],
            ["Cuanto tiempo durara el giveaway?", "`d|h|m|s`"],
            ["Cual es la recompenza?","Porfavor solo texto"]
        ]
        answers = {}

        for i, question in enumerate(questionList):
            answer = await GetMessage(self.bot, ctx, question[0], question[1])

            if not answer:
                await ctx.send("Tiempo de espera superado, Cancelando comando.")
                return

            answers[i] = answer

        embed = discord.Embed(name="Giveaway Contenido")
        for key, value in answers.items():
            embed.add_field(name=f"Pregunta: `{questionList[key][0]}`", value=f"Respuesta: `{value}`", inline=False)

        m = await ctx.send("Todas estas son validas?", embed=embed)
        await m.add_reaction("✅")
        await m.add_reaction("🇽")

        try:
            reaction, member = await self.bot.wait_for(
                "reaction_add",
                timeout=60,
                check=lambda reaction, user: user == ctx.author
                and reaction.message.channel == ctx.channel
            )
        except asyncio.TimeoutError:
            await ctx.send("Intenalo de nuevo, Ocurrio un error.")
            return

        if str(reaction.emoji) not in ["✅", "🇽"] or str(reaction.emoji) == "🇽":
            await ctx.send("cancelando giveaway!")
            return

        channelId = re.findall(r"[0-9]+", answers[0])[0]
        channel = self.bot.get_channel(int(channelId))

        time = convert(answers[1])

        giveawayEmbed = discord.Embed(
            title="🎉 __**Giveaway**__ 🎉",
            description=answers[2]
        )
        giveawayEmbed.set_footer(text=f"Este Giveaway termina en {time} segundos despues de este mensaje.")
        giveawayMessage = await channel.send(embed=giveawayEmbed)
        await giveawayMessage.add_reaction("🎉")


def setup(bot):
    bot.add_cog(Giveaway(bot))
