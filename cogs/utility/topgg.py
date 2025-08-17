import discord
from discord.ext import commands, tasks
import aiohttp
import os
from core.logger import get_logger
from discord import Webhook, app_commands
import asyncio
from datetime import datetime, timedelta
from core.config import Config

class TopGG(commands.Cog):
    """
    Handles Top.gg (Discord Bot List) integration
    """
    def __init__(self, bot):
        self.bot = bot
        self.logger = get_logger()
        self.stats_url = f"https://top.gg/api/bots/{self.bot.user.id}/stats"
        self.update_stats.start()

    def cog_unload(self):
        self.update_stats.cancel()

    @tasks.loop(minutes=30)
    async def update_stats(self):
        """
        Automatically updates Top.gg stats every 30 minutes
        """
        if not hasattr(self.bot, 'user') or not self.bot.user:
            return

        try:
            headers = {
                "Authorization": os.getenv('TOPGG_TOKEN')
            }
            
            # Get total guild count across all shards
            guild_count = len(self.bot.guilds)
            shard_count = self.bot.shard_count or 1
            
            payload = {
                "server_count": guild_count,
                "shard_count": shard_count,
                "shard_id": 0  # If not sharded, use 0
            }

            if self.bot.is_ready():
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.stats_url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            self.logger.info(
                                f"Posted stats to Top.gg: {guild_count} servers",
                                extra={
                                    'guild_count': guild_count,
                                    'shard_count': shard_count
                                }
                            )
                        else:
                            self.logger.error(
                                f"Failed to post Top.gg stats. Status: {resp.status}",
                                extra={'response': await resp.text()}
                            )

        except Exception as e:
            self.logger.error(f"Error updating Top.gg stats: {str(e)}")

    @update_stats.before_loop
    async def before_update_stats(self):
        await self.bot.wait_until_ready()
        # Wait 5 minutes after startup to ensure accurate stats
        await asyncio.sleep(300)

    async def process_vote(self, user_id: int):
        """Log votes from users"""
        try:
            user = await self.bot.fetch_user(user_id)
            if not user:
                return

            # Update user's vote timestamp and count
            await self.bot.db.user_votes.update_one(
                {'_id': user_id},
                {
                    '$set': {
                        'last_vote': datetime.utcnow().isoformat(),
                    },
                    '$inc': {'vote_count': 1}
                },
                upsert=True
            )

            # Send thank you DM
            try:
                vote_count = await self.get_vote_count(user_id)
                embed = discord.Embed(
                    title="Thanks for Voting!",
                    description=(
                        "Thank you for supporting SB Moderation! "
                        "Your vote helps us grow and reach more communities.\n\n"
                        f"Total Votes: {vote_count}\n"
                        "Next vote available in 12 hours!"
                    ),
                    color=discord.Color.blue()
                )
                await user.send(embed=embed)
            except discord.Forbidden:
                pass  # User has DMs disabled

            self.logger.info(
                f"Processed vote for {user}",
                extra={
                    'user_id': user_id,
                    'vote_count': await self.get_vote_count(user_id)
                }
            )

        except Exception as e:
            self.logger.error(f"Error processing vote: {str(e)}")

    async def get_vote_count(self, user_id: int) -> int:
        """Get the total number of votes for a user"""
        try:
            user_data = await self.bot.db.user_votes.find_one({'_id': user_id})
            return user_data.get('vote_count', 0) if user_data else 0
        except Exception as e:
            self.logger.error(f"Error getting vote count: {str(e)}")
            return 0

    @commands.hybrid_group(name="vote", description="Top.gg voting commands")
    async def vote(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🗳️ Vote for SB Moderation",
                description=(
                    "Support us by voting on Top.gg!\n\n"
                    "Voting helps us:\n"
                    "• Reach more communities\n"
                    "• Improve our services\n"
                    "• Stay motivated to add new features\n\n"
                    "[Click here to vote!](https://top.gg/bot/{self.bot.user.id}/vote)"
                ),
                color=discord.Color.blue()
            )
            
            # Add vote streak if any
            vote_count = await self.get_vote_count(ctx.author.id)
            if vote_count > 0:
                embed.add_field(
                    name="Your Voting Stats",
                    value=f"Total Votes: {vote_count}",
                    inline=False
                )
            
            await ctx.send(embed=embed)

    @vote.command(name="stats", description="View your voting statistics")
    async def vote_stats(self, ctx):
        try:
            user_data = await self.bot.db.user_votes.find_one({'_id': ctx.author.id})
            
            if not user_data:
                await ctx.send("You haven't voted for the bot yet!")
                return

            embed = discord.Embed(
                title="🗳️ Your Voting Statistics",
                color=discord.Color.blue()
            )
            
            vote_count = user_data.get('vote_count', 0)
            last_vote = user_data.get('last_vote')
            
            embed.add_field(
                name="Total Votes",
                value=str(vote_count),
                inline=False
            )
            
            if last_vote:
                last_vote_time = datetime.fromisoformat(last_vote)
                embed.add_field(
                    name="Last Vote",
                    value=f"<t:{int(last_vote_time.timestamp())}:R>",
                    inline=False
                )

            # Add next vote eligibility status
            if last_vote:
                next_vote = last_vote_time + timedelta(hours=12)  # Top.gg has 12-hour vote cooldown
                if next_vote > datetime.utcnow():
                    embed.add_field(
                        name="Next Vote Available",
                        value=f"<t:{int(next_vote.timestamp())}:R>",
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="Vote Status",
                        value="You can vote now!",
                        inline=False
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            self.logger.error(f"Error displaying vote stats: {str(e)}")
            await ctx.send("An error occurred while fetching your vote statistics.")

    # Removed voterewards command as it's no longer needed

async def setup(bot):
    await bot.add_cog(TopGG(bot))
