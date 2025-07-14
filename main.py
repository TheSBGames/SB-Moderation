import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "&"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

initial_cogs = [
    "cogs.automod",
    "cogs.moderation",
    "cogs.utility",
    "cogs.fun",
    "cogs.music",
    "cogs.tickets",
    "cogs.modmail",
    "cogs.chatgpt",
    "cogs.voice",
    "cogs.securechannels",
    "cogs.vcban",
    "cogs.automation",
    "cogs.mic",
    "cogs.welcome",
    "cogs.customroles"
]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

if __name__ == "__main__":
    for cog in initial_cogs:
        try:
            bot.load_extension(cog)
            print(f"🔹 Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")
    
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
