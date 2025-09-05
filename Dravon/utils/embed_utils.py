import discord

def add_dravon_footer(embed: discord.Embed) -> discord.Embed:
    """Add 'Powered by Dravon™' footer to any embed"""
    current_footer = embed.footer.text if embed.footer else ""
    
    if current_footer:
        # If there's already a footer, add Dravon branding with separator
        embed.set_footer(text=f"{current_footer} • Powered by Dravon™")
    else:
        # If no footer, just add Dravon branding
        embed.set_footer(text="Powered by Dravon™")
    
    return embed

def create_embed(title: str = None, description: str = None, color: int = 0x7289da) -> discord.Embed:
    """Create an embed with Dravon branding automatically added"""
    embed = discord.Embed(title=title, description=description, color=color)
    return add_dravon_footer(embed)