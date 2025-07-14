import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Load .env variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Safety check
if not TOKEN:
    print("❌ DISCORD_TOKEN is missing from environment variables!")
    exit(1)

# Bot prefix and intents
PREFIX = "&"
intents = discord.Intents.all()

# Create the bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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
