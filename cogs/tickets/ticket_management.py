import discord
from discord.ext import commands
from typing import Optional
from utils.embeds import powered_embed

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="tickets", description="Ticket system commands.")
    @commands.has_permissions(manage_guild=True)
    async def tickets(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: setup, panel, category, team, settings, logs, archive, blacklist.")

    @tickets.group(name="setup")
    async def ticket_setup(self, ctx):
        """Setup ticket system."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: enable, disable, channel, category, message, embed, button.")

    @ticket_setup.command(name="enable")
    async def setup_enable(self, ctx):
        """Enable ticket system."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.enabled': True}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Enabled ticket system"))

    @ticket_setup.command(name="disable")
    async def setup_disable(self, ctx):
        """Disable ticket system."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.enabled': False}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Disabled ticket system"))

    @ticket_setup.command(name="channel")
    async def setup_channel(self, ctx, channel: discord.TextChannel):
        """Set ticket creation channel."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.channel_id': channel.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set ticket channel to {channel.mention}"))

    @tickets.group(name="panel")
    async def ticket_panel(self, ctx):
        """Manage ticket panels."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, edit, delete, list, button, description, color.")

    @ticket_panel.command(name="create")
    async def panel_create(self, ctx, name: str, *, description: str):
        """Create a new ticket panel."""
        await self.db.ticket_panels.insert_one({
            'guild_id': ctx.guild.id,
            'name': name,
            'description': description
        })
        await ctx.send(embed=powered_embed(f"Created ticket panel: {name}"))

    @ticket_panel.command(name="edit")
    async def panel_edit(self, ctx, panel_id: str, *, new_description: str):
        """Edit a ticket panel."""
        await self.db.ticket_panels.update_one(
            {'_id': panel_id, 'guild_id': ctx.guild.id},
            {'$set': {'description': new_description}}
        )
        await ctx.send(embed=powered_embed("Updated ticket panel"))

    @tickets.group(name="category")
    async def ticket_category(self, ctx):
        """Manage ticket categories."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, edit, list, assign, unassign, permissions.")

    @ticket_category.command(name="create")
    async def category_create(self, ctx, name: str):
        """Create a new ticket category."""
        category = await ctx.guild.create_category(name)
        await self.db.ticket_categories.insert_one({
            'guild_id': ctx.guild.id,
            'name': name,
            'category_id': category.id
        })
        await ctx.send(embed=powered_embed(f"Created ticket category: {name}"))

    @tickets.group(name="team")
    async def ticket_team(self, ctx):
        """Manage support team settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, role, permissions, schedule, activity.")

    @ticket_team.command(name="add")
    async def team_add(self, ctx, member: discord.Member, role: str = "Support"):
        """Add a member to support team."""
        await self.db.support_team.insert_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id,
            'role': role
        })
        await ctx.send(embed=powered_embed(f"Added {member.name} to support team as {role}"))

    @tickets.group(name="settings")
    async def ticket_settings(self, ctx):
        """Configure ticket settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: limit, cooldown, naming, close, transcripts, responses, notifications.")

    @ticket_settings.command(name="limit")
    async def settings_limit(self, ctx, limit: int):
        """Set maximum open tickets per user."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.user_limit': limit}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set ticket limit to {limit} per user"))

    @tickets.group(name="logs")
    async def ticket_logs(self, ctx):
        """Manage ticket logs."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: channel, enable, disable, search, export, stats, activity.")

    @ticket_logs.command(name="channel")
    async def logs_channel(self, ctx, channel: discord.TextChannel):
        """Set ticket log channel."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.log_channel_id': channel.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set ticket logs channel to {channel.mention}"))

    @tickets.group(name="archive")
    async def ticket_archive(self, ctx):
        """Manage ticket archives."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: enable, disable, channel, duration, download, search, cleanup.")

    @ticket_archive.command(name="enable")
    async def archive_enable(self, ctx):
        """Enable ticket archiving."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'tickets.archive_enabled': True}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Enabled ticket archiving"))

    @tickets.group(name="blacklist")
    async def ticket_blacklist(self, ctx):
        """Manage ticket blacklist."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, reason, duration, appeal.")

    @ticket_blacklist.command(name="add")
    async def blacklist_add(self, ctx, member: discord.Member, *, reason: str):
        """Add user to ticket blacklist."""
        await self.db.ticket_blacklist.insert_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id,
            'reason': reason,
            'added_by': ctx.author.id,
            'timestamp': discord.utils.utcnow()
        })
        await ctx.send(embed=powered_embed(f"Added {member.name} to ticket blacklist"))

    @commands.Cog.listener()
    async def on_button_click(self, interaction: discord.Interaction):
        """Handle ticket button clicks."""
        if not interaction.data.get('custom_id', '').startswith('ticket_'):
            return
        
        # Implementation for button handling
        await interaction.response.send_message(embed=powered_embed("Creating your ticket..."), ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
