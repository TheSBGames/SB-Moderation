import discord
import asyncio
from discord import VoiceChannel, Member
from discord.ext import commands

class TempVoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_voice_channels = {}

    @commands.hybrid_group(name="tempvoice", description="Temporary Voice command group.")
    async def tempvoice(self, ctx):
        """Temporary Voice command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, delete, list, settings, cleanup.")

    @tempvoice.command(name="create")
    async def create(self, ctx):
        await ctx.send("Created temporary voice channel (implement logic)")

    @tempvoice.command(name="delete")
    async def delete(self, ctx, channel_id: int):
        await ctx.send(f"Deleted temporary voice channel {channel_id} (implement logic)")

    @tempvoice.command(name="list")
    async def list_channels(self, ctx):
        await ctx.send("List of temporary voice channels (implement logic)")

    @tempvoice.command(name="settings")
    async def settings(self, ctx):
        await ctx.send("Temporary voice settings (implement logic)")

    @tempvoice.command(name="cleanup")
    async def cleanup(self, ctx):
        await ctx.send("Cleaned up empty temporary voice channels (implement logic)")
    def __init__(self, bot):
        self.bot = bot
        self.temp_voice_channels = {}

    @commands.command(name='createvc')
    async def create_temp_voice_channel(self, ctx):
        """Creates a temporary voice channel for the user."""
        if ctx.author.voice:
            channel_name = f"Temp VC - {ctx.author.name}"
            category = ctx.author.voice.channel.category
            temp_channel = await category.create_voice_channel(channel_name)

            await ctx.author.move_to(temp_channel)
            self.temp_voice_channels[temp_channel.id] = ctx.author.id

            await temp_channel.send(f"{ctx.author.mention}, you have created a temporary voice channel!")

            # Delete the channel when empty
            await self.delete_empty_channel(temp_channel)
        else:
            await ctx.send("You need to be in a voice channel to create a temporary one.")

    async def delete_empty_channel(self, channel: VoiceChannel):
        """Deletes the voice channel if it becomes empty."""
        while True:
            await asyncio.sleep(10)  # Check every 10 seconds
            if len(channel.members) == 0:
                await channel.delete()
                del self.temp_voice_channels[channel.id]
                break

    @commands.command(name='deletevc')
    async def delete_temp_voice_channel(self, ctx):
        """Deletes the user's temporary voice channel if it exists."""
        for channel_id, user_id in list(self.temp_voice_channels.items()):
            if user_id == ctx.author.id:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    await channel.delete()
                    del self.temp_voice_channels[channel_id]
                    await ctx.send(f"{ctx.author.mention}, your temporary voice channel has been deleted.")
                    return
        await ctx.send("You do not have a temporary voice channel to delete.")

async def setup(bot):
    await bot.add_cog(TempVoiceCog(bot))