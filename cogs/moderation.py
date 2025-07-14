# cogs/moderation.py

import discord
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been **banned** for: `{reason}`")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been **kicked** for: `{reason}`")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 5):
        """Mute a user by giving them a 'Muted' role (default 5 mins)."""
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted", permissions=discord.Permissions(send_messages=False))
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, send_messages=False)

        await member.add_roles(mute_role)
        await ctx.send(f"🔇 {member.mention} has been muted for {duration} minutes.")

        await asyncio.sleep(duration * 60)
        await member.remove_roles(mute_role)
        await ctx.send(f"🔊 {member.mention} has been unmuted.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"🔊 {member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Deleted `{amount}` messages.", delete_after=3)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await ctx.send(f"⚠️ {member.mention} has been warned for: `{reason}`")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
