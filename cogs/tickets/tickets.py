    @commands.hybrid_group(name="ticket", description="Ticket command group.")
    async def ticket(self, ctx):
        """Ticket command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: panel, create, close, add, remove, list.")

    @ticket.group(name="panel")
    async def panel(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Panel subcommands: add, remove, edit, list, publish.")

    @panel.command(name="add")
    async def panel_add(self, ctx, panel_id: str, title: str):
        await ctx.send(f"Panel {panel_id} added with title {title} (implement logic)")

    @panel.command(name="remove")
    async def panel_remove(self, ctx, panel_id: str):
        await ctx.send(f"Panel {panel_id} removed (implement logic)")

    @panel.command(name="edit")
    async def panel_edit(self, ctx, panel_id: str, field: str, value: str):
        await ctx.send(f"Panel {panel_id} field {field} set to {value} (implement logic)")

    @panel.command(name="list")
    async def panel_list(self, ctx):
        await ctx.send("List of panels (implement logic)")

    @panel.command(name="publish")
    async def panel_publish(self, ctx, panel_id: str):
        await ctx.send(f"Panel {panel_id} published (implement logic)")

    @ticket.command(name="create")
    async def create(self, ctx, panel_id: str, category_id: int):
        await ctx.send(f"Ticket created in panel {panel_id} under category {category_id} (implement logic)")

    @ticket.command(name="close")
    async def close(self, ctx, ticket_id: str):
        await ctx.send(f"Ticket {ticket_id} closed (implement logic)")

    @ticket.command(name="add")
    async def add(self, ctx, ticket_id: str, user: discord.Member):
        await ctx.send(f"User {user.mention} added to ticket {ticket_id} (implement logic)")

    @ticket.command(name="remove")
    async def remove(self, ctx, ticket_id: str, user: discord.Member):
        await ctx.send(f"User {user.mention} removed from ticket {ticket_id} (implement logic)")

    @ticket.command(name="list")
    async def list_tickets(self, ctx):
        await ctx.send("List of open tickets (implement logic)")
from discord import app_commands, Interaction, Member, ButtonStyle, SelectOption
from discord.ext import commands
from discord.ui import View, Button, Select
from core.database import Database
from utils.embeds import powered_embed

class TicketSetupView(View):
    def __init__(self, bot, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.channel_id = channel_id

    @button(label="Create Ticket", style=ButtonStyle.primary)
    async def create_ticket(self, button: Button, interaction: Interaction):
        guild = interaction.guild
        ticket_channel = await guild.create_text_channel(f'ticket-{interaction.user.name}', category=None)
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket_channel.send(f'Ticket created by {interaction.user.mention}.')
        await interaction.response.send_message(f'Ticket created: {ticket_channel.mention}', ephemeral=True)

class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = Database()

    @app_commands.command(name="ticket_setup", description="Set up the ticket panel.")
    @commands.has_permissions(manage_guild=True)
    async def ticket_setup(self, interaction: Interaction):
        view = TicketSetupView(self.bot, interaction.channel_id)
        await interaction.response.send_message("Click the button below to create a ticket.", view=view)

    @app_commands.command(name="ticket_close", description="Close the current ticket.")
    async def ticket_close(self, interaction: Interaction):
        if interaction.channel.name.startswith('ticket-'):
            await interaction.channel.delete()
            await interaction.response.send_message("Ticket closed.", ephemeral=True)
        else:
            await interaction.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))