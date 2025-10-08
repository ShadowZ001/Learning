import discord

def create_welcome_embed(title="Welcome!", description="Welcome to the server!", color="#7289da", image_url=None, thumbnail_url=None, footer=None, member=None):
    """Create a welcome embed"""
    embed = discord.Embed(
        title=title,
        description=description,
        color=int(color.replace("#", ""), 16) if color.startswith("#") else 0x7289da
    )
    
    if member:
        embed.description = embed.description.replace("{user}", member.mention)
        embed.description = embed.description.replace("{username}", member.name)
        embed.description = embed.description.replace("{server}", member.guild.name)
    
    if image_url:
        embed.set_image(url=image_url)
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

def create_setup_embed(preview_embed):
    """Create setup embed"""
    embed = discord.Embed(
        title="Welcome Setup",
        description="Configure your welcome message settings",
        color=0x7289da
    )
    return embed