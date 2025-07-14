# cogs/music.py

import discord
from discord.ext import commands
import yt_dlp
import asyncio

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}

    def search_youtube(self, query):
        with yt_dlp.YoutubeDL({'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
            return {'url': info['url'], 'title': info['title']}

    def create_source(self, url):
        return discord.FFmpegPCMAudio(url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5")

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
            await ctx.send("🔊 Joined voice channel.")
        else:
            await ctx.send("❌ You're not in a voice channel.")

    @commands.command()
    async def play(self, ctx, *, query):
        if not ctx.voice_client:
            await ctx.invoke(self.join)

        song = self.search_youtube(query)
        source = self.create_source(song['url'])
        ctx.voice_client.play(source)
        await ctx.send(f"▶️ Now playing: `{song['title']}`")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            await ctx.send("⏹️ Stopped music and left the channel.")

async def setup(bot):
    await bot.add_cog(Music(bot))
