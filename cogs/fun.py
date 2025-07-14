# cogs/fun.py

import discord
from discord.ext import commands
import random

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx):
        await ctx.send(f"🎲 You rolled a {random.randint(1, 6)}!")

    @commands.command()
    async def coin(self, ctx):
        await ctx.send(f"🪙 You flipped: {random.choice(['Heads', 'Tails'])}")

    @commands.command()
    async def eightball(self, ctx, *, question):
        responses = ["Yes", "No", "Maybe", "Ask again later", "Definitely", "Absolutely not"]
        await ctx.send(f"🎱 {random.choice(responses)}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
