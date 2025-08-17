import discord
from discord.ext import commands
from typing import Union, Optional
from utils.embeds import powered_embed

class AutoModPunishments(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="automod_punishments", description="Configure AutoMod punishments.")
    async def punishments(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: actions, escalation, thresholds, warnings, appeals, exemptions, logs.")

    @punishments.group(name="actions")
    async def actions_settings(self, ctx):
        """Configure punishment actions."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, modify, reset.")

    @actions_settings.command(name="add")
    async def actions_add(self, ctx, violation: str, action: str, duration: int = 0):
        """Add a punishment action for a violation."""
        valid_actions = ["warn", "mute", "kick", "ban", "timeout"]
        if action not in valid_actions:
            await ctx.send(embed=powered_embed(f"Invalid action. Valid actions: {', '.join(valid_actions)}"))
            return

        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {f'punishments.actions.{violation}': {'type': action, 'duration': duration}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added punishment: {action} for {violation}"))

    @actions_settings.command(name="remove")
    async def actions_remove(self, ctx, violation: str):
        """Remove a punishment action."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {f'punishments.actions.{violation}': ""}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Removed punishment for {violation}"))

    @actions_settings.command(name="list")
    async def actions_list(self, ctx):
        """List all punishment actions."""
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        actions = doc.get('punishments', {}).get('actions', {})
        embed = powered_embed("Punishment Actions")
        for violation, action in actions.items():
            embed.add_field(name=violation, value=f"Type: {action['type']}, Duration: {action['duration']}", inline=False)
        await ctx.send(embed=embed)

    @actions_settings.command(name="modify")
    async def actions_modify(self, ctx, violation: str, action: str, duration: int = 0):
        """Modify an existing punishment action."""
        valid_actions = ["warn", "mute", "kick", "ban", "timeout"]
        if action not in valid_actions:
            await ctx.send(embed=powered_embed(f"Invalid action. Valid actions: {', '.join(valid_actions)}"))
            return

        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {f'punishments.actions.{violation}': {'type': action, 'duration': duration}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Modified punishment for {violation}"))

    @actions_settings.command(name="reset")
    async def actions_reset(self, ctx):
        """Reset all punishment actions to default."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {'punishments.actions': ""}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Reset all punishment actions to default"))

    @punishments.group(name="escalation")
    async def escalation_settings(self, ctx):
        """Configure punishment escalation."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: enable, disable, steps, reset, timeout.")

    @escalation_settings.command(name="enable")
    async def escalation_enable(self, ctx, enabled: bool):
        """Enable/disable punishment escalation."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.escalation.enabled': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} punishment escalation"))

    @escalation_settings.command(name="steps")
    async def escalation_steps(self, ctx, violation: str, *, steps: str):
        """Set escalation steps for a violation."""
        try:
            steps_list = [step.strip() for step in steps.split(',')]
            await self.db.automod_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {f'punishments.escalation.steps.{violation}': steps_list}},
                upsert=True
            )
            await ctx.send(embed=powered_embed(f"Set escalation steps for {violation}"))
        except Exception as e:
            await ctx.send(embed=powered_embed(f"Error: {str(e)}"))

    @escalation_settings.command(name="reset")
    async def escalation_reset(self, ctx, violation: str = None):
        """Reset escalation steps for a violation or all violations."""
        update = {'$unset': {f'punishments.escalation.steps.{violation}': ""}} if violation else {'$unset': {'punishments.escalation.steps': ""}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"Reset escalation steps for {violation if violation else 'all violations'}"))

    @escalation_settings.command(name="timeout")
    async def escalation_timeout(self, ctx, hours: int):
        """Set timeout period for escalation reset."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.escalation.timeout': hours}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set escalation timeout to {hours} hours"))

    @punishments.group(name="thresholds")
    async def thresholds_settings(self, ctx):
        """Configure punishment thresholds."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: set, remove, list, reset.")

    @thresholds_settings.command(name="set")
    async def thresholds_set(self, ctx, violation: str, warnings: int, action: str):
        """Set threshold for a violation."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {f'punishments.thresholds.{violation}': {'warnings': warnings, 'action': action}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set threshold for {violation}"))

    @thresholds_settings.command(name="remove")
    async def thresholds_remove(self, ctx, violation: str):
        """Remove threshold for a violation."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {f'punishments.thresholds.{violation}': ""}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Removed threshold for {violation}"))

    @thresholds_settings.command(name="list")
    async def thresholds_list(self, ctx):
        """List all thresholds."""
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        thresholds = doc.get('punishments', {}).get('thresholds', {})
        embed = powered_embed("Punishment Thresholds")
        for violation, data in thresholds.items():
            embed.add_field(name=violation, value=f"Warnings: {data['warnings']}, Action: {data['action']}", inline=False)
        await ctx.send(embed=embed)

    @thresholds_settings.command(name="reset")
    async def thresholds_reset(self, ctx):
        """Reset all thresholds."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {'punishments.thresholds': ""}},
            upsert=True
        )
        await ctx.send(embed=powered_embed("Reset all thresholds"))

    @punishments.group(name="warnings")
    async def warnings_settings(self, ctx):
        """Configure warning settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, clear, decay.")

    @warnings_settings.command(name="add")
    async def warnings_add(self, ctx, member: discord.Member, reason: str):
        """Add a warning to a member."""
        await self.db.warnings.insert_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id,
            'reason': reason,
            'timestamp': discord.utils.utcnow()
        })
        await ctx.send(embed=powered_embed(f"Added warning for {member.name}: {reason}"))

    @warnings_settings.command(name="remove")
    async def warnings_remove(self, ctx, member: discord.Member, warning_id: str):
        """Remove a warning from a member."""
        await self.db.warnings.delete_one({
            'guild_id': ctx.guild.id,
            'user_id': member.id,
            '_id': warning_id
        })
        await ctx.send(embed=powered_embed(f"Removed warning from {member.name}"))

    @warnings_settings.command(name="list")
    async def warnings_list(self, ctx, member: discord.Member):
        """List all warnings for a member."""
        warnings = await self.db.warnings.find({
            'guild_id': ctx.guild.id,
            'user_id': member.id
        }).to_list(length=None)
        
        embed = powered_embed(f"Warnings for {member.name}")
        for warning in warnings:
            embed.add_field(
                name=f"ID: {warning['_id']}",
                value=f"Reason: {warning['reason']}\nDate: {warning['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
                inline=False
            )
        await ctx.send(embed=embed)

    @warnings_settings.command(name="clear")
    async def warnings_clear(self, ctx, member: discord.Member):
        """Clear all warnings from a member."""
        await self.db.warnings.delete_many({
            'guild_id': ctx.guild.id,
            'user_id': member.id
        })
        await ctx.send(embed=powered_embed(f"Cleared all warnings from {member.name}"))

    @warnings_settings.command(name="decay")
    async def warnings_decay(self, ctx, days: int):
        """Set warning decay time in days."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.warnings.decay_days': days}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set warning decay time to {days} days"))

    @punishments.group(name="appeals")
    async def appeals_settings(self, ctx):
        """Configure punishment appeals."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: enable, disable, channel, cooldown.")

    @appeals_settings.command(name="enable")
    async def appeals_enable(self, ctx, enabled: bool):
        """Enable/disable appeals system."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.appeals.enabled': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} appeals system"))

    @appeals_settings.command(name="channel")
    async def appeals_channel(self, ctx, channel: discord.TextChannel):
        """Set appeals channel."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.appeals.channel_id': channel.id}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set appeals channel to {channel.mention}"))

    @appeals_settings.command(name="cooldown")
    async def appeals_cooldown(self, ctx, days: int):
        """Set appeals cooldown period."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'punishments.appeals.cooldown_days': days}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set appeals cooldown to {days} days"))

    @punishments.group(name="exemptions")
    async def exemptions_settings(self, ctx):
        """Configure punishment exemptions."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: roles, channels, users.")

    @exemptions_settings.command(name="roles")
    async def exemptions_roles(self, ctx, action: str, role: discord.Role):
        """Add/remove exempt roles."""
        if action not in ['add', 'remove']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'add' or 'remove'."))
            return

        update = {'$addToSet' if action == 'add' else '$pull': {'punishments.exemptions.roles': role.id}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed exempt role: {role.name}"))

    @exemptions_settings.command(name="channels")
    async def exemptions_channels(self, ctx, action: str, channel: discord.TextChannel):
        """Add/remove exempt channels."""
        if action not in ['add', 'remove']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'add' or 'remove'."))
            return

        update = {'$addToSet' if action == 'add' else '$pull': {'punishments.exemptions.channels': channel.id}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed exempt channel: {channel.name}"))

    @exemptions_settings.command(name="users")
    async def exemptions_users(self, ctx, action: str, user: discord.Member):
        """Add/remove exempt users."""
        if action not in ['add', 'remove']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'add' or 'remove'."))
            return

        update = {'$addToSet' if action == 'add' else '$pull': {'punishments.exemptions.users': user.id}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed exempt user: {user.name}"))

async def setup(bot):
    await bot.add_cog(AutoModPunishments(bot))
