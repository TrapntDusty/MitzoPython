import re
import datetime
from copy import deepcopy
import asyncio
import discord
from discord.ext import commands, tasks
from dateutil.relativedelta import relativedelta
import utils.json_loader
Mode = utils.json_loader.read_json("setup")

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}


class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} es un set de tiempo erroneo! h|m|s|d son argumentos validos"
                )
            except ValueError:
                raise commands.BadArgument(f"{key} no es un numero!")
        return round(time)


class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.datetime.now()
        mutes = deepcopy(self.bot.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.bot.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, id=int(Mode["Muted"]))
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Desmuteado: {member.display_name}")

                await self.bot.mutes.delete(member.id)
                try:
                    self.bot.muted_users.pop(member.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.bot.wait_until_ready()

    @commands.command(
        name='mute',
        description="Mutea a un usuario por x tiempo!",
        usage='<usuario> [tiempo]'
    )
    @commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
        role = discord.utils.get(ctx.guild.roles, id=int(Mode["Muted"]))
        try:
            if self.bot.muted_users[member.id]:
                await ctx.send("este usuario ya esta muteado")
                return
        except KeyError:
            pass

        data = {
            '_id': member.id,
            'mutedAt': datetime.datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.bot.mutes.upsert(data)
        self.bot.muted_users[member.id] = data

        await member.add_roles(role)

        if not time:
            await ctx.send(f"Muteado {member.display_name}")
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            if int(hours):
                await ctx.send(
                    f"Muteado {member.display_name} por {hours} horas, {minutes} minutos y {seconds} segundos"
                )
            elif int(minutes):
                await ctx.send(
                    f"Muteado {member.display_name} por {minutes} minutos y {seconds} segundos"
                )
            elif int(seconds):
                await ctx.send(f"Muteado {member.display_name} por {seconds} segundos")

        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"Desmuteado `{member.display_name}`")

            await self.bot.mutes.delete(member.id)
            try:
                self.bot.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command(
        name='unmute',
        description="Desmutea a un miembro!",
        usage='<Usuario>'
    )
    #@commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, id=int(Mode["Muted"]))
        await self.bot.mutes.delete(member.id)
        try:
            self.bot.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("este miembro no esta muteado.")
            return

        await member.remove_roles(role)
        await ctx.send(f"Desmuteado `{member.display_name}`")

    @commands.command(
        name="kick",
        description="Comando para kickear a un usuario",
        usage="<usuario> [razon]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.kick(user=member, reason=reason)

        # Using our past episodes knowledge can we make the log channel dynamic?
        embed = discord.Embed(
            title=f"{ctx.author.name} Kickeado: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="ban",
        description="un comando para banear a un usuario",
        usage="<usuario> [razon]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await ctx.guild.ban(user=member, reason=reason)

        # Using our past episodes knowledge can we make the log channel dynamic?
        embed = discord.Embed(
            title=f"{ctx.author.name} Baneado: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="unban",
        description="un comando para desbanear a un usuario",
        usage="<usuario> [razon]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def unban(self, ctx, member, *, reason=None):
        member = await self.bot.fetch_user(int(member))
        await ctx.guild.unban(member, reason=reason)

        embed = discord.Embed(
            title=f"{ctx.author.name} Desbaneado: {member.name}", description=reason
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="limpiar",
        description="un comando para limpiar una cantidad de mensaje, default 15",
        usage="[amount]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Mode["Owners"]),int(Mode["Admin"]),int(Mode["Mod"]))
    async def limpiar(self, ctx, amount=15):
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title=f"Borrados de: {ctx.channel.name}",
            description=f"{amount} Mensajes han sido borrados",
        )
        await ctx.send(embed=embed, delete_after=15)


def setup(bot):
    bot.add_cog(Moderacion(bot))
