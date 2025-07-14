import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Prefix and intents
PREFIX = "&"
intents = discord.Intents.all()

# Create hybrid bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# Set up event when bot is ready
@bot.event
async def on_ready():
    # Set bot presence
    activity = discord.Activity(type=discord.ActivityType.watching, name="SB Moderation | &help or /help")
    await bot.change_presence(status=discord.Status.online, activity=activity)

    # Sync slash comman
