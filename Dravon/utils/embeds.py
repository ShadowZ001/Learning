import discord
from typing import Optional

def create_welcome_embed(title: str = "Welcome!", description: str = "Welcome to the server!", 
                        color: str = "#7289da", image_url: Optional[str] = None, 
                        thumbnail_url: Optional[str] = None, footer: Optional[str] = None,
                        member: Optional[discord.Member] = None) -> discord.Embed:
    """Create a welcome embed with customizable options"""
    
    # Replace placeholders if member is provided
    if member:
        title = title.replace("{user}", member.display_name).replace("{mention}", member.mention)
        description = description.replace("{user}", member.display_name).replace("{mention}", member.mention)
    
    # Convert hex color to int
    color_int = int(color.replace("#", ""), 16) if color.startswith("#") else int(color, 16)
    
    embed = discord.Embed(
        title=title,
        description=description,
        color=color_int
    )
    
    if image_url:
        embed.set_image(url=image_url)
    
    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)
    elif member:
        embed.set_thumbnail(url=member.display_avatar.url)
    
    if footer:
        embed.set_footer(text=footer)
    
    return embed

def create_setup_embed(preview_embed: discord.Embed) -> discord.Embed:
    """Create the setup embed with preview"""
    embed = discord.Embed(
        title="Welcome Setup",
        description="**Enhanced Setup Features:**\n\n**Channel Selection:**\n• Search channels by name\n• Browse all available channels\n• Paginated channel selection\n\n**Message Customization:**\n• Welcome message with variables\n• Custom embed title and footer\n• External message (outside embed)\n• Rich placeholder support\n\n**Visual Customization:**\n• Color selection (predefined & custom)\n• Thumbnail and image settings\n• Clean interface without emojis\n\n**Advanced Options:**\n• Toggle embed mode\n• User ping settings\n• DM welcome messages\n• Auto-delete timer\n• Live preview and testing\n\nUse the buttons below to configure each aspect of your welcome system.",
        color=0x7289da
    )
    return embed