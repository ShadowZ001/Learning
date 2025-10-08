import discord

def add_dravon_footer(embed, help_only=False):
    """Add Dravon footer to embed"""
    if help_only:
        embed.set_footer(text="Powered by Dravon™ • Use >help for commands")
    else:
        embed.set_footer(text="Powered by Dravon™ • Advanced Discord Bot")
    return embed

def create_error_embed(title, description):
    """Create error embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0xff0000
    )
    return add_dravon_footer(embed)

def create_success_embed(title, description):
    """Create success embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x00ff00
    )
    return add_dravon_footer(embed)