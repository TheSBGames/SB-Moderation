import discord
from datetime import timedelta
from discord import app_commands, Member, Embed
from discord.ext import commands
from core.logger import logger
from utils.embeds import powered_embed
from utils.permissions import owner_only

class Moderation(commands.Cog):
    @commands.hybrid_group(name="moderation", description="Moderation command group.")
    async def moderation(self, ctx):
        """Moderation command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: ban, kick, timeout, mute, warn, warnings, clear.")

    @moderation.command(name="ban")
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        await ctx.send(f"Banned {member.mention} for reason: {reason}")

    @moderation.command(name="kick")
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        await ctx.send(f"Kicked {member.mention} for reason: {reason}")

    @moderation.group(name="timeout")
    async def timeout(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list.")

    @timeout.command(name="add")
    async def timeout_add(self, ctx, member: discord.Member, minutes: int = 30):
        await ctx.send(f"Timed out {member.mention} for {minutes} minutes.")

    @timeout.command(name="remove")
    async def timeout_remove(self, ctx, member: discord.Member):
        await ctx.send(f"Removed timeout for {member.mention}.")

    @timeout.command(name="list")
    async def timeout_list(self, ctx):
        await ctx.send("List of timed out members (implement logic)")

    @moderation.command(name="mute")
    async def mute(self, ctx, member: discord.Member, minutes: int = None):
        await ctx.send(f"Muted {member.mention} for {minutes if minutes else 'indefinite'} minutes.")

    @moderation.command(name="warn")
    async def warn(self, ctx, member: discord.Member, *, reason: str = None):
        await ctx.send(f"Warned {member.mention} for reason: {reason}")

    @moderation.command(name="warnings")
    async def warnings(self, ctx, member: discord.Member):
        await ctx.send(f"Warnings for {member.mention} (implement logic)")

    @moderation.command(name="clear")
    async def clear(self, ctx, amount: int = 5):
        await ctx.send(f"Cleared {amount} messages (implement logic)")
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @owner_only()
    @commands.hybrid_command(name="setstatus", description="Sets the bot presence.")
    async def set_status(self, status: str):
        await self.bot.change_presence(activity=discord.Game(name=status))
        await self.bot.get_context(self).send(embed=powered_embed("Status updated successfully."))

    @commands.hybrid_command(name="ban", description="Ban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, member: Member, *, reason: str = "No reason provided."):
        await member.ban(reason=reason)
        await self.bot.get_context(self).send(embed=powered_embed(f"Banned {member.mention} for: {reason}"))
        logger.info(f"Banned {member} for: {reason}")

    @commands.hybrid_command(name="kick", description="Kick a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, member: Member, *, reason: str = "No reason provided."):
        await member.kick(reason=reason)
        await self.bot.get_context(self).send(embed=powered_embed(f"Kicked {member.mention} for: {reason}"))
        logger.info(f"Kicked {member} for: {reason}")

    @commands.hybrid_command(name="timeout", description="Timeout a member for a specified duration.")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, member: Member, minutes: int = 30):
        await member.edit(timeout=discord.utils.utcnow() + timedelta(minutes=minutes))
        await self.bot.get_context(self).send(embed=powered_embed(f"Timed out {member.mention} for {minutes} minutes."))
        logger.info(f"Timed out {member} for {minutes} minutes.")

    @commands.hybrid_command(name="untimeout", description="Remove timeout from a member.")
    async def untimeout(self, member: Member):
        await member.edit(timeout=None)
        await self.bot.get_context(self).send(embed=powered_embed(f"Removed timeout from {member.mention}."))
        logger.info(f"Removed timeout from {member}.")

    @commands.hybrid_command(name="mute", description="Mute a member for a specified duration.")
    async def mute(self, member: Member, minutes: int = None):
        # Implement mute logic here (e.g., assigning a mute role)
        await self.bot.get_context(self).send(embed=powered_embed(f"Muted {member.mention} for {minutes} minutes." if minutes else "Muted {member.mention}."))
        logger.info(f"Mute {member} for {minutes} minutes." if minutes else f"Mute {member}.")

    @commands.hybrid_command(name="warn", description="Warn a member.")
    async def warn(self, member: Member, *, reason: str):
        # Implement warning logic here (e.g., incrementing warnings in the database)
        await self.bot.get_context(self).send(embed=powered_embed(f"Warned {member.mention} for: {reason}"))
        logger.info(f"Warned {member} for: {reason}")

    @commands.hybrid_command(name="warnings", description="List warnings for a member.")
    async def warnings(self, member: Member):
        # Implement logic to retrieve and display warnings
        await self.bot.get_context(self).send(embed=powered_embed(f"Warnings for {member.mention}: ..."))  # Replace with actual warnings
        logger.info(f"Retrieved warnings for {member}")

    @commands.hybrid_command(name="clear", description="Clear messages in a channel.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, amount: int = 5):
        await self.bot.get_context(self).channel.purge(limit=amount)
        await self.bot.get_context(self).send(embed=powered_embed(f"Cleared {amount} messages."))
        logger.info(f"Cleared {amount} messages.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))