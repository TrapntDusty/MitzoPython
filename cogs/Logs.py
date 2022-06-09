import discord
from discord import File, Member
import DiscordUtils
from discord.ext import commands
import utils.json_loader
from PIL import Image, ImageDraw, ImageFont
import io
from pathlib import Path
logsID = utils.json_loader.read_json("setup")

class Registros(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tracker = DiscordUtils.InviteTracker(bot)

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog cargado con exito\n-----")
        await self.tracker.cache_invites()

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        await self.tracker.update_invite_cache(invite)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        if message.author.bot:
            return
        async for entry in message.guild.audit_logs(limit=1,action=discord.AuditLogAction.message_delete):
            deleter = entry.user
        embed=discord.Embed(title="{} borro un Mensaje".format(deleter.name), description="mensaje borrado en {}".format(message.channel))
        embed.add_field(name= message.content ,value="Este es el mensaje borrado de {}".format(message.author.name), inline=True)
        await self.bot.get_channel(int(logsID["LogsErase"])).send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self,message_before, message_after):
        if len(message_after.content) > 250 or len(message_before.content) > 250:
            channel = self.bot.get_channel(int(logsID["LogsEdit"]))
            await channel.send("Mensaje muy largo , Mandando en modo texto")
            await channel.send("Mensaje antes: {}".format(message_before.content))
            await channel.send("Mensaje despues: {}".format(message_after.content))
            await channel.send("Editado por: {}".format(message_before.author.name))
            await channel.send("Editado en canal: {}".format(message_before.channel))
        else:
            embed=discord.Embed(title="{} edito un mensaje".format(message_before.author.name), description="mensaje editado en {}".format(message_before.channel))
            embed.add_field(name= message_before.content ,value="Mensaje antes del edit", inline=True)
            embed.add_field(name= message_after.content ,value="Mensaje despues del edit", inline=True)
            await self.bot.get_channel(int(logsID["LogsEdit"])).send(embed=embed)

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        await self.tracker.remove_invite_cache(invite)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await self.tracker.update_guild_cache(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        await self.tracker.remove_guild_cache(guild)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        cwd = utils.json_loader.get_path()
        background_image = Image.open(cwd + "/images/hhh.png")
        background_image = background_image.convert('RGBA')
        AVATAR_SIZE = 256
        image = background_image.copy()
        image_width, image_height = image.size
        rect_x0 = 400  # left 
        rect_y0 = 40  # top 
        rectangle_image = Image.new('RGBA', (image_width, image_height))
        rectangle_draw = ImageDraw.Draw(rectangle_image)
        borde = ImageDraw.Draw(image)
        borde.rectangle([0, 0, 1025, 499], outline=(255, 255, 255),width=10)
        draw = ImageDraw.Draw(image) 
        text = f'Bienvenid@'
        font = ImageFont.truetype(cwd + "/utils/Coiny-Regular.ttf",50)
        draw.text((375, 305), text, fill=(0,255,0,1), font=font)
        text2 = f'{member.display_name}'
        font = ImageFont.truetype(cwd + "/utils/Coiny-Regular.ttf",50)
        draw.text((445, 350), text2, fill=(0,255,0,1), font=font)
        text3 = f'Esperamos que te diviertas y aprendas en este servidor'
        font = ImageFont.truetype(cwd + "/utils/Coiny-Regular.ttf",30)
        draw.text((90, 410), text3, fill=(0,255,0,1), font=font)
        avatar_asset = member.avatar_url_as(format='jpg', size=AVATAR_SIZE)
        buffer_avatar = io.BytesIO(await avatar_asset.read())
        avatar_image = Image.open(buffer_avatar)
        avatar_image = avatar_image.resize((AVATAR_SIZE, AVATAR_SIZE)) #
        circle_image = Image.new('L', (AVATAR_SIZE, AVATAR_SIZE))
        circle_draw = ImageDraw.Draw(circle_image)
        circle_draw.ellipse((0, 0, AVATAR_SIZE, AVATAR_SIZE), fill=255)
        image.paste(avatar_image, (rect_x0, rect_y0), circle_image)
        buffer_output = io.BytesIO()
        image.save(buffer_output, format='PNG')
        buffer_output.seek(0)
        await self.bot.get_channel(int(logsID["LogsJoin"])).send(file=File(buffer_output, 'myimage.png'))

        inviter = await self.tracker.fetch_inviter(member)
        data = await self.bot.invites.find_by_custom(
            {"guild_id": member.guild.id, "inviter_id": inviter.id}
        )
        if data is None:
            data = {
                "guild_id": member.guild.id,
                "inviter_id": inviter.id,
                "count": 0,
                "invited_users": []
            }

        data["count"] += 1
        data["invited_users"].append(member.id)
        await self.bot.invites.upsert_custom(
            {"guild_id": member.guild.id, "inviter_id": inviter.id}, data
        )

        embed = discord.Embed(
            title=f"Bienvenido {member.display_name}!",
            description=f"Invitado por: {inviter.mention}\nInvitaciones: {data['count']}",
            timestamp=member.joined_at,
        )
        embed.set_thumbnail(url=member.avatar_url)
        embed.set_footer(text=member.guild, icon_url=member.guild.icon_url)
        await self.bot.get_channel(int(logsID["LogsJoin"])).send(embed=embed)


def setup(bot):
    bot.add_cog(Registros(bot))
