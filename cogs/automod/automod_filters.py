import discord
from discord.ext import commands
from typing import Dict, List, Union
from utils.embeds import powered_embed

class AutoModFilters(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="automod_filters", description="Configure AutoMod filters.")
    async def filters(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: spam, links, content, regex, attachments, mentions.")

    @filters.group(name="spam")
    async def spam_settings(self, ctx):
        """Configure spam filter settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: messages, emojis, mentions, capitals, lines, duplicates.")

    @spam_settings.command(name="messages")
    async def spam_messages(self, ctx, limit: int, interval: int):
        """Set message spam limits."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.messages': {'limit': limit, 'interval': interval}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set message spam limit to {limit} messages per {interval} seconds"))

    @spam_settings.command(name="emojis")
    async def spam_emojis(self, ctx, limit: int):
        """Set emoji spam limits."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.emojis': limit}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set emoji limit to {limit} per message"))

    @spam_settings.command(name="mentions")
    async def spam_mentions(self, ctx, limit: int):
        """Set mention spam limits."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.mentions': limit}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set mention limit to {limit} per message"))

    @spam_settings.command(name="capitals")
    async def spam_capitals(self, ctx, percentage: int):
        """Set capital letter percentage limit."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.capitals': percentage}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set capital letters limit to {percentage}%"))

    @spam_settings.command(name="lines")
    async def spam_lines(self, ctx, limit: int):
        """Set line count limit per message."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.lines': limit}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set line limit to {limit} per message"))

    @spam_settings.command(name="duplicates")
    async def spam_duplicates(self, ctx, enabled: bool, interval: int = 30):
        """Enable/disable duplicate message detection."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'spam_settings.duplicates': {'enabled': enabled, 'interval': interval}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} duplicate message detection"))

    @filters.group(name="links")
    async def links_settings(self, ctx):
        """Configure link filter settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: block, whitelist, blacklist, domains, discord.")

    @links_settings.command(name="block")
    async def links_block(self, ctx, enabled: bool):
        """Enable/disable link blocking."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'links.block_all': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} link blocking"))

    @links_settings.command(name="whitelist")
    async def links_whitelist(self, ctx, domain: str):
        """Add domain to whitelist."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$addToSet': {'links.whitelist': domain}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {domain} to link whitelist"))

    @links_settings.command(name="blacklist")
    async def links_blacklist(self, ctx, domain: str):
        """Add domain to blacklist."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$addToSet': {'links.blacklist': domain}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added {domain} to link blacklist"))

    @links_settings.command(name="domains")
    async def links_domains(self, ctx):
        """List whitelisted and blacklisted domains."""
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        links = doc.get('links', {})
        embed = powered_embed("Link Filter Domains")
        embed.add_field(name="Whitelist", value="\n".join(links.get('whitelist', [])) or "None")
        embed.add_field(name="Blacklist", value="\n".join(links.get('blacklist', [])) or "None")
        await ctx.send(embed=embed)

    @links_settings.command(name="discord")
    async def links_discord(self, ctx, enabled: bool):
        """Enable/disable Discord invite link filtering."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'links.block_discord': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} Discord invite filtering"))

    @filters.group(name="content")
    async def content_settings(self, ctx):
        """Configure content filter settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: words, phrases, mass_mentions, everyone, tokens.")

    @content_settings.command(name="words")
    async def content_words(self, ctx, action: str, *, word: str):
        """Add/remove filtered words."""
        if action not in ['add', 'remove']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'add' or 'remove'."))
            return

        update = {'$addToSet' if action == 'add' else '$pull': {'content.filtered_words': word}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed word from filter"))

    @content_settings.command(name="phrases")
    async def content_phrases(self, ctx, action: str, *, phrase: str):
        """Add/remove filtered phrases."""
        if action not in ['add', 'remove']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'add' or 'remove'."))
            return

        update = {'$addToSet' if action == 'add' else '$pull': {'content.filtered_phrases': phrase}}
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, update, upsert=True)
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed phrase from filter"))

    @content_settings.command(name="mass_mentions")
    async def content_mass_mentions(self, ctx, enabled: bool, threshold: int = 5):
        """Configure mass mention filtering."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'content.mass_mentions': {'enabled': enabled, 'threshold': threshold}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} mass mention filtering"))

    @content_settings.command(name="everyone")
    async def content_everyone(self, ctx, enabled: bool):
        """Enable/disable @everyone/@here filtering."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'content.block_everyone': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} @everyone/@here filtering"))

    @content_settings.command(name="tokens")
    async def content_tokens(self, ctx, enabled: bool):
        """Enable/disable Discord token filtering."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'content.block_tokens': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} Discord token filtering"))

    @filters.group(name="regex")
    async def regex_settings(self, ctx):
        """Configure regex filter settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list, test.")

    @regex_settings.command(name="add")
    async def regex_add(self, ctx, name: str, pattern: str):
        """Add a regex pattern."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {f'regex.patterns.{name}': pattern}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Added regex pattern: {name}"))

    @regex_settings.command(name="remove")
    async def regex_remove(self, ctx, name: str):
        """Remove a regex pattern."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$unset': {f'regex.patterns.{name}': ""}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Removed regex pattern: {name}"))

    @regex_settings.command(name="list")
    async def regex_list(self, ctx):
        """List all regex patterns."""
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        patterns = doc.get('regex', {}).get('patterns', {})
        embed = powered_embed("Regex Patterns")
        for name, pattern in patterns.items():
            embed.add_field(name=name, value=pattern, inline=False)
        await ctx.send(embed=embed)

    @regex_settings.command(name="test")
    async def regex_test(self, ctx, name: str, *, text: str):
        """Test a regex pattern."""
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        pattern = doc.get('regex', {}).get('patterns', {}).get(name)
        if not pattern:
            await ctx.send(embed=powered_embed(f"Pattern {name} not found"))
            return
        import re
        matches = re.findall(pattern, text)
        await ctx.send(embed=powered_embed(f"Test results for {name}:\nMatches: {matches if matches else 'None'}"))

    @filters.group(name="attachments")
    async def attachments_settings(self, ctx):
        """Configure attachment filter settings."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: types, size, scan, dimensions.")

    @attachments_settings.command(name="types")
    async def attachments_types(self, ctx, action: str, filetype: str):
        """Configure allowed/blocked file types."""
        if action not in ['allow', 'block']:
            await ctx.send(embed=powered_embed("Invalid action. Use 'allow' or 'block'."))
            return

        update_field = 'attachments.allowed_types' if action == 'allow' else 'attachments.blocked_types'
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$addToSet': {update_field: filetype}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{action.capitalize()}ed file type: {filetype}"))

    @attachments_settings.command(name="size")
    async def attachments_size(self, ctx, max_size: int):
        """Set maximum file size in MB."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'attachments.max_size': max_size}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set maximum file size to {max_size}MB"))

    @attachments_settings.command(name="scan")
    async def attachments_scan(self, ctx, enabled: bool):
        """Enable/disable file scanning."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'attachments.scan_files': enabled}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"{'Enabled' if enabled else 'Disabled'} file scanning"))

    @attachments_settings.command(name="dimensions")
    async def attachments_dimensions(self, ctx, max_width: int, max_height: int):
        """Set maximum image dimensions."""
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'attachments.max_dimensions': {'width': max_width, 'height': max_height}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set maximum image dimensions to {max_width}x{max_height}"))

async def setup(bot):
    await bot.add_cog(AutoModFilters(bot))
