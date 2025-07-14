# Converted moderation cog to hybrid commands
# File: cogs/moderation.py

import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ban", description="Ban a user from the server.")
    @app_commands.describe(member="The member to ban", reason="Reason for ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await ctx.send(f"🔨 {member.mention} has been **banned** for: `{reason}`")

    @commands.hybrid_command(name="kick", description="Kick a user from the server.")
    @app_commands.describe(member="The member to kick", reason="Reason for kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.mention} has been **kicked** for: `{reason}`")

    @commands.hybrid_command(name="mute", description="Mute a user for a number of minutes.")
    @app_commands.describe(member="The member to mute", duration="Duration in minutes")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx: commands.Context, member: discord.Member, duration: int = 5):
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

    @commands.hybrid_command(name="unmute", description="Unmute a user.")
    @app_commands.describe(member="The member to unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await ctx.send(f"🔊 {member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} is not muted.")

    @commands.hybrid_command(name="purge", description="Delete a number of messages from the channel.")
    @app_commands.describe(amount="Number of messages to delete")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx: commands.Context, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Deleted `{amount}` messages.", delete_after=3)

    @commands.hybrid_command(name="warn", description="Warn a user.")
    @app_commands.describe(member="The member to warn", reason="Reason for the warning")
    @commands.has_permissions(manage_roles=True)
    async def warn(self, ctx: commands.Context, member: discord.Member, *, reason="No reason provided"):
        await ctx.send(f"⚠️ {member.mention} has been warned for: `{reason}`")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
