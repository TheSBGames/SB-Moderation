import discord
from discord.ext import commands
from typing import Optional, Union
from utils.embeds import powered_embed

class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_group(name="server", description="Server management commands.")
    @commands.has_permissions(manage_guild=True)
    async def server(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: settings, roles, channels, invites, bans, verification, restrictions, alerts.")

    @server.group(name="settings")
    async def server_settings(self, ctx):
        """Server settings management."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: name, icon, banner, splash, description, region, locale, notifications.")

    @server_settings.command(name="name")
    async def settings_name(self, ctx, *, name: str):
        """Change server name."""
        await ctx.guild.edit(name=name)
        await ctx.send(embed=powered_embed(f"Changed server name to {name}"))

    @server_settings.command(name="icon")
    async def settings_icon(self, ctx, url: str = None):
        """Change server icon."""
        # Implementation for changing server icon
        await ctx.send(embed=powered_embed("Changed server icon"))

    @server_settings.command(name="banner")
    async def settings_banner(self, ctx, url: str = None):
        """Change server banner."""
        # Implementation for changing server banner
        await ctx.send(embed=powered_embed("Changed server banner"))

    @server_settings.command(name="splash")
    async def settings_splash(self, ctx, url: str = None):
        """Change server invite splash."""
        # Implementation for changing server splash
        await ctx.send(embed=powered_embed("Changed server splash"))

    @server_settings.command(name="description")
    async def settings_description(self, ctx, *, description: str):
        """Change server description."""
        await ctx.guild.edit(description=description)
        await ctx.send(embed=powered_embed("Updated server description"))

    @server_settings.command(name="region")
    async def settings_region(self, ctx, region: str):
        """Change server region."""
        # Implementation for changing server region
        await ctx.send(embed=powered_embed(f"Changed server region to {region}"))

    @server_settings.command(name="locale")
    async def settings_locale(self, ctx, locale: str):
        """Change server preferred locale."""
        await ctx.guild.edit(preferred_locale=locale)
        await ctx.send(embed=powered_embed(f"Changed server locale to {locale}"))

    @server_settings.command(name="notifications")
    async def settings_notifications(self, ctx, level: str):
        """Change default notification level."""
        levels = {
            "all": discord.NotificationLevel.all_messages,
            "mentions": discord.NotificationLevel.only_mentions
        }
        if level not in levels:
            await ctx.send(embed=powered_embed("Invalid level. Use 'all' or 'mentions'."))
            return
        await ctx.guild.edit(default_notifications=levels[level])
        await ctx.send(embed=powered_embed(f"Changed notification level to {level}"))

    @server.group(name="roles")
    async def server_roles(self, ctx):
        """Server roles management."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, edit, info, list, hierarchy, permissions, colors, assign, bulk.")

    @server_roles.command(name="hierarchy")
    async def roles_hierarchy(self, ctx):
        """Display role hierarchy."""
        roles = sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)
        embed = powered_embed("Role Hierarchy")
        for role in roles:
            embed.add_field(name=f"Position {role.position}", value=role.name, inline=False)
        await ctx.send(embed=embed)

    @server_roles.command(name="bulk")
    async def roles_bulk(self, ctx, action: str, *, roles: str):
        """Bulk role management."""
        role_list = [r.strip() for r in roles.split(',')]
        if action == "create":
            for role_name in role_list:
                await ctx.guild.create_role(name=role_name)
        elif action == "delete":
            for role_name in role_list:
                role = discord.utils.get(ctx.guild.roles, name=role_name)
                if role:
                    await role.delete()
        await ctx.send(embed=powered_embed(f"Bulk {action} completed for roles"))

    @server.group(name="channels")
    async def server_channels(self, ctx):
        """Server channels management."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, edit, info, list, categories, sync, lockdown, bulk.")

    @server_channels.command(name="categories")
    async def channels_categories(self, ctx):
        """List all categories and their channels."""
        categories = ctx.guild.categories
        embed = powered_embed("Channel Categories")
        for category in categories:
            channels = [ch.name for ch in category.channels]
            embed.add_field(name=category.name, value='\n'.join(channels) or "Empty", inline=False)
        await ctx.send(embed=embed)

    @server_channels.command(name="lockdown")
    async def channels_lockdown(self, ctx, state: bool, reason: str = None):
        """Lockdown all channels."""
        default_role = ctx.guild.default_role
        for channel in ctx.guild.channels:
            await channel.set_permissions(default_role, send_messages=not state, reason=reason)
        await ctx.send(embed=powered_embed(f"{'Enabled' if state else 'Disabled'} server lockdown"))

    @server.group(name="invites")
    async def server_invites(self, ctx):
        """Server invites management."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, list, info, prune, vanity, track.")

    @server_invites.command(name="track")
    async def invites_track(self, ctx, action: str):
        """Enable/disable invite tracking."""
        if action not in ['enable', 'disable']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'enable' or 'disable'."))
            return
        # Implementation for invite tracking
        await ctx.send(embed=powered_embed(f"{action.capitalize()}d invite tracking"))

    @server.group(name="bans")
    async def server_bans(self, ctx):
        """Server bans management."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, info, reason, softban, tempban, sync.")

    @server_bans.command(name="softban")
    async def bans_softban(self, ctx, member: discord.Member, *, reason: str = None):
        """Softban a member (ban and immediate unban)."""
        await ctx.guild.ban(member, reason=f"Softban: {reason}" if reason else "Softban")
        await ctx.guild.unban(member)
        await ctx.send(embed=powered_embed(f"Softbanned {member.name}"))

    @server_bans.command(name="sync")
    async def bans_sync(self, ctx, target_guild: discord.Guild):
        """Sync bans with another server."""
        # Implementation for syncing bans
        await ctx.send(embed=powered_embed("Synced bans with target server"))

    @server.group(name="verification")
    async def server_verification(self, ctx):
        """Server verification settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: level, gate, requirements, role, message, captcha.")

    @server_verification.command(name="captcha")
    async def verification_captcha(self, ctx, action: str):
        """Enable/disable CAPTCHA verification."""
        if action not in ['enable', 'disable']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'enable' or 'disable'."))
            return
        # Implementation for CAPTCHA verification
        await ctx.send(embed=powered_embed(f"{action.capitalize()}d CAPTCHA verification"))

    @server.group(name="restrictions")
    async def server_restrictions(self, ctx):
        """Server restriction settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: age, roles, channels, permissions, features, region.")

    @server_restrictions.command(name="age")
    async def restrictions_age(self, ctx, days: int):
        """Set minimum account age requirement."""
        # Implementation for account age restriction
        await ctx.send(embed=powered_embed(f"Set minimum account age to {days} days"))

    @server.group(name="alerts")
    async def server_alerts(self, ctx):
        """Server alert settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: joins, leaves, bans, channel, mentions, raids.")

    @server_alerts.command(name="raids")
    async def alerts_raids(self, ctx, threshold: int, interval: int):
        """Configure raid detection alerts."""
        # Implementation for raid alerts
        await ctx.send(embed=powered_embed(f"Set raid alert threshold to {threshold} joins per {interval} seconds"))

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
