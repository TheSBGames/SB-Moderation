import discord
from discord.ext import commands

async def on_ready(bot: commands.Bot):
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    print('------')
    # Optionally, you can load any necessary data or perform startup tasks here.