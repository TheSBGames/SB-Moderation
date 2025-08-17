import discord
from discord import Embed, Member
from discord.ext import commands
from core.database import Database
from utils.embeds import powered_embed

class Leveling(commands.Cog):
    @commands.hybrid_group(name="leveling", description="Leveling command group.")
    async def leveling(self, ctx):
        """Leveling command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: rank, leaderboard, enable, disable, xp.")

    @leveling.command(name="rank")
    async def rank(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(f"Rank for {user.mention} (implement logic)")

    @leveling.command(name="leaderboard")
    async def leaderboard(self, ctx):
        await ctx.send("Leaderboard (implement logic)")

    @leveling.command(name="enable")
    async def enable(self, ctx):
        await ctx.send("Leveling enabled (implement logic)")

    @leveling.command(name="disable")
    async def disable(self, ctx):
        await ctx.send("Leveling disabled (implement logic)")

    @leveling.group(name="xp")
    async def xp(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: set, add, remove.")

    @xp.command(name="set")
    async def xp_set(self, ctx, user: discord.Member, amount: int):
        await ctx.send(f"Set XP for {user.mention} to {amount} (implement logic)")

    @xp.command(name="add")
    async def xp_add(self, ctx, user: discord.Member, amount: int):
        await ctx.send(f"Added {amount} XP to {user.mention} (implement logic)")

    @xp.command(name="remove")
    async def xp_remove(self, ctx, user: discord.Member, amount: int):
        await ctx.send(f"Removed {amount} XP from {user.mention} (implement logic)")
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database(bot.config.MONGO_URI).db

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Add XP logic here
        xp_gained = 10  # Example XP gain
        await self.add_xp(message.author.id, xp_gained)

    async def add_xp(self, user_id: int, xp: int):
        user_data = await self.db.levels.find_one({'_id': user_id})
        if user_data:
            new_xp = user_data['xp'] + xp
            new_level = self.calculate_level(new_xp)
            await self.db.levels.update_one({'_id': user_id}, {'$set': {'xp': new_xp, 'level': new_level}})
        else:
            await self.db.levels.insert_one({'_id': user_id, 'xp': xp, 'level': 1})

    def calculate_level(self, xp: int) -> int:
        # Example level calculation based on XP
        return int(xp ** 0.5)

    @commands.hybrid_command(name="rank", description="Check your rank and XP.")
    async def rank(self, ctx, member: Member = None):
        member = member or ctx.author
        user_data = await self.db.levels.find_one({'_id': member.id})
        
        if user_data:
            embed = powered_embed(title=f"{member.display_name}'s Rank", description=f"Level: {user_data['level']}\nXP: {user_data['xp']}")
        else:
            embed = powered_embed(title=f"{member.display_name}'s Rank", description="No data found.")
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="leaderboard", description="Show the top users by XP.")
    async def leaderboard(self, ctx):
        top_users = await self.db.levels.find().sort('xp', -1).limit(10).to_list(length=10)
        embed = powered_embed(title="Leaderboard")
        
        for index, user in enumerate(top_users, start=1):
            embed.add_field(name=f"{index}. User ID: {user['_id']}", value=f"Level: {user['level']} | XP: {user['xp']}", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Leveling(bot))