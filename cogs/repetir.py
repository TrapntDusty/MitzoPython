import asyncio
import platform
import random
import discord
from discord.ext import commands
import utils.json_loader
Repi = utils.json_loader.read_json("setup")

class Repetir(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog ha sido cargado\n-----")

    @commands.command(
        name="r",
        description="un comando para repetir en un canal lo que ocupes",
        usage="[Texto a Repetir]"
    )
    @commands.has_any_role(int(Repi["Owners"]),int(Repi["Admin"]),int(Repi["Mod"]))
    async def r(self, ctx, channel:discord.TextChannel):
        await ctx.message.delete()
        embed = discord.Embed(
            title="Dime que repetire!",
            description="El comando se cancelara en 1 minuto.",
        )
        sent = await ctx.send(embed=embed)

        try:
            msg = await self.bot.wait_for(
                "message",
                timeout=60,
                check=lambda message: message.author == ctx.author
                and message.channel == ctx.channel,
            )
            if msg:
                await sent.delete()
                await msg.delete()
                await channel.send(msg.content)
        except asyncio.TimeoutError:
            await sent.delete()
            await ctx.send("Cancelando", delete_after=10)


def setup(bot):
    bot.add_cog(Repetir(bot))
