# cogs/modmail.py

import discord
from discord.ext import commands

MODMAIL_CHANNEL_ID = 123456789012345678  # Replace with your actual channel ID

class ModMail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore messages from bots
        if message.author.bot:
            return

        # Handle ModMail
        if isinstance(message.channel, discord.DMChannel):
            guild = self.bot.guilds[0]  # assumes one guild
            channel = guild.get_channel(MODMAIL_CHANNEL_ID)

            if channel:
                embed = discord.Embed(
                    title="📬 New ModMail",
                    description=message.content,
                    color=discord.Color.orange()
                )
                embed.set_author(name=str(message.author), icon_url=message.author.display_avatar.url)
                embed.set_footer(text=f"User ID: {message.author.id}")

                await channel.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def reply(self, ctx, user_id: int, *, message: str):
        """Reply to a modmail message."""
        user = self.bot.get_user(user_id)
        if user:
            try:
                await user.send(f"💌 Reply from staff:\n{message}")
                await ctx.send("✅ Message sent.")
            except discord.Forbidden:
                await ctx.send("❌ Couldn't send DM. User has DMs off.")
        else:
            await ctx.send("❌ User not found.")

async def setup(bot):
    await bot.add_cog(ModMail(bot))
