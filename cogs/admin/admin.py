import discord
from discord import Embed
from discord.ext import commands
from core.config import PREFIX, OWNER_ID
from utils.embeds import powered_embed

class Admin(commands.Cog):
    @commands.hybrid_group(name="admin", description="Admin command group.")
    async def admin(self, ctx):
        """Admin command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: setstatus, reload, np.")

    @admin.command(name="setstatus")
    async def setstatus(self, ctx, *, status: str):
        await ctx.send(f"Set bot status to: {status} (implement logic)")

    @admin.group(name="reload")
    async def reload(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: cog, all.")

    @reload.command(name="cog")
    async def reload_cog(self, ctx, cog: str):
        await ctx.send(f"Reloaded cog: {cog} (implement logic)")

    @reload.command(name="all")
    async def reload_all(self, ctx):
        await ctx.send("Reloaded all cogs (implement logic)")

    @admin.group(name="np")
    async def np(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: add, remove, list.")

    @np.command(name="add")
    async def np_add(self, ctx, user: discord.Member):
        await ctx.send(f"Added {user.mention} to no-prefix users (implement logic)")

    @np.command(name="remove")
    async def np_remove(self, ctx, user: discord.Member):
        await ctx.send(f"Removed {user.mention} from no-prefix users (implement logic)")

    @np.command(name="list")
    async def np_list(self, ctx):
        await ctx.send("List of no-prefix users (implement logic)")
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="setstatus", description="Sets the bot's presence.")
    @commands.is_owner()
    async def set_status(self, status: str):
        await self.bot.change_presence(activity=discord.Game(name=status))
        embed = powered_embed(title="Status Updated", description=f"Bot status set to: {status}")
        await self.bot.get_channel(OWNER_ID).send(embed=embed)

    @commands.hybrid_command(name="reload", description="Reloads a cog.")
    @commands.is_owner()
    async def reload_cog(self, cog: str):
        try:
            self.bot.reload_extension(f'cogs.{cog}')
            embed = powered_embed(title="Cog Reloaded", description=f"Successfully reloaded: {cog}")
        except Exception as e:
            embed = powered_embed(title="Error", description=f"Failed to reload: {cog}\nError: {str(e)}")
        await self.bot.get_channel(OWNER_ID).send(embed=embed)

    @commands.hybrid_command(name="np", description="Manage no-prefix users.")
    @commands.is_owner()
    async def noprefix(self, action: str, user: commands.MemberConverter = None):
        if action == "add":
            # Logic to add user to noprefix_users
            embed = powered_embed(title="No-Prefix User Added", description=f"User {user} added to no-prefix list.")
        elif action == "remove":
            # Logic to remove user from noprefix_users
            embed = powered_embed(title="No-Prefix User Removed", description=f"User {user} removed from no-prefix list.")
        elif action == "list":
            # Logic to list no-prefix users
            embed = powered_embed(title="No-Prefix Users", description="List of no-prefix users.")
        else:
            embed = powered_embed(title="Error", description="Invalid action. Use add, remove, or list.")
        
        await self.bot.get_channel(OWNER_ID).send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))