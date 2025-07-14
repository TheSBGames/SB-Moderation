# main.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "&"

# Setup intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Remove default help command (optional)
bot.remove_command("help")

# List of cogs to load
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
    print("🌐 Bot is online and ready!")

    # Sync application (slash/hybrid) commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Slash command sync failed: {e}")

# Load cogs
if __name__ == "__main__":
    for cog in initial_cogs:
        try:
            bot.load_extension(cog)
            print(f"🔹 Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

    # Start keep_alive web server (optional for uptime services)
    keep_alive()

    # Run the bot
    try:
        bot.run(TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        
