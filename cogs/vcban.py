# cogs/vcban.py

import discord
from discord.ext import commands

class VCBan(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc_banned = set()

    @commands.command()
    @commands.has_permissions(move_members=True)
    async def vcban(self, ctx, member: discord.Member):
        self.vc_banned.add(member.id)
        if member.voice:
            await member.move_to(None)
        await ctx.send(f"🚫 {member.mention} has been VC banned.")

    @commands.command()
    @commands.has_permissions(move_members=True)
    async def vcunban(self, ctx, member: discord.Member):
        self.vc_banned.discard(member.id)
        await ctx.send(f"✅ {member.mention} has been VC unbanned.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id in self.vc_banned and after.channel is not None:
            await member.move_to(None)

async def setup(bot):
    await bot.add_cog(VCBan(bot))
