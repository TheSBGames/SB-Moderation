import discord
from discord.ext import commands
from discord import ui, ButtonStyle, SelectOption
from typing import Optional, Dict, Any
from utils.embeds import powered_embed

class ConfigurationPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db

    @commands.hybrid_group(name="config", description="Server configuration panel.")
    @commands.has_permissions(manage_guild=True)
    async def config(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.show_main_panel(ctx)

    async def show_main_panel(self, ctx):
        """Show main configuration panel."""
        embed = powered_embed("Server Configuration Panel")
        embed.description = "Select a module to configure:"
        
        view = MainConfigView(self.bot, ctx.author)
        await ctx.send(embed=embed, view=view)

    @config.command(name="save")
    async def config_save(self, ctx):
        """Save current configuration to a file."""
        config = await self.db.guild_settings.find_one({'_id': ctx.guild.id})
        if not config:
            await ctx.send(embed=powered_embed("No configuration found"))
            return
        
        import json
        config_str = json.dumps(config, indent=2)
        await ctx.send(
            embed=powered_embed("Current Configuration"),
            file=discord.File(
                fp=str.encode(config_str),
                filename=f"config_{ctx.guild.id}.json"
            )
        )

    @config.command(name="load")
    async def config_load(self, ctx):
        """Load configuration from a file."""
        if not ctx.message.attachments:
            await ctx.send(embed=powered_embed("Please attach a configuration file"))
            return
        
        try:
            import json
            config_str = await ctx.message.attachments[0].read()
            config = json.loads(config_str)
            await self.db.guild_settings.update_one(
                {'_id': ctx.guild.id},
                {'$set': config},
                upsert=True
            )
            await ctx.send(embed=powered_embed("Configuration loaded successfully"))
        except Exception as e:
            await ctx.send(embed=powered_embed(f"Error loading configuration: {str(e)}"))

class MainConfigView(ui.View):
    def __init__(self, bot, owner):
        super().__init__(timeout=300)
        self.bot = bot
        self.owner = owner
        
        # Add module selector
        self.add_item(ModuleSelect(bot, owner))

class ModuleSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
        options = [
            SelectOption(
                label="Moderation",
                description="Configure moderation settings",
                emoji="🛡️",
                value="mod"
            ),
            SelectOption(
                label="AutoMod",
                description="Configure auto-moderation settings",
                emoji="🤖",
                value="automod"
            ),
            SelectOption(
                label="Tickets",
                description="Configure ticket system",
                emoji="🎫",
                value="tickets"
            ),
            SelectOption(
                label="Leveling",
                description="Configure leveling system",
                emoji="📈",
                value="leveling"
            ),
            SelectOption(
                label="Music",
                description="Configure music system",
                emoji="🎵",
                value="music"
            ),
            SelectOption(
                label="ModMail",
                description="Configure ModMail system",
                emoji="📨",
                value="modmail"
            ),
            SelectOption(
                label="Utility",
                description="Configure utility features",
                emoji="🔧",
                value="utility"
            ),
            SelectOption(
                label="AutoRole",
                description="Configure auto-role system",
                emoji="👥",
                value="autorole"
            ),
            SelectOption(
                label="AutoResponder",
                description="Configure auto-responder system",
                emoji="💬",
                value="autorespond"
            )
        ]
        
        super().__init__(
            placeholder="Select a module to configure...",
            options=options,
            row=0
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        module = self.values[0]
        panel = self.get_panel_class(module)(self.bot, interaction.user)
        embed = powered_embed(f"{self.get_module_name(module)} Configuration")
        await interaction.response.edit_message(embed=embed, view=panel)

    def get_module_name(self, module):
        """Get friendly module name."""
        names = {
            "mod": "Moderation",
            "automod": "Auto-Moderation",
            "tickets": "Ticket System",
            "leveling": "Leveling System",
            "music": "Music System",
            "modmail": "ModMail System",
            "utility": "Utility Features",
            "autorole": "Auto-Role System",
            "autorespond": "Auto-Responder System"
        }
        return names.get(module, module)

    def get_panel_class(self, module):
        """Get the appropriate panel class."""
        panels = {
            "mod": ModeratorPanel,
            "automod": AutoModPanel,
            "tickets": TicketPanel,
            "leveling": LevelingPanel,
            "music": MusicPanel,
            "modmail": ModMailPanel,
            "utility": UtilityPanel,
            "autorole": AutoRolePanel,
            "autorespond": AutoResponderPanel
        }
        return panels.get(module, ModeratorPanel) # Default to ModeratorPanel

class BaseConfigPanel(ui.View):
    def __init__(self, bot, owner):
        super().__init__(timeout=300)
        self.bot = bot
        self.owner = owner
        self.add_item(ui.Button(label="Back", style=ButtonStyle.secondary, custom_id="back"))

    async def handle_back(self, interaction: discord.Interaction):
        """Handle back button press."""
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        main_view = MainConfigView(self.bot, self.owner)
        embed = powered_embed("Server Configuration Panel")
        embed.description = "Select a module to configure:"
        await interaction.response.edit_message(embed=embed, view=main_view)

class ModeratorPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(ModerationSettingsSelect(bot, owner))

class AutoModPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(AutoModSettingsSelect(bot, owner))

class ModerationSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
        options = [
            SelectOption(
                label="Punishment Settings",
                description="Configure warning and punishment settings",
                emoji="⚠️",
                value="punishments"
            ),
            SelectOption(
                label="Logging Settings",
                description="Configure moderation logging",
                emoji="📝",
                value="logging"
            ),
            SelectOption(
                label="Permission Settings",
                description="Configure moderation permissions",
                emoji="🔒",
                value="permissions"
            ),
            SelectOption(
                label="Appeal Settings",
                description="Configure punishment appeals",
                emoji="🔄",
                value="appeals"
            ),
            SelectOption(
                label="Notification Settings",
                description="Configure moderation notifications",
                emoji="🔔",
                value="notifications"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        if setting == "punishments":
            modal = PunishmentSettingsModal()
            await interaction.response.send_modal(modal)
        elif setting == "logging":
            modal = LoggingSettingsModal()
            await interaction.response.send_modal(modal)
        # ... other settings will be handled similarly

class AutoModSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
        options = [
            SelectOption(
                label="Filter Settings",
                description="Configure automod filters",
                emoji="🔍",
                value="filters"
            ),
            SelectOption(
                label="Action Settings",
                description="Configure automated actions",
                emoji="⚡",
                value="actions"
            ),
            SelectOption(
                label="Threshold Settings",
                description="Configure trigger thresholds",
                emoji="📊",
                value="thresholds"
            ),
            SelectOption(
                label="Whitelist Settings",
                description="Configure exemptions and whitelists",
                emoji="✅",
                value="whitelist"
            ),
            SelectOption(
                label="Logging Settings",
                description="Configure automod logging",
                emoji="📝",
                value="logging"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        if setting == "filters":
            modal = FilterSettingsModal()
            await interaction.response.send_modal(modal)
        elif setting == "actions":
            modal = ActionSettingsModal()
            await interaction.response.send_modal(modal)
        # ... other settings will be handled similarly

class TicketPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(TicketSettingsSelect(bot, owner))

class LevelingPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(LevelingSettingsSelect(bot, owner))

class MusicPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(MusicSettingsSelect(bot, owner))

class ModMailPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(ModMailSettingsSelect(bot, owner))

class UtilityPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(UtilitySettingsSelect(bot, owner))

class AutoRolePanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(AutoRoleSettingsSelect(bot, owner))

class AutoResponderPanel(BaseConfigPanel):
    def __init__(self, bot, owner):
        super().__init__(bot, owner)
        self.add_item(AutoResponderSettingsSelect(bot, owner))

class TicketSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        if setting == "categories":
            modal = TicketCategoryModal()
            await interaction.response.send_modal(modal)
        # Add other settings handlers
        
        options = [
            SelectOption(
                label="Category Settings",
                description="Configure ticket categories",
                emoji="📁",
                value="categories"
            ),
            SelectOption(
                label="Permission Settings",
                description="Configure ticket permissions",
                emoji="🔒",
                value="permissions"
            ),
            SelectOption(
                label="Template Settings",
                description="Configure ticket templates",
                emoji="📝",
                value="templates"
            ),
            SelectOption(
                label="Archive Settings",
                description="Configure ticket archival",
                emoji="📦",
                value="archive"
            ),
            SelectOption(
                label="Notification Settings",
                description="Configure ticket notifications",
                emoji="🔔",
                value="notifications"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class LevelingSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        if setting == "xp":
            modal = LevelingXPModal()
            await interaction.response.send_modal(modal)
        # Add other settings handlers
        
        options = [
            SelectOption(
                label="XP Settings",
                description="Configure XP gain settings",
                emoji="⭐",
                value="xp"
            ),
            SelectOption(
                label="Reward Settings",
                description="Configure level rewards",
                emoji="🎁",
                value="rewards"
            ),
            SelectOption(
                label="Role Settings",
                description="Configure level roles",
                emoji="👥",
                value="roles"
            ),
            SelectOption(
                label="Notification Settings",
                description="Configure level up notifications",
                emoji="🔔",
                value="notifications"
            ),
            SelectOption(
                label="Leaderboard Settings",
                description="Configure leaderboard display",
                emoji="🏆",
                value="leaderboard"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class MusicSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        modal = None
        
        if setting == "permissions":
            modal = MusicPermissionModal()
        elif setting == "sources":
            modal = MusicSourceModal()
        elif setting == "quality":
            modal = MusicQualityModal()
        elif setting == "playlists":
            modal = MusicPlaylistModal()
        elif setting == "restrictions":
            modal = MusicRestrictionModal()
        
        if modal:
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Settings for {setting} are coming soon!", ephemeral=True)
        
        options = [
            SelectOption(
                label="Permission Settings",
                description="Configure music permissions",
                emoji="🔒",
                value="permissions"
            ),
            SelectOption(
                label="Source Settings",
                description="Configure music sources",
                emoji="🔗",
                value="sources"
            ),
            SelectOption(
                label="Quality Settings",
                description="Configure audio quality",
                emoji="🎵",
                value="quality"
            ),
            SelectOption(
                label="Playlist Settings",
                description="Configure playlist features",
                emoji="📜",
                value="playlists"
            ),
            SelectOption(
                label="Restriction Settings",
                description="Configure music restrictions",
                emoji="⛔",
                value="restrictions"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class ModMailSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        modal = None
        
        if setting == "categories":
            modal = ModMailCategoryModal()
        elif setting == "permissions":
            modal = ModMailPermissionModal()
        elif setting == "templates":
            modal = ModMailTemplateModal()
        elif setting == "archive":
            modal = ModMailArchiveModal()
        elif setting == "notifications":
            modal = ModMailNotificationModal()
        
        if modal:
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Settings for {setting} are coming soon!", ephemeral=True)
        
        options = [
            SelectOption(
                label="Category Settings",
                description="Configure modmail categories",
                emoji="📁",
                value="categories"
            ),
            SelectOption(
                label="Permission Settings",
                description="Configure modmail permissions",
                emoji="🔒",
                value="permissions"
            ),
            SelectOption(
                label="Template Settings",
                description="Configure modmail templates",
                emoji="📝",
                value="templates"
            ),
            SelectOption(
                label="Archive Settings",
                description="Configure modmail archival",
                emoji="📦",
                value="archive"
            ),
            SelectOption(
                label="Notification Settings",
                description="Configure modmail notifications",
                emoji="🔔",
                value="notifications"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class UtilitySettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        modal = None
        
        if setting == "commands":
            modal = UtilityCommandsModal()
        elif setting == "permissions":
            modal = UtilityPermissionModal()
        elif setting == "restrictions":
            modal = UtilityRestrictionModal()
        elif setting == "logging":
            modal = UtilityLoggingModal()
        elif setting == "cooldowns":
            modal = UtilityCooldownModal()
        
        if modal:
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Settings for {setting} are coming soon!", ephemeral=True)
        
        options = [
            SelectOption(
                label="Command Settings",
                description="Configure utility commands",
                emoji="🔧",
                value="commands"
            ),
            SelectOption(
                label="Permission Settings",
                description="Configure command permissions",
                emoji="🔒",
                value="permissions"
            ),
            SelectOption(
                label="Restriction Settings",
                description="Configure command restrictions",
                emoji="⛔",
                value="restrictions"
            ),
            SelectOption(
                label="Logging Settings",
                description="Configure command logging",
                emoji="📝",
                value="logging"
            ),
            SelectOption(
                label="Cooldown Settings",
                description="Configure command cooldowns",
                emoji="⏱️",
                value="cooldowns"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class AutoRoleSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        modal = None
        
        if setting == "join":
            modal = AutoRoleJoinModal()
        elif setting == "bots":
            modal = AutoRoleBotModal()
        elif setting == "levels":
            modal = AutoRoleLevelModal()
        elif setting == "reactions":
            modal = AutoRoleReactionModal()
        elif setting == "conditions":
            modal = AutoRoleConditionModal()
        
        if modal:
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Settings for {setting} are coming soon!", ephemeral=True)
        
        options = [
            SelectOption(
                label="Join Role Settings",
                description="Configure roles on join",
                emoji="➡️",
                value="join"
            ),
            SelectOption(
                label="Bot Role Settings",
                description="Configure bot roles",
                emoji="🤖",
                value="bots"
            ),
            SelectOption(
                label="Level Role Settings",
                description="Configure level-based roles",
                emoji="📈",
                value="levels"
            ),
            SelectOption(
                label="Reaction Role Settings",
                description="Configure reaction roles",
                emoji="🎯",
                value="reactions"
            ),
            SelectOption(
                label="Condition Settings",
                description="Configure role conditions",
                emoji="⚙️",
                value="conditions"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class AutoResponderSettingsSelect(ui.Select):
    def __init__(self, bot, owner):
        self.bot = bot
        self.owner = owner
        
    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.owner:
            await interaction.response.send_message("You cannot use this panel", ephemeral=True)
            return

        setting = self.values[0]
        # Show appropriate modal for the selected setting
        modal = None
        
        if setting == "triggers":
            modal = AutoResponseTriggerModal()
        elif setting == "responses":
            modal = AutoResponseContentModal()
        elif setting == "variables":
            modal = AutoResponseVariableModal()
        elif setting == "scheduling":
            modal = AutoResponseScheduleModal()
        elif setting == "conditions":
            modal = AutoResponseConditionModal()
        
        if modal:
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(f"Settings for {setting} are coming soon!", ephemeral=True)
        
        options = [
            SelectOption(
                label="Trigger Settings",
                description="Configure auto-response triggers",
                emoji="🎯",
                value="triggers"
            ),
            SelectOption(
                label="Response Settings",
                description="Configure auto-responses",
                emoji="💬",
                value="responses"
            ),
            SelectOption(
                label="Variable Settings",
                description="Configure response variables",
                emoji="📝",
                value="variables"
            ),
            SelectOption(
                label="Schedule Settings",
                description="Configure response schedules",
                emoji="⏰",
                value="scheduling"
            ),
            SelectOption(
                label="Condition Settings",
                description="Configure response conditions",
                emoji="⚙️",
                value="conditions"
            )
        ]
        
        super().__init__(
            placeholder="Select a setting to configure...",
            options=options,
            row=1
        )

class PunishmentSettingsModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Punishment Settings")
        
        self.add_item(ui.TextInput(
            label="Warning Threshold",
            placeholder="Number of warnings before punishment",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Default Punishment",
            placeholder="mute/kick/ban",
            required=True,
            row=1
        ))
        # Add more settings as needed

    async def on_submit(self, interaction: discord.Interaction):
        # Save settings to database
        await interaction.response.send_message("Punishment settings updated!", ephemeral=True)

class LoggingSettingsModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Logging Settings")
        
        self.add_item(ui.TextInput(
            label="Log Channel",
            placeholder="Channel ID for logging",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Log Events",
            placeholder="warn,mute,kick,ban",
            required=True,
            row=1
        ))
        # Add more settings as needed

    async def on_submit(self, interaction: discord.Interaction):
        # Save settings to database
        await interaction.response.send_message("Logging settings updated!", ephemeral=True)

class FilterSettingsModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Filter Settings")
        
        self.add_item(ui.TextInput(
            label="Banned Words",
            placeholder="comma-separated list of words",
            required=False,
            row=0,
            style=discord.TextStyle.paragraph
        ))
        self.add_item(ui.TextInput(
            label="Regex Patterns",
            placeholder="one pattern per line",
            required=False,
            row=1,
            style=discord.TextStyle.paragraph
        ))
        # Add more settings as needed

    async def on_submit(self, interaction: discord.Interaction):
        # Save settings to database
        await interaction.response.send_message("Filter settings updated!", ephemeral=True)

class ActionSettingsModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Action Settings")
        
        self.add_item(ui.TextInput(
            label="First Offense",
            placeholder="warn/mute/kick/ban",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Repeat Offense",
            placeholder="warn/mute/kick/ban",
            required=True,
            row=1
        ))
        # Add more settings as needed

    async def on_submit(self, interaction: discord.Interaction):
        # Save settings to database
        await interaction.response.send_message("Action settings updated!", ephemeral=True)

# Additional modal classes
class AutoResponseTriggerModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Auto-Response Trigger Settings")
        self.add_item(ui.TextInput(
            label="Trigger Words",
            placeholder="Comma-separated list of trigger words",
            required=True,
            style=discord.TextStyle.paragraph,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Trigger Type",
            placeholder="exact/contains/regex",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Auto-response trigger settings updated!", ephemeral=True)

class AutoResponseContentModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Auto-Response Content Settings")
        self.add_item(ui.TextInput(
            label="Response Content",
            placeholder="The response message content",
            required=True,
            style=discord.TextStyle.paragraph,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Response Type",
            placeholder="text/embed/reaction",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Auto-response content settings updated!", ephemeral=True)

class AutoResponseVariableModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Auto-Response Variable Settings")
        self.add_item(ui.TextInput(
            label="Variable Name",
            placeholder="Name of the variable",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Variable Value",
            placeholder="Value or replacement text",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Auto-response variable settings updated!", ephemeral=True)

class AutoResponseScheduleModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Auto-Response Schedule Settings")
        self.add_item(ui.TextInput(
            label="Schedule Pattern",
            placeholder="Cron expression (e.g., */5 * * * *)",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Time Zone",
            placeholder="Time zone (e.g., UTC, America/New_York)",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Auto-response schedule settings updated!", ephemeral=True)

class AutoResponseConditionModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Auto-Response Condition Settings")
        self.add_item(ui.TextInput(
            label="Required Roles",
            placeholder="Comma-separated list of role IDs",
            required=False,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Channel Restrictions",
            placeholder="Comma-separated list of channel IDs",
            required=False,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Auto-response condition settings updated!", ephemeral=True)

# Add similar modals for all select menus
# For example:
class TicketCategoryModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Ticket Category Settings")
        self.add_item(ui.TextInput(
            label="Category Name",
            placeholder="Support/Feedback/Bug Report",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="Category Description",
            placeholder="Description of this ticket category",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("Ticket category settings updated!", ephemeral=True)

class LevelingXPModal(ui.Modal):
    def __init__(self):
        super().__init__(title="XP Settings")
        self.add_item(ui.TextInput(
            label="Base XP",
            placeholder="Base XP per message (default: 5)",
            required=True,
            row=0
        ))
        self.add_item(ui.TextInput(
            label="XP Cooldown",
            placeholder="Cooldown in seconds (default: 60)",
            required=True,
            row=1
        ))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("XP settings updated!", ephemeral=True)

# ... Add more modals for other settings ...

async def setup(bot):
    await bot.add_cog(ConfigurationPanel(bot))
