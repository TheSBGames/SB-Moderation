import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
PREFIX = "&"

# Intents setup
intents = discord.Intents.all()

# Create bot with command prefix and intents
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Event: On ready
@bot.event
async def on_ready():
    # Set the bot's custom status
    activity = discord.Activity(type=discord.ActivityType.watching, name="SB Moderation | &help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Sync slash commands

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
    print(f"❌ Error syncing slash commands: {e}")

