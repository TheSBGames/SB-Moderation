# main.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load token from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "&"

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    await bot.tree.sync()
    print("✅ Slash commands synced.")

# List of cogs to load
initial_cogs = [
    "cogs.automod",
    "cogs.moderation",
    "cogs.utility",
    "cogs.fun",
    "cogs.music",
    "cogs.modmail",
    "cogs.tickets",
    "cogs.chatgpt",
]

for cog in initial_cogs:
    try:
        bot.load_extension(cog)
        print(f"✅ Loaded cog: {cog}")
    except Exception as e:
        print(f"❌ Failed to load cog {cog}: {e}")

# Run bot
if __name__ == "__main__":
    bot.run(TOKEN)
