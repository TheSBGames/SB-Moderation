import discord
from discord import Embed
from discord.ext import commands
from utils.embeds import powered_embed

class Utility(commands.Cog):
    @commands.hybrid_group(name="role", description="Role utility commands.")
    async def role(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: info, create, delete, edit, list, color, mention, audit, position, permissions, members, icon, hoisted, mentionable.")

    @role.group(name="permissions")
    async def role_permissions(self, ctx):
        """Manage role permissions."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: view, add, remove, list, reset, copy.")

    @role_permissions.command(name="view")
    async def perm_view(self, ctx, role: discord.Role):
        await ctx.send(f"Viewing permissions for {role.name}")

    @role_permissions.command(name="add")
    async def perm_add(self, ctx, role: discord.Role, permission: str):
        await ctx.send(f"Added {permission} to {role.name}")

    @role_permissions.command(name="remove")
    async def perm_remove(self, ctx, role: discord.Role, permission: str):
        await ctx.send(f"Removed {permission} from {role.name}")

    @role_permissions.command(name="list")
    async def perm_list(self, ctx, role: discord.Role):
        await ctx.send(f"Listing all permissions for {role.name}")

    @role_permissions.command(name="reset")
    async def perm_reset(self, ctx, role: discord.Role):
        await ctx.send(f"Reset permissions for {role.name}")

    @role_permissions.command(name="copy")
    async def perm_copy(self, ctx, source: discord.Role, target: discord.Role):
        await ctx.send(f"Copied permissions from {source.name} to {target.name}")

    @role.group(name="members")
    async def role_members(self, ctx):
        """Manage role members."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: list, add, remove, clear, mass_add, mass_remove, search.")

    @role_members.command(name="list")
    async def members_list(self, ctx, role: discord.Role):
        await ctx.send(f"Listing members with {role.name}")

    @role_members.command(name="add")
    async def members_add(self, ctx, role: discord.Role, member: discord.Member):
        await ctx.send(f"Added {member.name} to {role.name}")

    @role_members.command(name="remove")
    async def members_remove(self, ctx, role: discord.Role, member: discord.Member):
        await ctx.send(f"Removed {member.name} from {role.name}")

    @role_members.command(name="clear")
    async def members_clear(self, ctx, role: discord.Role):
        await ctx.send(f"Cleared all members from {role.name}")

    @role_members.command(name="mass_add")
    async def members_mass_add(self, ctx, role: discord.Role, condition: str):
        await ctx.send(f"Mass adding members to {role.name} based on {condition}")

    @role_members.command(name="mass_remove")
    async def members_mass_remove(self, ctx, role: discord.Role, condition: str):
        await ctx.send(f"Mass removing members from {role.name} based on {condition}")

    @role_members.command(name="search")
    async def members_search(self, ctx, role: discord.Role, query: str):
        await ctx.send(f"Searching for members in {role.name} matching {query}")

    @role.command(name="position")
    async def role_position(self, ctx, role: discord.Role, position: int):
        await ctx.send(f"Setting position of {role.name} to {position}")

    @role.command(name="icon")
    async def role_icon(self, ctx, role: discord.Role, url: str = None):
        await ctx.send(f"Setting icon for {role.name}")

    @role.command(name="hoisted")
    async def role_hoisted(self, ctx, role: discord.Role, hoisted: bool):
        await ctx.send(f"Setting hoisted status of {role.name} to {hoisted}")

    @role.command(name="mentionable")
    async def role_mentionable(self, ctx, role: discord.Role, mentionable: bool):
        await ctx.send(f"Setting mentionable status of {role.name} to {mentionable}")

    @role.command(name="info")
    async def role_info(self, ctx, role: discord.Role):
        await ctx.send(f"Role info for {role.name}: ID {role.id}, Color {role.color}, Members {len(role.members)}")

    @role.command(name="create")
    async def role_create(self, ctx, name: str, color: str = None):
        await ctx.send(f"Created role {name} with color {color} (implement logic)")

    @role.command(name="delete")
    async def role_delete(self, ctx, role: discord.Role):
        await ctx.send(f"Deleted role {role.name} (implement logic)")

    @role.command(name="edit")
    async def role_edit(self, ctx, role: discord.Role, field: str, value: str):
        await ctx.send(f"Edited role {role.name}: set {field} to {value} (implement logic)")

    @role.command(name="list")
    async def role_list(self, ctx):
        roles = ctx.guild.roles
        await ctx.send(f"Roles: {', '.join([r.name for r in roles])}")

    @role.command(name="color")
    async def role_color(self, ctx, role: discord.Role, color: str):
        await ctx.send(f"Set color of {role.name} to {color} (implement logic)")

    @role.command(name="mention")
    async def role_mention(self, ctx, role: discord.Role):
        await ctx.send(f"Role mention: {role.mention}")

    @role.command(name="audit")
    async def role_audit(self, ctx, role: discord.Role):
        await ctx.send(f"Audit log for role {role.name} (implement logic)")

    @commands.hybrid_group(name="emoji", description="Emoji utility commands.")
    async def emoji(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: info, create, delete, list, audit.")

    @emoji.command(name="info")
    async def emoji_info(self, ctx, emoji: discord.Emoji):
        await ctx.send(f"Emoji info: {emoji.name}, ID {emoji.id}, URL {emoji.url}")

    @emoji.command(name="create")
    async def emoji_create(self, ctx, name: str, url: str):
        await ctx.send(f"Created emoji {name} from {url} (implement logic)")

    @emoji.command(name="delete")
    async def emoji_delete(self, ctx, emoji: discord.Emoji):
        await ctx.send(f"Deleted emoji {emoji.name} (implement logic)")

    @emoji.command(name="list")
    async def emoji_list(self, ctx):
        emojis = ctx.guild.emojis
        await ctx.send(f"Emojis: {', '.join([e.name for e in emojis])}")

    @emoji.command(name="audit")
    async def emoji_audit(self, ctx, emoji: discord.Emoji):
        await ctx.send(f"Audit log for emoji {emoji.name} (implement logic)")

    @commands.hybrid_group(name="invite", description="Invite utility commands.")
    async def invite(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: info, create, delete, list, audit.")

    @invite.command(name="info")
    async def invite_info(self, ctx, invite: discord.Invite):
        await ctx.send(f"Invite info: {invite.code}, Uses {invite.uses}, Channel {invite.channel}")

    @invite.command(name="create")
    async def invite_create(self, ctx, channel: discord.TextChannel):
        await ctx.send(f"Created invite for {channel.mention} (implement logic)")

    @invite.command(name="delete")
    async def invite_delete(self, ctx, invite: discord.Invite):
        await ctx.send(f"Deleted invite {invite.code} (implement logic)")

    @invite.command(name="list")
    async def invite_list(self, ctx):
        invites = await ctx.guild.invites()
        await ctx.send(f"Invites: {', '.join([i.code for i in invites])}")

    @invite.command(name="audit")
    async def invite_audit(self, ctx, invite: discord.Invite):
        await ctx.send(f"Audit log for invite {invite.code} (implement logic)")

    @commands.hybrid_group(name="integration", description="Integration utility commands.")
    async def integration(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: info, list, audit.")

    @integration.command(name="info")
    async def integration_info(self, ctx, integration: discord.Integration):
        await ctx.send(f"Integration info: {integration.name}, ID {integration.id}")

    @integration.command(name="list")
    async def integration_list(self, ctx):
        integrations = await ctx.guild.integrations()
        await ctx.send(f"Integrations: {', '.join([i.name for i in integrations])}")

    @integration.command(name="audit")
    async def integration_audit(self, ctx, integration: discord.Integration):
        await ctx.send(f"Audit log for integration {integration.name} (implement logic)")
    @commands.hybrid_group(name="utility", description="Utility command group.")
    async def utility(self, ctx):
        """Utility command group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: avatar, serverinfo, userinfo, ping, meme, coinflip, 8ball, embed.")

    @utility.command(name="avatar")
    async def avatar(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        embed = powered_embed(f"Avatar for {user.display_name}")
        embed.set_image(url=user.avatar.url if user.avatar else user.default_avatar.url)
        await ctx.send(embed=embed)

    @utility.command(name="serverinfo")
    async def serverinfo(self, ctx):
        guild = ctx.guild
        embed = powered_embed(f"Server Info: {guild.name}")
        embed.add_field(name="Members", value=str(guild.member_count))
        embed.add_field(name="Owner", value=guild.owner.mention)
        await ctx.send(embed=embed)

    @utility.command(name="userinfo")
    async def userinfo(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        embed = powered_embed(f"User Info: {user.display_name}")
        embed.add_field(name="ID", value=str(user.id))
        embed.add_field(name="Joined", value=str(user.joined_at))
        await ctx.send(embed=embed)

    @utility.command(name="ping")
    async def ping(self, ctx):
        await ctx.send(embed=powered_embed(f"Pong! {round(self.bot.latency * 1000)}ms"))

    @utility.command(name="meme")
    async def meme(self, ctx):
        await ctx.send(embed=powered_embed("Here's a meme! (implement fetch logic)"))

    @utility.command(name="coinflip")
    async def coinflip(self, ctx):
        import random
        result = random.choice(["Heads", "Tails"])
        await ctx.send(embed=powered_embed(f"Coinflip: {result}"))

    @utility.command(name="8ball")
    async def eightball(self, ctx, *, question: str):
        import random
        responses = ["Yes", "No", "Maybe", "Ask again later", "Definitely", "Absolutely not"]
        await ctx.send(embed=powered_embed(f"Question: {question}\nAnswer: {random.choice(responses)}"))

    @utility.group(name="embed")
    async def embed(self, ctx):
        """Embed builder group."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a subcommand: create, color, title, description, send.")

    @embed.command(name="create")
    async def embed_create(self, ctx):
        await ctx.send(embed=powered_embed("Embed builder started. (implement modal logic)"))

    @embed.command(name="color")
    async def embed_color(self, ctx, color: str):
        await ctx.send(embed=powered_embed(f"Set embed color to {color}. (implement logic)"))

    @embed.command(name="title")
    async def embed_title(self, ctx, title: str):
        await ctx.send(embed=powered_embed(f"Set embed title to {title}. (implement logic)"))

    @embed.command(name="description")
    async def embed_description(self, ctx, description: str):
        await ctx.send(embed=powered_embed(f"Set embed description. (implement logic)"))

    @embed.command(name="send")
    async def embed_send(self, ctx):
        await ctx.send(embed=powered_embed("Embed sent. (implement logic)"))
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def ping(self, ctx: commands.Context):
        latency = round(self.bot.latency * 1000)  # Convert to milliseconds
        embed = Embed(title="Pong!", description=f"Latency: {latency}ms", color=0x00ff00)
        embed.set_footer(text="Powered By SB Moderation™")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="userinfo", description="Get information about a user.")
    async def userinfo(self, ctx: commands.Context, member: commands.MemberConverter = None):
        member = member or ctx.author
        embed = Embed(title=f"User Info for {member}", color=0x00ff00)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Name", value=str(member), inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=True)
        embed.set_footer(text="Powered By SB Moderation™")
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Utility(bot))