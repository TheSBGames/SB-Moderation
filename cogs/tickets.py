import discord
from discord.ext import commands
from discord.ui import View, Select
import asyncio
import json
import os

CATEGORY_FILE = "data/ticket_categories.json"

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Load or initialize category config
def load_categories():
    if not os.path.exists(CATEGORY_FILE):
        return {}
    with open(CATEGORY_FILE, "r") as f:
        return json.load(f)

def save_categories(data):
    with open(CATEGORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="General help from staff."),
            discord.SelectOption(label="Report", description="Report a user or issue."),
            discord.SelectOption(label="Appeal", description="Appeal a punishment."),
        ]
        super().__init__(placeholder="Choose your ticket type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        categories = load_categories()
        guild_id = str(interaction.guild.id)
        category_name = categories.get(guild_id, {}).get(ticket_type.lower(), f"{ticket_type} Tickets")

        # Find or create category
        category = discord.utils.get(interaction.guild.categories, name=category_name)
        if category is None:
            category = await interaction.guild.create_category(category_name)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True)
        }

        channel_name = f"{ticket_type.lower()}-{interaction.user.name}".replace(" ", "-")
        ticket_channel = await interaction.guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            category=category,
            topic=f"{ticket_type} ticket for {interaction.user.name}"
        )

        await ticket_channel.send(f"🎟️ Hello {interaction.user.mention}, please describe your issue.\nUse `&close` when done.")
        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ticketsetup")
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx, *, description: str = "Use the dropdown below to open a ticket."):
        """Send the ticket panel. You can customize the description."""
        embed = discord.Embed(
            title="🎫 Create a Ticket",
            description=description,
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed, view=TicketView())

    @commands.command(name="setticketcategory")
    @commands.has_permissions(administrator=True)
    async def setticketcategory(self, ctx, ticket_type: str, *, category_name: str):
        """Set the category for a ticket type. Usage: &setticketcategory support Support Tickets"""
        categories = load_categories()
        guild_id = str(ctx.guild.id)
        if guild_id not in categories:
            categories[guild_id] = {}

        categories[guild_id][ticket_type.lower()] = category_name
        save_categories(categories)
        await ctx.send(f"✅ Category for `{ticket_type}` tickets set to `{category_name}`.")

    @commands.command(name="close")
    async def close_ticket(self, ctx):
        """Close the ticket."""
        if any(x in ctx.channel.name for x in ["support", "report", "appeal"]):
            await ctx.send("❌ Closing ticket in 5 seconds...")
            await asyncio.sleep(5)
            await ctx.channel.delete()
        else:
            await ctx.send("⚠️ This
        
