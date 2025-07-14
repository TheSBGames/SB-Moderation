# cogs/chatgpt.py

import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatGPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ask")
    async def ask_chatgpt(self, ctx, *, question: str):
        """Ask ChatGPT anything using &ask [question]"""
        await ctx.trigger_typing()

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful Discord assistant."},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )

            answer = response.choices[0].message.content
            if len(answer) > 2000:
                answer = answer[:1990] + "..."

            await ctx.reply(answer)

        except Exception as e:
            await ctx.send(f"⚠️ Error: {e}")

async def setup(bot):
    await bot.add_cog(ChatGPT(bot))
