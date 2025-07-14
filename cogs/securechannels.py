# cogs/securechannels.py

import discord
from discord.ext import commands

class SecureChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.passwords = {}  # Temporary session memory

    @commands.command()
    async def lockchannel(self, ctx, *, password: str):
        """Locks current channel with a password."""
        self.passwords[ctx.channel.id] = password
        await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=False)
        await ctx.send("🔐 This channel is now locked.")

    @commands.command()
    async def unlockchannel(self, ctx, *, password: str):
        if self.passwords.get(ctx.channel.id) == password:
            await ctx.channel.set_permissions(ctx.guild.default_role, view_channel=True)
            del self.passwords[ctx.channel.id]
            await ctx.send("🔓 Channel unlocked.")
        else:
            await ctx.send("❌ Incorrect password.")

async def setup(bot):
    await bot.add_cog(SecureChannels(bot))
