import discord
from discord.ext import commands
from typing import Optional, Union, Dict
from utils.embeds import powered_embed

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="autoresponder", description="Auto-responder management commands.")
    @commands.has_permissions(manage_guild=True)
    async def autoresponder(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: triggers, responses, conditions, variables, schedule, settings, stats.")

    @autoresponder.group(name="triggers")
    async def trigger_settings(self, ctx):
        """Manage auto-response triggers."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, edit, list, test, regex, exact, contains.")

    @trigger_settings.command(name="add")
    async def trigger_add(self, ctx, trigger_type: str, *, content: str):
        """Add a trigger."""
        await self.db.autoresponder.insert_one({
            'guild_id': ctx.guild.id,
            'type': trigger_type,
            'content': content,
            'creator_id': ctx.author.id
        })
        await ctx.send(embed=powered_embed(f"Added {trigger_type} trigger"))

    @trigger_settings.command(name="remove")
    async def trigger_remove(self, ctx, trigger_id: str):
        """Remove a trigger."""
        await self.db.autoresponder.delete_one({
            'guild_id': ctx.guild.id,
            '_id': trigger_id
        })
        await ctx.send(embed=powered_embed("Removed trigger"))

    @autoresponder.group(name="responses")
    async def response_settings(self, ctx):
        """Manage auto-responses."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, edit, list, random, embed, reaction, file.")

    @response_settings.command(name="add")
    async def response_add(self, ctx, trigger_id: str, response_type: str, *, content: str):
        """Add a response to a trigger."""
        await self.db.autoresponder.update_one(
            {'guild_id': ctx.guild.id, '_id': trigger_id},
            {'$push': {'responses': {
                'type': response_type,
                'content': content
            }}}
        )
        await ctx.send(embed=powered_embed("Added response"))

    @autoresponder.group(name="conditions")
    async def condition_settings(self, ctx):
        """Manage response conditions."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, edit, list, channel, role, time, user, cooldown.")

    @condition_settings.command(name="add")
    async def condition_add(self, ctx, trigger_id: str, condition_type: str, *, value: str):
        """Add a condition to a trigger."""
        await self.db.autoresponder.update_one(
            {'guild_id': ctx.guild.id, '_id': trigger_id},
            {'$push': {'conditions': {
                'type': condition_type,
                'value': value
            }}}
        )
        await ctx.send(embed=powered_embed(f"Added {condition_type} condition"))

    @autoresponder.group(name="variables")
    async def variable_settings(self, ctx):
        """Manage response variables."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, edit, list, custom, global, user.")

    @variable_settings.command(name="add")
    async def variable_add(self, ctx, name: str, *, value: str):
        """Add a custom variable."""
        await self.db.autoresponder_vars.insert_one({
            'guild_id': ctx.guild.id,
            'name': name,
            'value': value
        })
        await ctx.send(embed=powered_embed(f"Added variable {name}"))

    @autoresponder.group(name="schedule")
    async def schedule_settings(self, ctx):
        """Manage scheduled responses."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, edit, list, cron, interval, once, recurring.")

    @schedule_settings.command(name="add")
    async def schedule_add(self, ctx, channel: discord.TextChannel, time: str, *, message: str):
        """Add a scheduled response."""
        await self.db.autoresponder_schedule.insert_one({
            'guild_id': ctx.guild.id,
            'channel_id': channel.id,
            'time': time,
            'message': message
        })
        await ctx.send(embed=powered_embed("Added scheduled response"))

    @autoresponder.group(name="settings")
    async def autoresponder_settings(self, ctx):
        """Configure auto-responder settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: toggle, cooldown, channels, roles, mentions, delete, log.")

    @autoresponder_settings.command(name="toggle")
    async def settings_toggle(self, ctx, enabled: bool):
        """Toggle auto-responder system."""
        await self.db.guild_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'autoresponder.enabled': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} auto-responder"))

    @autoresponder.group(name="stats")
    async def stats_settings(self, ctx):
        """View auto-responder statistics."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: triggers, responses, usage, popular, channels, users, export.")

    @stats_settings.command(name="triggers")
    async def stats_triggers(self, ctx):
        """View trigger statistics."""
        triggers = await self.db.autoresponder.find({'guild_id': ctx.guild.id}).to_list(length=None)
        embed = powered_embed("Trigger Statistics")
        embed.add_field(name="Total Triggers", value=str(len(triggers)))
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle auto-responses."""
        if message.author.bot:
            return

        # Get guild settings
        settings = await self.db.guild_settings.find_one({'_id': message.guild.id}) or {}
        if not settings.get('autoresponder', {}).get('enabled', False):
            return

        # Process triggers
        await self.process_triggers(message)

    async def process_triggers(self, message):
        """Process message triggers."""
        triggers = await self.db.autoresponder.find({
            'guild_id': message.guild.id
        }).to_list(length=None)

        for trigger in triggers:
            if await self.check_trigger(message, trigger):
                await self.send_response(message, trigger)

    async def check_trigger(self, message, trigger):
        """Check if message matches trigger."""
        content = message.content.lower()
        trigger_content = trigger['content'].lower()

        if trigger['type'] == 'exact':
            return content == trigger_content
        elif trigger['type'] == 'contains':
            return trigger_content in content
        elif trigger['type'] == 'regex':
            import re
            return bool(re.search(trigger_content, content))
        return False

    async def send_response(self, message, trigger):
        """Send trigger response."""
        for response in trigger.get('responses', []):
            try:
                if response['type'] == 'message':
                    await message.channel.send(response['content'])
                elif response['type'] == 'embed':
                    embed = discord.Embed.from_dict(response['content'])
                    await message.channel.send(embed=embed)
                elif response['type'] == 'reaction':
                    await message.add_reaction(response['content'])
            except discord.HTTPException:
                continue

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))
