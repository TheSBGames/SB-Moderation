import discord
from discord.ext import commands
from discord import app_commands

class MicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Prefix command: &mic
    @commands.command(name="mic")
    async def mic_prefix(self, ctx):
        await ctx.send("🎤 This is the prefix command: &mic")

    # Slash command: /mic
    @app_commands.command(name="mic", description="🎤 Respond with mic status")
    async def mic_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message("🎤 This is the slash command: /mic")

    # Make sure slash commands work
    @commands.Cog.listener()
    async def on_ready(self):
        try:
            self.bot.tree.add_command(self.mic_slash)
        except Exception as e:
            print(f"⚠️ Failed to register /mic: {e}")

async def setup(bot):
    await bot.add_cog(MicCog(bot))
