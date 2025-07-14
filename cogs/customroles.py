# cogs/customroles.py

import discord
from discord.ext import commands
from discord.ui import View, Select

class RoleSelect(Select):
    def __init__(self, roles: list[discord.Role]):
        options = [discord.SelectOption(label=role.name, value=str(role.id)) for role in roles]
        super().__init__(
            placeholder="Choose your roles...",
            min_values=0,
            max_values=len(options),
            options=options
        )
        self.roles = roles

    async def callback(self, interaction: discord.Interaction):
        selected_ids = [int(role_id) for role_id in self.values]
        selected_roles = [role for role in self.roles if role.id in selected_ids]

        # Remove all roles from the list first
        for role in self.roles:
            if role in interaction.user.roles:
                await interaction.user.remove_roles(role)

        # Add selected roles
        await interaction.user.add_roles(*selected_roles)

        await interaction.response.send_message(
            content="✅ Your roles have been updated!",
            ephemeral=True
        )

class RoleView(View):
    def __init__(self, roles: list[discord.Role]):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))

class CustomRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="rolesetup")
    @commands.has_permissions(administrator=True)
    async def rolesetup(self, ctx, *, role_names):
        """
        Sends a custom role panel with given roles. Separate role names with commas.
        Example: &rolesetup Red, Blue, Gamer
        """
        role_names = [name.strip() for name in role_names.split(',')]
        guild_roles = ctx.guild.roles
        selected_roles = [role for role in guild_roles if role.name in role_names]

        if not selected_roles:
            await ctx.send("❌ No valid roles found. Make sure the roles exist.")
            return

        embed = discord.Embed(
            title="🎭 Choose Your Roles",
            description="Select roles from the menu below to get or remove them.",
            color=discord.Color.green()
        )

        await ctx.send(embed=embed, view=RoleView(selected_roles))

async def setup(bot):
    await bot.add_cog(CustomRoles(bot))
