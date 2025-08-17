import os
import discord
from discord.ext import commands
from core.config import Config
from core.database import Database
from core.logger import setup_logger

async def main():
    # Load configuration
    config = Config()
    
    # Set up logging
    logger = setup_logger()
    
    # Initialize the bot
    bot = commands.Bot(command_prefix=config.PREFIX, intents=discord.Intents.default())
    bot.db = Database(config.MONGO_URI).db
    bot.author_credit = "Powered By SB Moderation™"

    # Load cogs
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

    # Start the bot
    await bot.start(config.BOT_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())