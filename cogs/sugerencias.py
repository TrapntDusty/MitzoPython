import discord
import random
import asyncio
import DiscordUtils
from discord.ext import commands
import utils.json_loader
from datetime import datetime
archiv = utils.json_loader.read_json("setup")

class testeo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="ponersugerencia",
        description="un comando para poner sugerencias",
        usage="[sugerencia]",
        aliases=["sug", "s"])
    async def sugerencia(self, ctx, *, sugerencia):
        channel = self.bot.get_channel(int(archiv["Sugerencias"]))
        embed = discord.Embed(
            title = "Sugerencia  de {}".format(ctx.author),
            description = f"{sugerencia}",
            color=random.choice(self.bot.color_list),
			timestamp=datetime.utcnow()
        )
        message = await channel.send(embed=embed)
        await message.add_reaction('✅')
        await message.add_reaction('❌')

    @commands.command(
        name="aprovarsugerencia",
        description="un comando para denegar sugerencias",
        usage="[ID sugerencia]", 
        aliases=["AcceptS", "as"]
        )
    @commands.has_any_role(int(archiv["Owners"]),int(archiv["Admin"]),int(archiv["Mod"]))
    async def aprovsugerencia(self, ctx, msgID: int): 
        channel = self.bot.get_channel(int(archiv["Sugerencias"]))
        msg = await channel.fetch_message(msgID)
        embededmsg = msg.embeds[0].to_dict()
        embed = discord.Embed(
            title = f"{embededmsg.get('title')}",
            description = f"{embededmsg.get('description')}",
            color = 0x2ECC71,
            timestamp=datetime.utcnow()
        )
        embed.add_field(name=f"La sugerencia ha sido aceptada",value='\u200b')
        await msg.edit(embed=embed)

    @commands.command(
        name="denegarsugerencia",
        description="un comando para denegar sugerencias",
        usage="[ID sugerencia]", 
        aliases=["ds", "denyS", "cs"]
        )
    @commands.has_any_role(int(archiv["Owners"]),int(archiv["Admin"]),int(archiv["Mod"]))
    async def cancesugerencia(self, ctx, msgID: int): 
        channel = self.bot.get_channel(int(archiv["Sugerencias"]))
        msg = await channel.fetch_message(msgID)
        embededmsg = msg.embeds[0].to_dict()
        embed = discord.Embed(
            title = f"{embededmsg.get('title')}",
            description = f"{embededmsg.get('description')}",
            color = 0xE74C3C,
            timestamp=datetime.utcnow(),
        )
        embed.add_field(name= f"La sugerencia ha sido denegada", value='\u200b')
        await msg.edit(embed=embed)
        
    


def setup(bot):
    bot.add_cog(testeo(bot))
