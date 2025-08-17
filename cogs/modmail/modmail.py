import discord
from discord import Embed, Message, User
from discord.ext import commands
from core.database import Database
from core.logger import get_logger
from utils.embeds import powered_embed

logger = get_logger(__name__)

class ModMail(commands.Cog):
    @commands.hybrid_group(name="modmail", description="ModMail command group.")
    async def modmail(self, ctx):
        """ModMail command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: thread, reply, close, list, transcript.")

    @modmail.command(name="thread")
    async def thread(self, ctx, user: discord.Member):
        await ctx.send(f"Opened modmail thread for {user.mention} (implement logic)")

    @modmail.command(name="reply")
    async def reply(self, ctx, thread_id: str, *, message: str):
        await ctx.send(f"Replied to thread {thread_id}: {message} (implement logic)")

    @modmail.command(name="close")
    async def close(self, ctx, thread_id: str):
        await ctx.send(f"Closed modmail thread {thread_id} (implement logic)")

    @modmail.command(name="list")
    async def list_threads(self, ctx):
        await ctx.send("List of modmail threads (implement logic)")

    @modmail.command(name="transcript")
    async def transcript(self, ctx, thread_id: str):
        await ctx.send(f"Transcript for thread {thread_id} (implement logic)")
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database(bot.config.MONGO_URI).db

    async def get_modmail_channel(self, guild_id: int):
        # Fetch the modmail channel from the database
        modmail_config = await self.db.modmail_threads.find_one({'_id': guild_id})
        return modmail_config['modmail_channel'] if modmail_config else None

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        
        # Check if the message is a DM
        if isinstance(message.channel, discord.DMChannel):
            guild_id = self.get_guild_id_from_user(message.author.id)
            modmail_channel_id = await self.get_modmail_channel(guild_id)
            if modmail_channel_id:
                modmail_channel = self.bot.get_channel(modmail_channel_id)
                if modmail_channel:
                    embed = powered_embed(title="New ModMail", description=message.content, color=0x00ff00)
                    await modmail_channel.send(embed=embed)
                    await message.channel.send("Your message has been sent to the staff.")
                else:
                    await message.channel.send("ModMail channel not found.")
            else:
                await message.channel.send("ModMail is not set up for this server.")

    def get_guild_id_from_user(self, user_id: int):
        # Logic to retrieve the guild ID from the user ID
        # This is a placeholder and should be implemented based on your logic
        return 123456789012345678  # Replace with actual logic

async def setup(bot: commands.Bot):
    await bot.add_cog(ModMail(bot))