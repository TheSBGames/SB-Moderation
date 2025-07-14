# cogs/utility.py

import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        await ctx.send(user.avatar.url)

    @commands.command()
    async def userinfo(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        embed = discord.Embed(title=f"Info for {user}", color=discord.Color.green())
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=user.avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = discord.Embed(title=guild.name, color=discord.Color.blue())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Owner", value=guild.owner)
        embed.set_thumbnail(url=guild.icon.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
