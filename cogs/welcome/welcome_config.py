import discord
from discord.ext import commands
from discord import app_commands, Interaction, SelectOption, TextStyle
from discord.ui import Modal, TextInput, View, Button, Select
from core.logger import get_logger
from utils.embeds import powered_embed
from typing import Optional, Dict, Any
import json

class WelcomeConfigModal(Modal):
    def __init__(self, title: str = "Welcome Message Configuration"):
        super().__init__(title=title)

        self.message = TextInput(
            label="Message Content",
            placeholder="Welcome {user} to {server}! You are member #{count}",
            style=TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.embed_title = TextInput(
            label="Embed Title",
            placeholder="🎉 Welcome to {server}!",
            required=True,
            max_length=256
        )

        self.embed_color = TextInput(
            label="Embed Color (Hex)",
            placeholder="Enter hex color code (e.g., #FF5733)",
            required=False,
            max_length=7
        )

        self.embed_footer = TextInput(
            label="Embed Footer",
            placeholder="Member #{count} | Joined {time}",
            required=False,
            max_length=2048
        )

        self.embed_thumbnail = TextInput(
            label="Embed Thumbnail URL",
            placeholder="Leave empty to use user's avatar",
            required=False
        )

        for item in [self.message, self.embed_title, self.embed_color, 
                    self.embed_footer, self.embed_thumbnail]:
            self.add_item(item)

class LeaveConfigModal(Modal):
    def __init__(self, title: str = "Leave Message Configuration"):
        super().__init__(title=title)

        self.message = TextInput(
            label="Message Content",
            placeholder="Goodbye {user}! We now have {count} members.",
            style=TextStyle.paragraph,
            required=True,
            max_length=2000
        )

        self.embed_title = TextInput(
            label="Embed Title",
            placeholder="👋 Member Left",
            required=True,
            max_length=256
        )

        self.embed_color = TextInput(
            label="Embed Color (Hex)",
            placeholder="Enter hex color code (e.g., #FF5733)",
            required=False,
            max_length=7
        )

        self.embed_footer = TextInput(
            label="Embed Footer",
            placeholder="Member count: {count}",
            required=False,
            max_length=2048
        )

        for item in [self.message, self.embed_title, self.embed_color, self.embed_footer]:
            self.add_item(item)

class ConfigSelect(Select):
    def __init__(self, placeholder: str, options: list):
        super().__init__(
            placeholder=placeholder,
            min_values=1,
            max_values=1,
            options=options
        )

class WelcomeConfigView(View):
    def __init__(self, bot, timeout=180):
        super().__init__(timeout=timeout)
        self.bot = bot
        self.logger = get_logger()

    @discord.ui.button(label="Configure Welcome", style=discord.ButtonStyle.primary)
    async def welcome_config(self, interaction: Interaction, button: Button):
        modal = WelcomeConfigModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Configure Leave", style=discord.ButtonStyle.primary)
    async def leave_config(self, interaction: Interaction, button: Button):
        modal = LeaveConfigModal()
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Preview Settings", style=discord.ButtonStyle.secondary)
    async def preview_settings(self, interaction: Interaction, button: Button):
        try:
            settings = await self.bot.db.welcome_settings.find_one({'_id': interaction.guild_id})
            if not settings:
                await interaction.response.send_message(
                    "No welcome/leave configuration found for this server.",
                    ephemeral=True
                )
                return

            embed = powered_embed("Welcome/Leave Configuration")
            
            # Welcome settings
            welcome_msg = settings.get('welcome_message', 'Not configured')
            welcome_channel = settings.get('welcome_channel', 'Not set')
            welcome_config = settings.get('welcome_config', {})
            
            embed.add_field(
                name="Welcome Settings",
                value=(
                    f"**Channel:** <#{welcome_channel}>\n"
                    f"**Message:** {welcome_msg[:100]}...\n"
                    f"**Embed Title:** {welcome_config.get('title', 'Default')}\n"
                    f"**Color:** {welcome_config.get('color', 'Default')}\n"
                    f"**Show Avatar:** {welcome_config.get('show_avatar', True)}"
                ),
                inline=False
            )
            
            # Leave settings
            leave_msg = settings.get('leave_message', 'Not configured')
            leave_channel = settings.get('leave_channel', 'Not set')
            leave_config = settings.get('leave_config', {})
            
            embed.add_field(
                name="Leave Settings",
                value=(
                    f"**Channel:** <#{leave_channel}>\n"
                    f"**Message:** {leave_msg[:100]}...\n"
                    f"**Embed Title:** {leave_config.get('title', 'Default')}\n"
                    f"**Color:** {leave_config.get('color', 'Default')}"
                ),
                inline=False
            )
            
            # Auto-role settings
            autorole_id = settings.get('autorole_id')
            if autorole_id:
                role = interaction.guild.get_role(autorole_id)
                embed.add_field(
                    name="Auto-Role",
                    value=f"Role: {role.mention if role else 'Invalid Role'}",
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            self.logger.error(f"Error in preview_settings: {str(e)}")
            await interaction.response.send_message(
                "An error occurred while loading settings.",
                ephemeral=True
            )

    @discord.ui.button(label="Reset Settings", style=discord.ButtonStyle.danger)
    async def reset_settings(self, interaction: Interaction, button: Button):
        try:
            # Add confirmation button
            confirm_view = View(timeout=60)
            
            async def confirm_callback(i: Interaction):
                if i.user != interaction.user:
                    await i.response.send_message("You cannot use this confirmation.", ephemeral=True)
                    return

                await self.bot.db.welcome_settings.delete_one({'_id': interaction.guild_id})
                await i.response.send_message("All welcome/leave settings have been reset.", ephemeral=True)
                self.logger.info(f"Welcome settings reset in guild {interaction.guild_id}")

            async def cancel_callback(i: Interaction):
                if i.user != interaction.user:
                    await i.response.send_message("You cannot use this confirmation.", ephemeral=True)
                    return

                await i.response.send_message("Reset cancelled.", ephemeral=True)

            confirm_view.add_item(Button(
                label="Confirm Reset",
                style=discord.ButtonStyle.danger,
                custom_id="confirm_reset"
            ))
            confirm_view.add_item(Button(
                label="Cancel",
                style=discord.ButtonStyle.secondary,
                custom_id="cancel_reset"
            ))

            confirm_view.children[0].callback = confirm_callback
            confirm_view.children[1].callback = cancel_callback

            await interaction.response.send_message(
                "Are you sure you want to reset all welcome/leave settings?",
                view=confirm_view,
                ephemeral=True
            )

        except Exception as e:
            self.logger.error(f"Error in reset_settings: {str(e)}")
            await interaction.response.send_message(
                "An error occurred while resetting settings.",
                ephemeral=True
            )

class WelcomePreview:
    @staticmethod
    def format_message(message: str, member: discord.Member, guild: discord.Guild) -> str:
        """Format welcome/leave message with variables."""
        return (message
                .replace("{user}", member.mention)
                .replace("{username}", member.name)
                .replace("{server}", guild.name)
                .replace("{count}", str(guild.member_count))
                .replace("{user_tag}", str(member))
                .replace("{time}", f"<t:{int(member.joined_at.timestamp())}:R>"))

    @staticmethod
    async def create_welcome_embed(member: discord.Member, config: Dict[str, Any]) -> discord.Embed:
        """Create a welcome embed based on configuration."""
        embed = powered_embed(
            config.get('embed_title', '🎉 Welcome!').format(
                user=member.name,
                server=member.guild.name,
                count=member.guild.member_count
            )
        )

        # Set color if provided
        if 'embed_color' in config:
            try:
                color = int(config['embed_color'].strip('#'), 16)
                embed.colour = discord.Colour(color)
            except ValueError:
                pass

        # Set thumbnail
        if config.get('embed_thumbnail'):
            embed.set_thumbnail(url=config['embed_thumbnail'])
        else:
            embed.set_thumbnail(url=member.display_avatar.url)

        # Add join date
        embed.add_field(
            name="Joined",
            value=f"<t:{int(member.joined_at.timestamp())}:F>",
            inline=True
        )

        # Add account age
        embed.add_field(
            name="Account Created",
            value=f"<t:{int(member.created_at.timestamp())}:R>",
            inline=True
        )

        # Add member count
        embed.add_field(
            name="Member Count",
            value=str(member.guild.member_count),
            inline=True
        )

        # Set footer if provided
        if 'embed_footer' in config:
            footer_text = config['embed_footer'].format(
                count=member.guild.member_count,
                time=f"<t:{int(member.joined_at.timestamp())}:R>"
            )
            embed.set_footer(text=footer_text)

        return embed

    @staticmethod
    async def create_leave_embed(member: discord.Member, config: Dict[str, Any]) -> discord.Embed:
        """Create a leave embed based on configuration."""
        embed = powered_embed(
            config.get('embed_title', '👋 Goodbye!').format(
                user=member.name,
                server=member.guild.name,
                count=member.guild.member_count
            )
        )

        # Set color if provided
        if 'embed_color' in config:
            try:
                color = int(config['embed_color'].strip('#'), 16)
                embed.colour = discord.Colour(color)
            except ValueError:
                pass

        embed.set_thumbnail(url=member.display_avatar.url)

        # Add time spent on server
        joined_at = member.joined_at
        if joined_at:
            embed.add_field(
                name="Time on Server",
                value=f"Joined <t:{int(joined_at.timestamp())}:R>",
                inline=True
            )

        # Add member count
        embed.add_field(
            name="Remaining Members",
            value=str(member.guild.member_count),
            inline=True
        )

        # Set footer if provided
        if 'embed_footer' in config:
            footer_text = config['embed_footer'].format(
                count=member.guild.member_count,
                time=f"<t:{int(member.joined_at.timestamp() if member.joined_at else 0)}:R>"
            )
            embed.set_footer(text=footer_text)

        return embed
