import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "&"

# Intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Remove default help to allow custom help later
bot.remove_command("help")

# List of cogs
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

async def main():
    # Load extensions
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            print(f"🔹 Loaded {cog}")
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")
    
    # Start keep_alive server (only needed for Replit/UptimeRobot)
    keep_alive()

    # Start bot
    try:
        await bot.start(TOKEN)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
    
