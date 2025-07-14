# cogs/automation.py

import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime

class Automation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.auto_messages.start()

    auto_data = [
        {"channel_id": 123456789012345678, "message": "💡 Remember to read the rules!", "interval": 3600}
    ]

    @tasks.loop(seconds=60)
    async def auto_messages(self):
        now = datetime.utcnow()
        for msg in self.auto_data:
            channel = self.bot.get_channel(msg["channel_id"])
            if channel and now.minute % (msg["interval"] // 60) == 0:
                await channel.send(msg["message"])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def remindme(self, ctx, time: int, *, message: str):
        """Set a reminder (in minutes)."""
        await ctx.send(f"⏰ Reminder set for {time} minutes.")
        await asyncio.sleep(time * 60)
        await ctx.author.send(f"🔔 Reminder: {message}")

async def setup(bot):
    await bot.add_cog(Automation(bot))
