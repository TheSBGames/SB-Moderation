import discord
from discord.ext import commands
import asyncio
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

async def load_all_extensions():
    for cog in initial_cogs:
        try:
            await bot.load_extension(cog)
            print(f"🔹 Loaded {cog}")
            await asyncio.sleep(1)  # Add delay to prevent rate-limiting
        except Exception as e:
            print(f"❌ Failed to load {cog}: {e}")

async def main():
    async with bot:
        await load_all_extensions()
        try:
            await bot.start(TOKEN)
        except Exception as e:
            print(f"❌ Error starting bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
