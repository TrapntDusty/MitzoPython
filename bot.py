import contextlib
import io
import os
import logging
import textwrap
from traceback import format_exception
import discord
from pathlib import Path
import motor.motor_asyncio
from discord.ext import commands
import utils.json_loader
from utils.mongo import Document
from utils.util import clean_code, Pag


cwd = Path(__file__).parents[0]
cwd = str(cwd)
print(f"{cwd}\n-----")


async def get_prefix(bot, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)
        return commands.when_mentioned_or(data["prefix"])(bot, message)
    except:
        return commands.when_mentioned_or(bot.DEFAULTPREFIX)(bot, message)


intents = discord.Intents.all()  # Help command requires member intents
DEFAULTPREFIX = "!"
secret_file = utils.json_loader.read_json("secrets")
bot = commands.Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    owner_id=208762650706968586,
    help_command=None,
    intents=intents,
)  # change command_prefix='-' to command_prefix=get_prefix for custom prefixes
bot.config_token = secret_file["token"]
bot.connection_url = secret_file["mongo"]

logging.basicConfig(level=logging.INFO)

bot.DEFAULTPREFIX = DEFAULTPREFIX
bot.blacklisted_users = []
bot.muted_users = {}
bot.cwd = cwd

bot.colors = {
    "WHITE": 0xFFFFFF,
    "AQUA": 0x1ABC9C,
    "GREEN": 0x2ECC71,
    "BLUE": 0x3498DB,
    "PURPLE": 0x9B59B6,
    "LUMINOUS_VIVID_PINK": 0xE91E63,
    "GOLD": 0xF1C40F,
    "ORANGE": 0xE67E22,
    "RED": 0xE74C3C,
    "NAVY": 0x34495E,
    "DARK_AQUA": 0x11806A,
    "DARK_GREEN": 0x1F8B4C,
    "DARK_BLUE": 0x206694,
    "DARK_PURPLE": 0x71368A,
    "DARK_VIVID_PINK": 0xAD1457,
    "DARK_GOLD": 0xC27C0E,
    "DARK_ORANGE": 0xA84300,
    "DARK_RED": 0x992D22,
    "DARK_NAVY": 0x2C3E50,
}
bot.color_list = [c for c in bot.colors.values()]


@bot.event
async def on_ready():
    # On ready, print some details to standard out
    print(
        f"-----\nLogeado como : {bot.user.name} : {bot.user.id}\n-----\nCon el Prefijo: {bot.DEFAULTPREFIX}\n-----"
    )
    await bot.change_presence(
        activity=discord.Game(name="Tageame para saber que prefijo uso")
    )  # This changes the bots 'activity'

    for document in await bot.config.get_all():
        print(document)

    currentMutes = await bot.mutes.get_all()
    for mute in currentMutes:
        bot.muted_users[mute["_id"]] = mute

    print(bot.muted_users)

    print("Initialized Database\n-----")


@bot.event
async def on_message(message):
    # Ignore messages sent by yourself or bots
    if message.author.bot:
        return

    # A way to blacklist users from the bot by not processing commands
    # if the author is in the blacklisted_users list
    if message.author.id in bot.blacklisted_users:
        return

    # Whenever the bot is tagged, respond with its prefix
    if message.content.startswith(f"<@!{bot.user.id}>") and len(message.content) == len(
        f"<@!{bot.user.id}>"
    ):
        data = await bot.config.find_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = bot.DEFAULTPREFIX
        else:
            prefix = data["prefix"]
        await message.channel.send(f"Mi prefijo aqui es `{prefix}`", delete_after=15)

    await bot.process_commands(message)


if __name__ == "__main__":
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
    bot.db = bot.mongo["menudocs"]
    bot.config = Document(bot.db, "config")
    bot.mutes = Document(bot.db, "muteados")
    bot.warns = Document(bot.db, "notas")
    bot.invites = Document(bot.db, "invitaciones")
    bot.reaction_roles = Document(bot.db, "roles_reaccion")
    bot.keep_roles = Document(bot.db, "Keep_Roles")

    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")

    bot.run(bot.config_token)