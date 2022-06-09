import random
import datetime
import discord
from discord.ext import commands
import utils.json_loader
Evento = utils.json_loader.read_json("setup")


# In cogs we make our own class
# for d.py which subclasses commands.Cog


class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog cargado con exito\n-----")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # On member joins we find a channel called general and if it exists,
        # send an embed welcoming them to our guild
        channel = self.bot.get_channel(int(Evento["Bienvenida"]))
        if channel:
            embed = discord.Embed(
                description="Bienvenido al servidor!",
                color=random.choice(self.bot.color_list),
            )
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name=member.name, icon_url=member.avatar_url)
            embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
            embed.timestamp = datetime.datetime.utcnow()

            await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if len(before.roles) < len(after.roles):
            Rol = next(role for role in after.roles if role not in before.roles)
            if Rol.name == "Server Booster":
                channel = self.bot.get_channel(int(Evento["Boost"]))
                if channel:
                    embed = discord.Embed(
                    title="<:fancy:692995698014158849> __**¡ {} ha mejorado el servidor !**__ <:fancy:692995698014158849>".format(after.author.name),
                    description="<:kermity:947218077723013130> Gracias por ayudar mejorando el servidor <:kermity:947218077723013130>\n<:Group1:919112124888924160> ¡{} es una persona realmente impresionante!".format(after.author.name),
                    color=random.choice(self.bot.color_list),
                    )
                    if after.guild.premium_subscription_count < 2:
                        nivel = 0
                    elif after.guild.premium_subscription_count < 7:
                        nivel = 1
                    elif after.guild.premium_subscription_count < 14:
                        nivel = 2
                    else:
                        nivel = 3
                    embed.add_field(value=f"> ¡El servidor ahora tiene {after.guild.premium_subscription_count} mejoras! <:fancy:692995698014158849>\n> ¡Somos nivel {nivel}! <a:ratJAM:851996870272090122>\n> ¡El limite es el cielo! <:Frog_Fingers:842495317273477180>",name='\u200b')
                    embed.set_thumbnail(url=after.author.avatar_url)
                    embed.set_image(url = "https://images-ext-1.discordapp.net/external/bqDVQMHcWfly0uC-FU_Jt8SoLI214PZWZBxUW2N_hf8/https/c.tenor.com/O-hQvpUXQfYAAAAC/minecraft-steve.gif")

                    await channel.send("<:Frog_Fingers:842495317273477180> {} Muchas gracias por Boostear!".format(after.author.mention))
                    await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            if int(h) == 0 and int(m) == 0:
                await ctx.send(f" Debes esperar {int(s)} Segundos para utilizar este comando!")
            elif int(h) == 0 and int(m) != 0:
                await ctx.send(
                    f" Debes esperar {int(m)} Minutos y {int(s)} Segundos para utilizar este comando!"
                )
            else:
                await ctx.send(
                    f" Debes esperar {int(h)} horas, {int(m)} Minutos y {int(s)} Segundos para utilizar este comando!"
                )
        elif isinstance(error, commands.CheckFailure):
            # If the command has failed a check, trip this
            await ctx.send("Hey! no tienes permisos para usar este comando.")
        # Implement further custom checks for errors here...
        raise error


def setup(bot):
    bot.add_cog(Eventos(bot))
