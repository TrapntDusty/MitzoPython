import discord
from discord.ext import commands
from utils.util import GetMessage
import utils.json_loader

class inicio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="inicio",
        aliases=["iniciar", "configurar"],
        description="Para Configurar el bot para tu servidor!",
        usage="inicio",
    )
    @commands.guild_only()
    @commands.is_owner()
    async def inicio(self, ctx):
        await ctx.send("Empezemos este giveaway , primero respondeme estas preguntas.")

        questionList = [
            ["Dame la ID del rol", "Owners"],
            ["Dame la ID del rol", "Admin"],
            ["Dame la ID del rol", "Mod"],
            ["Dame la ID del rol", "Muted"],
            ["Dame id del canal de logs de entrada", "LogsJoin"],
            ["Dame id del canal de logs editados", "LogsEdit"],
            ["Dame id del canal de logs borrados", "LogsErase"],
            ["Dame id del canal de mensaje bienvenida", "Bienvenida"],
            ["Dame id del canal de mensaje boost", "Boost"],
            ["Dame id del canal de sugerencias", "Sugerencias"]
        ]
        answers = {}

        for i, question in enumerate(questionList):
            answer = await GetMessage(self.bot, ctx, question[0], question[1])

            if not answer:
                await ctx.send("Tiempo de espera superado, Cancelando comando.")
                return

            answers[i] = answer
        
        inicios = utils.json_loader.read_json("setup")

        for key, value in answers.items():
            inicios["{}".format(questionList[key][1])] = value=f"{value}"
            utils.json_loader.write_json(inicios,"setup")


def setup(bot):
    bot.add_cog(inicio(bot))
