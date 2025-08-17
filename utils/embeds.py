from discord import Embed

def powered_embed(title: str, description: str = None, color: int = 0x00ff00) -> Embed:
    embed = Embed(title=title, description=description, color=color)
    embed.set_footer(text="Powered By SB Moderation™")
    return embed

def error_embed(title: str, description: str) -> Embed:
    return powered_embed(title, description, color=0xff0000)

def success_embed(title: str, description: str) -> Embed:
    return powered_embed(title, description, color=0x00ff00)

def info_embed(title: str, description: str) -> Embed:
    return powered_embed(title, description, color=0x0000ff)