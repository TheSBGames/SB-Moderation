import discord
from discord.ext import commands
import re

LINK_RE = re.compile(r'https?://\S+|www\.\S+')
INVITE_RE = re.compile(r'(discord\.gg|discordapp\.com/invite)/\S+')
BADWORD_RE = re.compile(r'\b(badword1|badword2)\b', re.IGNORECASE)

async def on_message_edit(before: discord.Message, after: discord.Message):
    if before.author.bot or before.content == after.content:
        return

    automod_settings = await after.guild.db.automod_settings.find_one({'_id': after.guild.id})
    if not automod_settings or not automod_settings.get('enabled', False):
        return

    if any(role.id in automod_settings.get('bypass_roles', []) for role in after.author.roles):
        return

    had_link = LINK_RE.search(before.content or '')
    has_link = LINK_RE.search(after.content or '')
    had_invite = INVITE_RE.search(before.content or '')
    has_invite = INVITE_RE.search(after.content or '')
    had_badword = BADWORD_RE.search(before.content or '')
    has_badword = BADWORD_RE.search(after.content or '')

    if (not had_link and has_link) or (not had_invite and has_invite) or (not had_badword and has_badword):
        await after.delete()
        punishment = automod_settings.get('action', {}).get('type', 'timeout')
        duration = automod_settings.get('action', {}).get('duration_minutes', 30)

        if punishment == 'timeout':
            await after.author.timeout(duration * 60)
            await after.author.send(f'You were punished for editing a message to contain a link or bad word.')
        
        log_channel_id = automod_settings.get('log_channel')
        if log_channel_id:
            log_channel = after.guild.get_channel(log_channel_id)
            if log_channel:
                embed = discord.Embed(title="Automod Action", color=discord.Color.red())
                embed.add_field(name="User", value=after.author.mention)
                embed.add_field(name="Action", value=f"{punishment.capitalize()} for editing a message.")
                embed.add_field(name="Before", value=before.content)
                embed.add_field(name="After", value=after.content)
                await log_channel.send(embed=embed)