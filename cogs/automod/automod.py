import discord
from discord import app_commands, Embed
from discord.ext import commands
from core.database import Database
from utils.embeds import powered_embed
from utils.permissions import owner_only

class AutoMod(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = bot.db

    @app_commands.command(name="automod_enable", description="Enable auto-moderation for the guild.")
    @commands.has_permissions(manage_guild=True)
    async def automod_enable(self, interaction: discord.Interaction):
        await self.db.automod_settings.update_one(
            {'_id': interaction.guild.id},
            {'$set': {'enabled': True}},
            upsert=True
        )
        await interaction.response.send_message(embed=powered_embed("Auto-moderation enabled."))

    @app_commands.command(name="automod_disable", description="Disable auto-moderation for the guild.")
    @commands.has_permissions(manage_guild=True)
    async def automod_disable(self, interaction: discord.Interaction):
        await self.db.automod_settings.update_one(
            {'_id': interaction.guild.id},
            {'$set': {'enabled': False}},
            upsert=True
        )
        await interaction.response.send_message(embed=powered_embed("Auto-moderation disabled."))

    @app_commands.command(name="automod_config", description="Configure auto-moderation settings.")
    @commands.has_permissions(manage_guild=True)
    async def automod_config(self, interaction: discord.Interaction):
        # Implementation for configuring automod settings
        pass
    # Granular automod commands
    @commands.hybrid_group(name="automod", description="Auto-moderation command group.")
    @commands.has_permissions(manage_guild=True)
    async def automod(self, ctx):
        """Auto-moderation command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send(embed=powered_embed("Use a subcommand: enable, disable, config, set, add, remove, list, whitelist."))

    @automod.command(name="enable")
    async def enable(self, ctx):
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$set': {'enabled': True}}, upsert=True)
        await ctx.send(embed=powered_embed("Auto-moderation enabled."))

    @automod.command(name="disable")
    async def disable(self, ctx):
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$set': {'enabled': False}}, upsert=True)
        await ctx.send(embed=powered_embed("Auto-moderation disabled."))

    @automod.command(name="set")
    async def set(self, ctx, feature: str, value: str):
        """Set automod feature (anti_links, anti_invites, anti_badwords) on/off."""
        valid_features = ["anti_links", "anti_invites", "anti_badwords"]
        if feature not in valid_features:
            await ctx.send(embed=powered_embed(f"Invalid feature. Valid: {', '.join(valid_features)}"))
            return
        val = value.lower() in ("true", "on", "yes", "1")
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$set': {feature: val}}, upsert=True)
        await ctx.send(embed=powered_embed(f"Set {feature} to {val}."))

    @automod.command(name="addbadword")
    async def addbadword(self, ctx, word: str):
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$addToSet': {'badwords': word}}, upsert=True)
        await ctx.send(embed=powered_embed(f"Added badword: {word}"))

    @automod.command(name="removebadword")
    async def removebadword(self, ctx, word: str):
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$pull': {'badwords': word}}, upsert=True)
        await ctx.send(embed=powered_embed(f"Removed badword: {word}"))

    @automod.command(name="listbadwords")
    async def listbadwords(self, ctx):
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        badwords = doc.get('badwords', [])
        if not badwords:
            await ctx.send(embed=powered_embed("No badwords set."))
        else:
            await ctx.send(embed=powered_embed(f"Badwords: {', '.join(badwords)}"))

    @automod.command(name="setpunishment")
    async def setpunishment(self, ctx, type: str, duration: int = 30):
        valid_types = ["timeout", "mute", "kick", "ban"]
        if type not in valid_types:
            await ctx.send(embed=powered_embed(f"Invalid punishment type. Valid: {', '.join(valid_types)}"))
            return
        await self.db.automod_settings.update_one(
            {'_id': ctx.guild.id},
            {'$set': {'action': {"type": type, "duration_minutes": duration}}},
            upsert=True
        )
        await ctx.send(embed=powered_embed(f"Set punishment: {type} ({duration} min)"))

    @automod.command(name="whitelistrole")
    async def whitelistrole(self, ctx, role: discord.Role):
        await self.db.automod_settings.update_one({'_id': ctx.guild.id}, {'$addToSet': {'bypass_roles': role.id}}, upsert=True)
        await ctx.send(embed=powered_embed(f"Whitelisted role: {role.name}"))

    @automod.command(name="listsettings")
    async def listsettings(self, ctx):
        doc = await self.db.automod_settings.find_one({'_id': ctx.guild.id}) or {}
        embed = powered_embed("AutoMod Settings")
        for k, v in doc.items():
            if k != "_id":
                embed.add_field(name=k, value=str(v), inline=False)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        automod_settings = await self.db.automod_settings.find_one({'_id': message.guild.id})
        if automod_settings and automod_settings.get('enabled'):
            # Implement automod logic here
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        
        automod_settings = await self.db.automod_settings.find_one({'_id': before.guild.id})
        if automod_settings and automod_settings.get('enabled'):
            # Implement edit detection logic here
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(AutoMod(bot))