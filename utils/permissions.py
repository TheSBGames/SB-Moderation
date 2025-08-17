from discord.ext import commands
from functools import wraps
from discord import PermissionOverwrite

def owner_only():
    def predicate(ctx):
        return ctx.author.id == 1186506712040099850
    return commands.check(predicate)

def has_permissions(**perms):
    def predicate(ctx):
        return all(getattr(ctx.author.guild_permissions, perm) for perm in perms)
    return commands.check(predicate)

def get_permission_overwrites(managers, default_role):
    overwrites = {
        default_role: PermissionOverwrite(read_messages=False),
    }
    for manager in managers:
        overwrites[manager] = PermissionOverwrite(read_messages=True, send_messages=True)
    return overwrites