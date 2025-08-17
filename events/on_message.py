from discord import Message
from discord.ext import commands
from core.bot import Bot

async def on_message(bot: Bot, message: Message):
    if message.author.bot:
        return

    # Check for no-prefix users
    if await bot.db.noprefix_users.find_one({'_id': message.author.id}):
        if not message.content.startswith(bot.command_prefix):
            ctx = await bot.get_context(message)
            if not ctx.valid:
                cmd_name = message.content.split()[0].lower()
                cmd = bot.get_command(cmd_name)
                if cmd:
                    await bot.invoke(ctx)
    
    # Additional message processing can be added here

def setup(bot: Bot):
    bot.add_listener(on_message, 'on_message')