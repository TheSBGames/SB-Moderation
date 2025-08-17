import discord
from discord.ext import commands
from typing import Optional, Union, List
from utils.embeds import powered_embed

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="autorole", description="Auto-role management commands.")
    @commands.has_permissions(manage_roles=True)
    async def autorole(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: join, bot, boost, level, reaction, verification, settings, conditions.")

    @autorole.group(name="join")
    async def join_roles(self, ctx):
        """Manage roles given on join."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, delay, requirements, toggle, human, bot.")

    @join_roles.command(name="add")
    async def join_add(self, ctx, role: discord.Role):
        """Add a role to give on join."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$addToSet': {'join_roles': role.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {role.name} to join roles"))

    @join_roles.command(name="remove")
    async def join_remove(self, ctx, role: discord.Role):
        """Remove a role from join roles."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$pull': {'join_roles': role.id}}
        )
        await ctx.send(embed=powered_embed(f"Removed {role.name} from join roles"))

    @autorole.group(name="bot")
    async def bot_roles(self, ctx):
        """Manage roles given to bots."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, requirements, toggle.")

    @bot_roles.command(name="add")
    async def bot_add(self, ctx, role: discord.Role):
        """Add a role to give to bots."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$addToSet': {'bot_roles': role.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {role.name} to bot roles"))

    @autorole.group(name="boost")
    async def boost_roles(self, ctx):
        """Manage roles given on server boost."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, stack, requirements, temporary.")

    @boost_roles.command(name="add")
    async def boost_add(self, ctx, role: discord.Role):
        """Add a role to give on boost."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$addToSet': {'boost_roles': role.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {role.name} to boost roles"))

    @autorole.group(name="level")
    async def level_roles(self, ctx):
        """Manage roles given on reaching levels."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, requirements, stack, temporary.")

    @level_roles.command(name="add")
    async def level_add(self, ctx, role: discord.Role, level: int):
        """Add a role for a level requirement."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {f'level_roles.{role.id}': level}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {role.name} for level {level}"))

    @autorole.group(name="reaction")
    async def reaction_roles(self, ctx):
        """Manage reaction roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, edit, list, button, menu, unique, temporary.")

    @reaction_roles.command(name="create")
    async def reaction_create(self, ctx, role: discord.Role, emoji: str, *, description: str = None):
        """Create a reaction role."""
        await self.db.reaction_roles.insert_one({
            'guild_id': ctx.guild.id,
            'role_id': role.id,
            'emoji': emoji,
            'description': description
        })
        await ctx.send(embed=powered_embed(f"Created reaction role for {role.name}"))

    @autorole.group(name="verification")
    async def verification_roles(self, ctx):
        """Manage verification roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: set, remove, requirements, timeout, steps, captcha.")

    @verification_roles.command(name="set")
    async def verification_set(self, ctx, role: discord.Role):
        """Set verification role."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'verification_role': role.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set {role.name} as verification role"))

    @autorole.group(name="settings")
    async def autorole_settings(self, ctx):
        """Configure autorole settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: delay, stack, dm, requirements, logging, sync, reset.")

    @autorole_settings.command(name="delay")
    async def settings_delay(self, ctx, seconds: int):
        """Set delay before giving roles."""
        await self.db.autorole.update_one(
            {'guild_id': ctx.guild.id},
            {'$set': {'settings.delay': seconds}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set role delay to {seconds} seconds"))

    @autorole.group(name="conditions")
    async def autorole_conditions(self, ctx):
        """Manage role conditions."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, edit, test, logic, reset.")

    @autorole_conditions.command(name="add")
    async def conditions_add(self, ctx, role: discord.Role, condition_type: str, *, value: str):
        """Add a condition for role assignment."""
        await self.db.autorole_conditions.insert_one({
            'guild_id': ctx.guild.id,
            'role_id': role.id,
            'type': condition_type,
            'value': value
        })
        await ctx.send(embed=powered_embed(f"Added condition for {role.name}"))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Handle autorole on member join."""
        if member.bot:
            return await self.handle_bot_roles(member)
        return await self.handle_join_roles(member)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Handle autorole on member update."""
        if before.premium_since != after.premium_since:
            await self.handle_boost_roles(after)

    async def handle_join_roles(self, member):
        """Handle giving roles on join."""
        settings = await self.db.autorole.find_one({'guild_id': member.guild.id}) or {}
        join_roles = settings.get('join_roles', [])
        
        for role_id in join_roles:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Autorole: Join role")
                except discord.HTTPException:
                    continue

    async def handle_bot_roles(self, member):
        """Handle giving roles to bots."""
        settings = await self.db.autorole.find_one({'guild_id': member.guild.id}) or {}
        bot_roles = settings.get('bot_roles', [])
        
        for role_id in bot_roles:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Autorole: Bot role")
                except discord.HTTPException:
                    continue

    async def handle_boost_roles(self, member):
        """Handle giving roles on boost."""
        settings = await self.db.autorole.find_one({'guild_id': member.guild.id}) or {}
        boost_roles = settings.get('boost_roles', [])
        
        for role_id in boost_roles:
            role = member.guild.get_role(role_id)
            if role:
                try:
                    await member.add_roles(role, reason="Autorole: Boost role")
                except discord.HTTPException:
                    continue

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
