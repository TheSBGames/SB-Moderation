import discord
from discord.ext import commands
from discord.ui import View, Select

class TicketSelect(Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Support", description="Get help from staff."),
            discord.SelectOption(label="Report", description="Report a user or issue."),
            discord.SelectOption(label="Appeal", description="Appeal a ban or mute.")
        ]
        super().__init__(placeholder="Choose your ticket type...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        ticket_type = self.values[0]
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True),
            interaction.guild.me: discord.PermissionOverwrite(view_channel=True)
        }
        ticket_channel = await interaction.guild.create_text_channel(
            name=f"{ticket_type.lower()}-ticket-{interaction.user.name}",
            overwrites=overwrites,
            topic=f"{ticket_type} ticket for {interaction.user.name}"
        )
        await ticket_channel.send(
            f"🎟️ Hello {interaction.user.mention}, staff will assist you shortly.\nType `&close` to close this ticket."
        )
        await interaction.response.send_message(
            f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True
        )

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self, ctx):
        """Send the ticket select menu."""
        embed = discord.Embed(
            title="🎫 Create a Ticket",
            description="Use the dropdown below to open a ticket.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=TicketView())

    @commands.command()
    async def close(self, ctx):
        """Close the current ticket channel."""
        if "ticket" in ctx.channel.name:
            await ctx.send("❌ Ticket will close in 5 seconds...")
            await discord.utils.sleep_until(discord.utils.utcnow() + discord.utils.timedelta(seconds=5))
            await ctx.channel.delete()
        else:
            await ctx.send("⚠️ This command can only be used in a ticket channel.")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
