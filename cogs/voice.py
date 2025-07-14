# cogs/voice.py

import discord
from discord.ext import commands

class VoiceTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(move_members=True)
    async def move(self, ctx, member: discord.Member, channel: discord.VoiceChannel):
        await member.move_to(channel)
        await ctx.send(f"🔁 Moved {member.mention} to {channel.mention}")

    @commands.command()
    @commands.has_permissions(mute_members=True)
    async def vcmute(self, ctx, member: discord.Member):
        await member.edit(mute=True)
        await ctx.send(f"🔇 Muted {member.mention} in voice")

    @commands.command()
    @commands.has_permissions(mute_members=True)
    async def vcunmute(self, ctx, member: discord.Member):
        await member.edit(mute=False)
        await ctx.send(f"🔊 Unmuted {member.mention} in voice")

async def setup(bot):
    await bot.add_cog(VoiceTools(bot))
