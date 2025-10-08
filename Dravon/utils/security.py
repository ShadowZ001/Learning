import discord

def has_security_access(guild, user):
    """Check if user has access to security commands (owner + extranovant only)"""
    return user.id == guild.owner_id or user.id == 1037768611126841405

def create_access_denied_embed(bot):
    """Create access denied embed for security commands"""
    embed = discord.Embed(
        title="❌ Access Restricted",
        description="You cannot use this command.\n\nOnly server owners and extranovant can access security features.",
        color=0x808080
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    return embed