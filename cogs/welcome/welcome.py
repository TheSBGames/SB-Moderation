import discord
from discord.ext import commands
from discord import app_commands, Interaction, Member, SelectOption, TextChannel
from core.logger import get_logger
from utils.embeds import powered_embed
from typing import Optional, Dict, Any
import json
from .welcome_config import WelcomeConfigView, WelcomePreviewdiscord
from discord.ext import commands
from discord import app_commands, Interaction, SelectOption
from core.logger import get_logger
from utils.embeds import powered_embed
from typing import Optional
import json

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.logger = get_logger()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Handle member join events."""
        try:
            # Get welcome settings for the guild
            settings = await self.bot.db.welcome_settings.find_one({'_id': member.guild.id})
            if not settings:
                return

            # Get the welcome channel
            channel_id = settings.get('welcome_channel')
            if not channel_id:
                return

            channel = member.guild.get_channel(channel_id)
            if not channel:
                return

            # Get welcome message
            message = settings.get('welcome_message', 'Welcome {user} to {server}!')
            message = message.replace('{user}', member.mention)
            message = message.replace('{server}', member.guild.name)
            message = message.replace('{count}', str(member.guild.member_count))

            # Create and send welcome embed
            embed = powered_embed("Welcome!")
            embed.description = message
            embed.set_thumbnail(url=member.display_avatar.url)

            # Add member information
            embed.add_field(
                name="Account Created",
                value=f"<t:{int(member.created_at.timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="Member Count",
                value=str(member.guild.member_count),
                inline=True
            )

            # Send welcome message
            await channel.send(embed=embed)

            # Assign auto-role if enabled
            role_id = settings.get('autorole_id')
            if role_id:
                try:
                    role = member.guild.get_role(role_id)
                    if role:
                        await member.add_roles(role, reason="Welcome auto-role")
                except Exception as e:
                    self.logger.error(f"Failed to add auto-role: {str(e)}")

            self.logger.info(
                f"Welcomed {member} in {member.guild}",
                extra={
                    'guild_id': member.guild.id,
                    'user_id': member.id
                }
            )

        except Exception as e:
            self.logger.error(f"Error in welcome event: {str(e)}")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        """Handle member leave events."""
        try:
            # Get leave settings for the guild
            settings = await self.bot.db.welcome_settings.find_one({'_id': member.guild.id})
            if not settings:
                return

            # Get the leave channel
            channel_id = settings.get('leave_channel')
            if not channel_id:
                return

            channel = member.guild.get_channel(channel_id)
            if not channel:
                return

            # Get leave message
            message = settings.get('leave_message', 'Goodbye {user}! We now have {count} members.')
            message = message.replace('{user}', str(member))
            message = message.replace('{server}', member.guild.name)
            message = message.replace('{count}', str(member.guild.member_count))

            # Create and send leave embed
            embed = powered_embed("Member Left")
            embed.description = message
            embed.set_thumbnail(url=member.display_avatar.url)

            # Add member information
            embed.add_field(
                name="Joined Server",
                value=f"<t:{int(member.joined_at.timestamp())}:R>",
                inline=True
            )
            embed.add_field(
                name="Member Count",
                value=str(member.guild.member_count),
                inline=True
            )

            await channel.send(embed=embed)

            self.logger.info(
                f"Member {member} left {member.guild}",
                extra={
                    'guild_id': member.guild.id,
                    'user_id': member.id
                }
            )

        except Exception as e:
            self.logger.error(f"Error in leave event: {str(e)}")

    @commands.hybrid_group(name="welcome", description="Configure welcome and leave messages.")
    @commands.has_permissions(administrator=True)
    async def welcome(self, ctx):
        """Base welcome command that shows configuration UI."""
        if ctx.invoked_subcommand is None:
            view = WelcomeConfigView(self.bot)
            embed = powered_embed("Welcome System Configuration")
            embed.description = (
                "Use the buttons below to configure:\n"
                "• Welcome messages and embeds\n"
                "• Leave messages and embeds\n"
                "• Auto-role settings\n"
                "• Preview current settings\n"
                "\nAvailable variables:\n"
                "• {user} - Member mention\n"
                "• {username} - Member name\n"
                "• {server} - Server name\n"
                "• {count} - Member count\n"
                "• {user_tag} - Member's full tag\n"
                "• {time} - Join/Leave time"
            )
            await ctx.send(embed=embed, view=view)

    @welcome.command(name="channel", description="Set the welcome message channel")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: TextChannel):
        """Set the channel for welcome messages."""
        try:
            # Check bot permissions
            if not channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.send(f"I don't have permission to send messages in {channel.mention}!")
                return

            await self.bot.db.welcome_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {'welcome_channel': channel.id}},
                upsert=True
            )

            embed = powered_embed("Welcome Channel Set")
            embed.description = f"Welcome messages will now be sent to {channel.mention}"
            await ctx.send(embed=embed)

            # Send test message to verify permissions
            try:
                test_embed = powered_embed("Welcome Channel Test")
                test_embed.description = "This is a test message to verify bot permissions."
                await channel.send(embed=test_embed, delete_after=5)
            except discord.Forbidden:
                await ctx.send(f"Warning: Some permissions are missing in {channel.mention}. Messages may not send correctly.")

            self.logger.info(
                f"Welcome channel set to {channel} in {ctx.guild}",
                extra={
                    'guild_id': ctx.guild.id,
                    'channel_id': channel.id,
                    'permissions': str(channel.permissions_for(ctx.guild.me))
                }
            )

        except Exception as e:
            self.logger.error(f"Error setting welcome channel: {str(e)}")
            await ctx.send("An error occurred while setting the welcome channel.")

    @welcome.command(name="message", description="Set a custom welcome message.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, *, message: str):
        """Set a custom welcome message. Use {user}, {server}, and {count} as placeholders."""
        try:
            await self.bot.db.welcome_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {'welcome_message': message}},
                upsert=True
            )

            embed = powered_embed("Welcome Message Set")
            embed.description = "New welcome message set! Use `/welcome test` to preview it."
            embed.add_field(name="Message", value=message)
            await ctx.send(embed=embed)

            self.logger.info(
                f"Welcome message updated in {ctx.guild}",
                extra={'guild_id': ctx.guild.id}
            )

        except Exception as e:
            self.logger.error(f"Error setting welcome message: {str(e)}")
            await ctx.send("An error occurred while setting the welcome message.")

    @welcome.command(name="test", description="Test the welcome message.")
    @commands.has_permissions(administrator=True)
    async def test_welcome(self, ctx):
        """Test the welcome message with your own user."""
        try:
            settings = await self.bot.db.welcome_settings.find_one({'_id': ctx.guild.id})
            if not settings or 'welcome_channel' not in settings:
                await ctx.send("Welcome channel not set! Use `/welcome channel` first.")
                return

            # Simulate member join
            await self.on_member_join(ctx.author)
            await ctx.send("Test welcome message sent!")

        except Exception as e:
            self.logger.error(f"Error testing welcome message: {str(e)}")
            await ctx.send("An error occurred while testing the welcome message.")

    @welcome.command(name="autorole", description="Set auto-role for new members.")
    @commands.has_permissions(administrator=True)
    async def set_autorole(self, ctx, role: discord.Role):
        """Set a role to be automatically assigned to new members."""
        try:
            # Check bot permissions
            if not ctx.guild.me.guild_permissions.manage_roles:
                await ctx.send("I need the 'Manage Roles' permission to assign roles!")
                return

            # Check role hierarchy
            if role >= ctx.guild.me.top_role:
                await ctx.send("I cannot assign roles that are higher than or equal to my highest role!")
                return

            await self.bot.db.welcome_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {'autorole_id': role.id}},
                upsert=True
            )

            embed = powered_embed("Auto-Role Set")
            embed.description = f"New members will automatically receive the {role.mention} role."
            await ctx.send(embed=embed)

            self.logger.info(
                f"Auto-role set to {role} in {ctx.guild}",
                extra={
                    'guild_id': ctx.guild.id,
                    'role_id': role.id
                }
            )

        except Exception as e:
            self.logger.error(f"Error setting auto-role: {str(e)}")
            await ctx.send("An error occurred while setting the auto-role.")

    @commands.hybrid_group(name="leave", description="Configure leave messages and settings.")
    @commands.has_permissions(administrator=True)
    async def leave(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = powered_embed("Leave System Commands")
            embed.description = (
                "Available subcommands:\n"
                "• `/leave channel <channel>` - Set leave message channel\n"
                "• `/leave message <message>` - Set custom leave message\n"
                "• `/leave test` - Test leave message"
            )
            await ctx.send(embed=embed)

    @leave.command(name="channel", description="Set the leave message channel.")
    @commands.has_permissions(administrator=True)
    async def set_leave_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel for leave messages."""
        try:
            await self.bot.db.welcome_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {'leave_channel': channel.id}},
                upsert=True
            )

            embed = powered_embed("Leave Channel Set")
            embed.description = f"Leave messages will now be sent to {channel.mention}"
            await ctx.send(embed=embed)

            self.logger.info(
                f"Leave channel set to {channel} in {ctx.guild}",
                extra={
                    'guild_id': ctx.guild.id,
                    'channel_id': channel.id
                }
            )

        except Exception as e:
            self.logger.error(f"Error setting leave channel: {str(e)}")
            await ctx.send("An error occurred while setting the leave channel.")

    @leave.command(name="message", description="Set a custom leave message.")
    @commands.has_permissions(administrator=True)
    async def set_leave_message(self, ctx, *, message: str):
        """Set a custom leave message. Use {user}, {server}, and {count} as placeholders."""
        try:
            await self.bot.db.welcome_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': {'leave_message': message}},
                upsert=True
            )

            embed = powered_embed("Leave Message Set")
            embed.description = "New leave message set! Use `/leave test` to preview it."
            embed.add_field(name="Message", value=message)
            await ctx.send(embed=embed)

            self.logger.info(
                f"Leave message updated in {ctx.guild}",
                extra={'guild_id': ctx.guild.id}
            )

        except Exception as e:
            self.logger.error(f"Error setting leave message: {str(e)}")
            await ctx.send("An error occurred while setting the leave message.")

    @leave.command(name="test", description="Test the leave message.")
    @commands.has_permissions(administrator=True)
    async def test_leave(self, ctx):
        """Test the leave message with your own user."""
        try:
            settings = await self.bot.db.welcome_settings.find_one({'_id': ctx.guild.id})
            if not settings or 'leave_channel' not in settings:
                await ctx.send("Leave channel not set! Use `/leave channel` first.")
                return

            # Simulate member leave
            await self.on_member_remove(ctx.author)
            await ctx.send("Test leave message sent!")

        except Exception as e:
            self.logger.error(f"Error testing leave message: {str(e)}")
            await ctx.send("An error occurred while testing the leave message.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
