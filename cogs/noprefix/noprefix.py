import discord
from discord import app_commands, Interaction, Member, SelectOption
from discord.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Optional
from core.config import PREFIX, OWNER_ID
from core.logger import get_logger
from utils.embeds import powered_embed

class NoPrefix(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check_expired_task.start()
        self.logger = get_logger()

    def cog_unload(self):
        self.check_expired_task.cancel()

    @tasks.loop(minutes=5.0)
    async def check_expired_task(self):
        """Check for and remove expired no-prefix users."""
        try:
            now = datetime.utcnow().isoformat()
            # Find and remove expired entries
            result = await self.bot.db.noprefix_users.delete_many({
                'expires_at': {'$lt': now}
            })
            if result.deleted_count > 0:
                self.logger.info(f"Removed {result.deleted_count} expired no-prefix users")
        except Exception as e:
            self.logger.error(f"Error checking expired no-prefix users: {str(e)}")

    @check_expired_task.before_loop
    async def before_check_expired(self):
        """Wait until the bot is ready before starting the task."""
        await self.bot.wait_until_ready()

    @commands.hybrid_group(name="noprefix", description="No-Prefix command group.")
    @commands.has_permissions(administrator=True)
    async def noprefix(self, ctx):
        """No-Prefix command group."""
        if ctx.invoked_subcommand is None:
            embed = powered_embed("No-Prefix Commands")
            embed.description = (
                "Available subcommands:\n"
                "• `/np_add` - Add a user to no-prefix list\n"
                "• `/np_remove` - Remove a user from no-prefix list\n"
                "• `/np_list` - List all no-prefix users\n"
                "• `/np_audit` - View audit log of no-prefix actions"
            )
            await ctx.send(embed=embed)

    @commands.hybrid_command(name="np_add", description="Add a user to no-prefix users.")
    @commands.has_permissions(administrator=True)
    async def np_add(self, interaction: Interaction, user: Member):
        """Add a user to the no-prefix users list with duration selection."""
        try:
            # Check if user already has no-prefix
            existing = await self.bot.db.noprefix_users.find_one({'_id': user.id})
            if existing:
                await interaction.response.send_message(
                    embed=powered_embed(f"{user.mention} already has no-prefix access."),
                    ephemeral=True
                )
                return

            view = NoPrefixDurationView(self.bot, interaction.user, user)
            embed = powered_embed("No-Prefix Duration Selection")
            embed.description = f"Select duration for {user.mention}'s no-prefix access:"
            embed.add_field(
                name="Note", 
                value="You can select a temporary duration or make it permanent."
            )
            await interaction.response.send_message(embed=embed, view=view)
            
            self.logger.info(
                f"No-prefix add initiated for {user} by {interaction.user} in {interaction.guild}"
            )
            
        except Exception as e:
            self.logger.error(f"Error in np_add: {str(e)}")
            await interaction.response.send_message(
                "An error occurred. Please try again.",
                ephemeral=True
            )
    @commands.hybrid_command(name="np_remove", description="Remove a user from no-prefix users.")
    @commands.has_permissions(administrator=True)
    async def np_remove(self, interaction: Interaction, user: Member):
        """Remove a user from the no-prefix users list."""
        try:
            result = await self.bot.db.noprefix_users.delete_one({'_id': user.id})
            
            if result.deleted_count > 0:
                embed = powered_embed("No-Prefix Access Removed")
                embed.description = f"Removed no-prefix access from {user.mention}."
                embed.add_field(name="Removed By", value=interaction.user.mention)
                
                # Add audit log entry
                await self.bot.db.noprefix_audit.insert_one({
                    'timestamp': datetime.utcnow().isoformat(),
                    'action': 'remove',
                    'actor_id': interaction.user.id,
                    'target_id': user.id
                })
                
                self.logger.info(
                    f"No-prefix removed from {user} by {interaction.user} in {interaction.guild}"
                )
                
                await interaction.response.send_message(embed=embed)
                
                # Try to notify the user
                try:
                    dm_embed = powered_embed("No-Prefix Access Removed")
                    dm_embed.description = "Your no-prefix access has been removed."
                    await user.send(embed=dm_embed)
                except discord.Forbidden:
                    pass
            else:
                await interaction.response.send_message(
                    embed=powered_embed(f"{user.mention} did not have no-prefix access."),
                    ephemeral=True
                )
                
        except Exception as e:
            self.logger.error(f"Error in np_remove: {str(e)}")
            await interaction.response.send_message(
                "An error occurred. Please try again.",
                ephemeral=True
            )

    @commands.hybrid_command(name="np_list", description="List all no-prefix users.")
    @commands.has_permissions(administrator=True)
    async def np_list(self, interaction: Interaction):
        """List all users in the no-prefix users list."""
        try:
            users = await self.bot.db.noprefix_users.find().to_list(length=None)
            
            if not users:
                await interaction.response.send_message(
                    embed=powered_embed("No users have no-prefix access."),
                    ephemeral=True
                )
                return

            embed = powered_embed("No-Prefix Users")
            
            for user in users:
                user_id = user['_id']
                added_by = user.get('added_by', 'Unknown')
                added_at = user.get('added_at', 'Unknown')
                expires_at = user.get('expires_at')
                
                try:
                    member = await interaction.guild.fetch_member(user_id)
                    name = member.mention
                except:
                    name = f"User ID: {user_id}"
                
                value = [
                    f"Added by: <@{added_by}>",
                    f"Added at: <t:{int(datetime.fromisoformat(added_at).timestamp())}:F>"
                ]
                
                if expires_at:
                    exp_time = datetime.fromisoformat(expires_at)
                    if exp_time > datetime.utcnow():
                        value.append(f"Expires: <t:{int(exp_time.timestamp())}:R>")
                    else:
                        value.append("Expired")
                else:
                    value.append("Duration: ♾️ Permanent")
                
                embed.add_field(
                    name=name,
                    value="\n".join(value),
                    inline=False
                )
            
            self.logger.info(f"No-prefix list viewed by {interaction.user} in {interaction.guild}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in np_list: {str(e)}")
            await interaction.response.send_message(
                "An error occurred. Please try again.",
                ephemeral=True
            )

    @commands.hybrid_command(name="np_audit", description="View no-prefix audit log.")
    @commands.has_permissions(administrator=True)
    async def np_audit(self, interaction: Interaction, limit: int = 10):
        """View the audit log for no-prefix actions."""
        try:
            if limit > 25:  # Reasonable limit to prevent huge messages
                limit = 25

            audit_log = await self.bot.db.noprefix_audit.find().sort(
                'timestamp', -1
            ).limit(limit).to_list(length=None)
            
            if not audit_log:
                await interaction.response.send_message(
                    embed=powered_embed("No audit log entries found."),
                    ephemeral=True
                )
                return
                
            embed = powered_embed("No-Prefix Audit Log")
            
            for entry in audit_log:
                timestamp = entry.get('timestamp')
                action = entry.get('action')
                target_id = entry.get('target_id')
                actor_id = entry.get('actor_id')
                details = entry.get('details', '')
                
                value = [
                    f"Action: {action}",
                    f"By: <@{actor_id}>",
                    f"Target: <@{target_id}>",
                    f"Details: {details}"
                ]
                
                embed.add_field(
                    name=f"<t:{int(datetime.fromisoformat(timestamp).timestamp())}:F>",
                    value="\n".join(value),
                    inline=False
                )
            
            self.logger.info(f"No-prefix audit log viewed by {interaction.user} in {interaction.guild}")
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            self.logger.error(f"Error in np_audit: {str(e)}")
            await interaction.response.send_message(
                "An error occurred. Please try again.",
                ephemeral=True
            )

class NoPrefixDurationView(discord.ui.View):
    def __init__(self, bot, owner, target_user):
        super().__init__(timeout=300)
        self.bot = bot
        self.owner = owner
        self.target_user = target_user
        
        # Add duration selector
        self.add_item(DurationSelect(bot, owner, target_user))

class DurationSelect(discord.ui.Select):
    def __init__(self, bot, owner, target_user):
        self.bot = bot
        self.owner = owner
        self.target_user = target_user
        self.logger = get_logger()
        
        options = [
            SelectOption(
                label="1 Hour",
                description="No-prefix access for 1 hour",
                value="1h",
                emoji="⏱️"
            ),
            SelectOption(
                label="6 Hours",
                description="No-prefix access for 6 hours",
                value="6h",
                emoji="⏱️"
            ),
            SelectOption(
                label="12 Hours",
                description="No-prefix access for 12 hours",
                value="12h",
                emoji="⏱️"
            ),
            SelectOption(
                label="1 Day",
                description="No-prefix access for 24 hours",
                value="24h",
                emoji="📅"
            ),
            SelectOption(
                label="1 Week",
                description="No-prefix access for 1 week",
                value="1w",
                emoji="📅"
            ),
            SelectOption(
                label="1 Month",
                description="No-prefix access for 1 month",
                value="1m",
                emoji="📅"
            ),
            SelectOption(
                label="Permanent",
                description="Permanent no-prefix access",
                value="permanent",
                emoji="♾️"
            )
        ]
        
        super().__init__(
            placeholder="Select duration...",
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            if interaction.user != self.owner:
                await interaction.response.send_message(
                    "You cannot use this panel",
                    ephemeral=True
                )
                return

            duration = self.values[0]
            expires_at = None
            duration_text = "permanently"
            
            # Calculate expiration time
            now = datetime.utcnow()
            
            if duration != "permanent":
                try:
                    if duration.endswith('h'):
                        hours = int(duration[:-1])
                        expires_at = now + timedelta(hours=hours)
                        duration_text = f"for {hours} hour{'s' if hours > 1 else ''}"
                    elif duration == "24h":
                        expires_at = now + timedelta(days=1)
                        duration_text = "for 1 day"
                    elif duration == "1w":
                        expires_at = now + timedelta(weeks=1)
                        duration_text = "for 1 week"
                    elif duration == "1m":
                        expires_at = now + timedelta(days=30)
                        duration_text = "for 1 month"
                except ValueError:
                    await interaction.response.send_message(
                        "Invalid duration format",
                        ephemeral=True
                    )
                    return

            try:
                # Update database
                await self.bot.db.noprefix_users.update_one(
                    {'_id': self.target_user.id},
                    {'$set': {
                        'added_by': self.owner.id,
                        'added_at': now.isoformat(),
                        'expires_at': expires_at.isoformat() if expires_at else None,
                        'duration': duration
                    }},
                    upsert=True
                )
                
                # Add audit log entry
                await self.bot.db.noprefix_audit.insert_one({
                    'timestamp': now.isoformat(),
                    'action': 'add',
                    'actor_id': self.owner.id,
                    'target_id': self.target_user.id,
                    'details': f"Duration: {duration_text}"
                })
                
                self.logger.info(
                    f"No-prefix added to {self.target_user} by {self.owner} with duration {duration_text}"
                )
                
            except Exception as e:
                self.logger.error(f"Database error in DurationSelect: {str(e)}")
                await interaction.response.send_message(
                    "An error occurred while updating the database. Please try again.",
                    ephemeral=True
                )
                return

            # Create confirmation embed
            embed = powered_embed("No-Prefix Access Granted")
            embed.description = f"{self.target_user.mention} has been given no-prefix access {duration_text}."
            
            if expires_at:
                embed.add_field(
                    name="Expires",
                    value=f"<t:{int(expires_at.timestamp())}:F> (<t:{int(expires_at.timestamp())}:R>)"
                )
            else:
                embed.add_field(name="Duration", value="♾️ Permanent")

            embed.add_field(
                name="Added By",
                value=self.owner.mention,
                inline=True
            )

            # Disable the select menu and update the message
            self.disabled = True
            await interaction.response.edit_message(embed=embed, view=self.view)

            # Send DM to target user
            try:
                dm_embed = powered_embed("No-Prefix Access Granted")
                dm_embed.description = f"You have been given no-prefix access in all servers with this bot {duration_text}."
                if expires_at:
                    dm_embed.add_field(
                        name="Expires",
                        value=f"<t:{int(expires_at.timestamp())}:F> (<t:{int(expires_at.timestamp())}:R>)"
                    )
                await self.target_user.send(embed=dm_embed)
            except discord.Forbidden:
                # If we can't DM the user, just ignore it
                pass

        except Exception as e:
            self.logger.error(f"Error in DurationSelect callback: {str(e)}")
            await interaction.response.send_message(
                "An error occurred while processing your request. Please try again.",
                ephemeral=True
            )

    @commands.hybrid_command(name="np_remove", description="Remove a user from no-prefix users.")
    @commands.has_permissions(administrator=True)
    async def np_remove(self, interaction: Interaction, user: Member):
        """Remove a user from the no-prefix users list."""
        await self.bot.db.noprefix_users.delete_one({'_id': user.id})
        await interaction.response.send_message(embed=powered_embed(f"{user.mention} has been removed from no-prefix users."))

    @commands.hybrid_command(name="np_list", description="List all no-prefix users.")
    @commands.has_permissions(administrator=True)
    async def np_list(self, interaction: Interaction):
        """List all users in the no-prefix users list."""
        users = await self.bot.db.noprefix_users.find().to_list(length=None)
        if not users:
            await interaction.response.send_message(embed=powered_embed("No users found in no-prefix list."))
            return

        user_mentions = [f"<@{user['_id']}>" for user in users]
        await interaction.response.send_message(embed=powered_embed("No-Prefix Users:\n" + "\n".join(user_mentions)))

async def setup(bot: commands.Bot):
    await bot.add_cog(NoPrefix(bot))