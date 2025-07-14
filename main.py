import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Load token and keys from .env file
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Define prefix and intents
PREFIX = "&"
intents = discord.Intents.all()

# Create bot instance with hybrid command support
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Event: When the bot is ready
@bot.event
async def on_ready():
    # Set the bot's status
    activity = discord.Activity(type=discord.ActivityType.watching, name="SB Moderation | &help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        print(f"❌ Error syncing slash commands: {e}")

    print(f"✅ Logged in as {bot.user} (ID: {bot.user.id})")

