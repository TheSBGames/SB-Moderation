import discord
from discord.ext import commands
from typing import Optional, Union
from utils.embeds import powered_embed

class LevelingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="leveling", description="Leveling system commands.")
    async def leveling(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: rank, leaderboard, settings, rewards, roles, multipliers, badges, stats.")

    @leveling.group(name="settings")
    @commands.has_permissions(manage_guild=True)
    async def level_settings(self, ctx):
        """Configure leveling system settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: enable, disable, xp, cooldown, announce, blacklist, stack, reset.")

    @level_settings.command(name="enable")
    async def settings_enable(self, ctx):
        """Enable leveling system."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'leveling.enabled': True}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Enabled leveling system"))

    @level_settings.command(name="disable")
    async def settings_disable(self, ctx):
        """Disable leveling system."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'leveling.enabled': False}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Disabled leveling system"))

    @level_settings.command(name="xp")
    async def settings_xp(self, ctx, min_xp: int, max_xp: int):
        """Set XP gain range per message."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {
                'leveling.xp_range': {
                    'min': min_xp,
                    'max': max_xp
                }
            }},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set XP range to {min_xp}-{max_xp}"))

    @leveling.group(name="rewards")
    @commands.has_permissions(manage_guild=True)
    async def level_rewards(self, ctx):
        """Manage level rewards."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, edit, roles, items, temporary.")

    @level_rewards.command(name="add")
    async def rewards_add(self, ctx, level: int, reward_type: str, *, reward: str):
        """Add a level reward."""
        await self.db.level_rewards.insert_one({
            'guild_id': ctx.guild.id,
            'level': level,
            'type': reward_type,
            'reward': reward
        })
        await ctx.send(embed=powered_embed(f"Added {reward_type} reward for level {level}"))

    @leveling.group(name="roles")
    @commands.has_permissions(manage_guild=True)
    async def level_roles(self, ctx):
        """Manage level roles."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, stack, autorole, hierarchy, temporary.")

    @level_roles.command(name="add")
    async def roles_add(self, ctx, level: int, role: discord.Role):
        """Add a level role."""
        await self.db.level_roles.insert_one({
            'guild_id': ctx.guild.id,
            'level': level,
            'role_id': role.id
        })
        await ctx.send(embed=powered_embed(f"Added role {role.name} for level {level}"))

    @leveling.group(name="multipliers")
    @commands.has_permissions(manage_guild=True)
    async def level_multipliers(self, ctx):
        """Manage XP multipliers."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, channel, role, time, event, boost.")

    @level_multipliers.command(name="add")
    async def multipliers_add(self, ctx, type: str, target_id: int, multiplier: float):
        """Add an XP multiplier."""
        await self.db.xp_multipliers.insert_one({
            'guild_id': ctx.guild.id,
            'type': type,
            'target_id': target_id,
            'multiplier': multiplier
        })
        await ctx.send(embed=powered_embed(f"Added {multiplier}x multiplier for {type}"))

    @leveling.group(name="badges")
    async def level_badges(self, ctx):
        """Manage level badges."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, list, assign, remove, custom, display.")

    @level_badges.command(name="create")
    @commands.has_permissions(manage_guild=True)
    async def badges_create(self, ctx, name: str, emoji: str, requirement: str):
        """Create a new level badge."""
        await self.db.level_badges.insert_one({
            'guild_id': ctx.guild.id,
            'name': name,
            'emoji': emoji,
            'requirement': requirement
        })
        await ctx.send(embed=powered_embed(f"Created badge: {name} {emoji}"))

    @leveling.command(name="rank")
    async def rank(self, ctx, member: discord.Member = None):
        """Check rank of a user."""
        member = member or ctx.author
        user_data = await self.db.user_levels.find_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id
        })
        if not user_data:
            await ctx.send(embed=powered_embed(f"{member.name} hasn't earned any XP yet"))
            return
        
        # Create rank card
        await ctx.send(embed=powered_embed(f"Rank card for {member.name}"))

    @leveling.command(name="leaderboard")
    async def leaderboard(self, ctx, category: str = "xp"):
        """View the server leaderboard."""
        valid_categories = ["xp", "messages", "voice", "weekly", "monthly"]
        if category not in valid_categories:
            await ctx.send(embed=powered_embed(f"Invalid category. Valid categories: {', '.join(valid_categories)}"))
            return

        users = await self.db.user_levels.find({
            'guild_id': ctx.guild.id
        }).sort(category, -1).limit(10).to_list(length=None)

        embed = powered_embed("Server Leaderboard")
        for i, user in enumerate(users, 1):
            member = ctx.guild.get_member(user['user_id'])
            if member:
                embed.add_field(
                    name=f"#{i} {member.name}",
                    value=f"Level: {user.get('level', 0)}\nXP: {user.get('xp', 0)}",
                    inline=False
                )
        await ctx.send(embed=embed)

    @leveling.command(name="stats")
    async def stats(self, ctx, member: discord.Member = None):
        """View detailed leveling stats."""
        member = member or ctx.author
        stats = await self.db.user_levels.find_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id
        })
        if not stats:
            await ctx.send(embed=powered_embed(f"No stats found for {member.name}"))
            return

        embed = powered_embed(f"Leveling Stats for {member.name}")
        embed.add_field(name="Level", value=stats.get('level', 0))
        embed.add_field(name="XP", value=stats.get('xp', 0))
        embed.add_field(name="Messages", value=stats.get('messages', 0))
        embed.add_field(name="Voice Time", value=f"{stats.get('voice_minutes', 0)} minutes")
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle XP gain from messages."""
        if message.author.bot:
            return

        guild_settings = await self.db.guild_settings.find_one({'_id': message.guild.id}) or {}
        if not guild_settings.get('leveling', {}).get('enabled', False):
            return

        # Implementation for XP calculation and level up checks
        await self.process_message_xp(message)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle XP gain from voice activity."""
        if member.bot:
            return

        guild_settings = await self.db.guild_settings.find_one({'_id': member.guild.id}) or {}
        if not guild_settings.get('leveling', {}).get('enabled', False):
            return

        # Implementation for voice XP tracking
        await self.process_voice_xp(member, before, after)

    async def process_message_xp(self, message):
        """Process XP gain from a message."""
        # Implementation for XP processing
        pass

    async def process_voice_xp(self, member, before, after):
        """Process XP gain from voice activity."""
        # Implementation for voice XP processing
        pass

async def setup(bot):
    await bot.add_cog(LevelingSystem(bot))
