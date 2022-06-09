import discord
from discord.ext import commands
from utils.util import Pag
import utils.json_loader
Note = utils.json_loader.read_json("setup")


class Warns(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name="warn",
        description="un comando para notear a una persona",
        usage="[persona] [razon]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Note["Owners"]),int(Note["Admin"]),int(Note["Mod"]))
    async def warn(self, ctx, member: discord.Member, *, reason):
        if member.id in [ctx.author.id, self.bot.user.id]:
            return await ctx.send("No te puedes notear a ti mismo o al bot!")
        
        current_warn_count = len(
            await self.bot.warns.find_many_by_custom(
                {
                    "user_id": member.id,
                    "guild_id": member.guild.id
                }
            )
        ) + 1
        
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id, "number": current_warn_count}
        warn_data = {"reason": reason, "timestamp": ctx.message.created_at, "warned_by": ctx.author.id}
        
        await self.bot.warns.upsert_custom(warn_filter, warn_data)
        
        embed = discord.Embed(
            title="Estas siendo noteado:",
            description=f"__**Razon**__:\n{reason}",
            colour=discord.Colour.red(),
            timestamp=ctx.message.created_at
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.set_footer(text=f"Nota: {current_warn_count}")
        
        try:
            await member.send(embed=embed)
            await ctx.send("Avise al usuario en privado por ti.")
        except discord.HTTPException:
            await ctx.send(member.mention, embed=embed)
            
    @commands.command(
        name="warns",
        description="un comando para checar las notas de una persona",
        usage="[persona]",
    )
    @commands.guild_only()
    @commands.has_any_role(int(Note["Owners"]),int(Note["Admin"]),int(Note["Mod"]))
    async def warns(self, ctx, member: discord.Member):
        warn_filter = {"user_id": member.id, "guild_id": member.guild.id}
        warns = await self.bot.warns.find_many_by_custom(warn_filter)
        
        if not bool(warns):
            return await ctx.send(f"No encontre ninguna nota hacia: `{member.display_name}`")
        
        warns = sorted(warns, key=lambda x: x["number"])
        
        pages = []
        for warn in warns:
            description = f"""
            Numero de la nota: `{warn['number']}`
            Razon de la nota: `{warn['reason']}`
            Noteado por: <@{warn['warned_by']}>
            Fecha de la nota: {warn['timestamp'].strftime("%I:%M %p %B %d, %Y")}
            """
            pages.append(description)
        
        await Pag(
            title=f"Warns for `{member.display_name}`",
            colour=0xCE2029,
            entries=pages,
            length=1
        ).start(ctx)

    @commands.command(
        name="borrarnota",
        description="un comando para borrar la(s) nota(s) de una persona",
        usage="[persona] [no. nota]",
        aliases=["delwarn", "dw"]
        )
    @commands.has_any_role(int(Note["Owners"]),int(Note["Admin"]),int(Note["Mod"]))
    @commands.guild_only()
    async def deletewarn(self, ctx, member: discord.Member, warn: int = None):
        filter_dict = {"user_id": member.id, "guild_id": member.guild.id}
        if warn:
            filter_dict["number"] = warn

        was_deleted = await self.bot.warns.delete_by_custom(filter_dict)
        if was_deleted and was_deleted.acknowledged:
            if warn:
                return await ctx.send(
                    f"Elimine la nota `{warn}` de `{member.display_name}`"
                )

            return await ctx.send(
                f"he eliminado `{was_deleted.deleted_count}` notas de `{member.display_name}`"
            )

        await ctx.send(
            f"no encontre ninguna nota hacia `{member.display_name}` para eliminar"
        )


def setup(bot):
    bot.add_cog(Warns(bot))
