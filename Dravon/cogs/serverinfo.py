import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class ServerInfoView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=300)
        self.guild = guild
    
    @discord.ui.button(label="Feature Info", style=discord.ButtonStyle.secondary)
    async def feature_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        features = self.guild.features
        
        embed = discord.Embed(
            title="**__Server Features__**",
            color=0x7289da
        )
        
        feature_list = [
            "Guild Onboarding Ever Enabled",
            "Age Verification Large Guild", 
            "Community",
            "Guild Onboarding Has Prompts",
            "News",
            "Soundboard",
            "Tierless Boosting",
            "Pin Permission Migration Complete",
            "Tierless Boosting System Message",
            "Guild Onboarding",
            "Auto Moderation",
            "Guild Server Guide"
        ]
        
        description = ""
        for feature in feature_list:
            feature_key = feature.upper().replace(" ", "_")
            has_feature = feature_key in features
            status = "✅" if has_feature else "❌"
            description += f"**{feature} :** {status}\n"
        
        embed.description = description
        
        view = ChannelInfoView(self.guild)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Role Info", style=discord.ButtonStyle.secondary)
    async def role_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        roles = sorted(self.guild.roles, key=lambda r: r.position, reverse=True)
        
        embed = discord.Embed(
            title="**__Server Roles__**",
            color=0x7289da
        )
        
        description = f"**Total Roles:** {len(roles)}\n\n"
        
        role_text = ""
        for role in roles:
            member_count = len(role.members)
            role_line = f"{role.mention} - {member_count} members\n"
            
            if len(description + role_text + role_line) > 4000:  # Discord embed limit
                break
            role_text += role_line
        
        description += role_text
        embed.description = description
        
        view = ChannelInfoView(self.guild)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="Channel Info", style=discord.ButtonStyle.secondary, row=1)
    async def channel_info_separate(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="**__Channels__**",
            color=0x7289da
        )
        
        text_channels = len([c for c in self.guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in self.guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len([c for c in self.guild.channels if isinstance(c, discord.CategoryChannel)])
        
        description = f"**Text Channels:** {text_channels}\n"
        description += f"**Voice Channels:** {voice_channels}\n"
        description += f"**Categories:** {categories}\n"
        description += f"**Total Channels:** {len(self.guild.channels)}"
        
        embed.description = description
        
        await interaction.response.edit_message(embed=embed, view=None)

class ChannelInfoView(discord.ui.View):
    def __init__(self, guild):
        super().__init__(timeout=300)
        self.guild = guild
    
    @discord.ui.button(label="Channel Info", style=discord.ButtonStyle.secondary)
    async def channel_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="**__Channels__**",
            color=0x7289da
        )
        
        text_channels = len([c for c in self.guild.channels if isinstance(c, discord.TextChannel)])
        voice_channels = len([c for c in self.guild.channels if isinstance(c, discord.VoiceChannel)])
        categories = len([c for c in self.guild.channels if isinstance(c, discord.CategoryChannel)])
        
        description = f"**Text Channels:** {text_channels}\n"
        description += f"**Voice Channels:** {voice_channels}\n"
        description += f"**Categories:** {categories}\n"
        description += f"**Total Channels:** {len(self.guild.channels)}"
        
        embed.description = description
        
        await interaction.response.edit_message(embed=embed, view=None)

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="serverinfo", aliases=["si"])
    async def server_info(self, ctx):
        guild = ctx.guild
        
        # Get verification level
        verification_levels = {
            discord.VerificationLevel.none: "None",
            discord.VerificationLevel.low: "Low",
            discord.VerificationLevel.medium: "Medium", 
            discord.VerificationLevel.high: "High",
            discord.VerificationLevel.highest: "Highest"
        }
        
        # Get notification settings
        notification_settings = {
            discord.NotificationLevel.all_messages: "All Messages",
            discord.NotificationLevel.only_mentions: "Only Mentions"
        }
        
        # Get content filter
        content_filters = {
            discord.ContentFilter.disabled: "Disabled",
            discord.ContentFilter.no_role: "No Role",
            discord.ContentFilter.all_members: "All Members"
        }
        
        embed = discord.Embed(
            title="**__About __**",
            color=0x7289da
        )
        
        description = f"**Name:** {guild.name}\n\n"
        description += f"**ID:** {guild.id}\n\n"
        description += f"**Owner:** {guild.owner.mention if guild.owner else 'Unknown'} (<@{guild.owner_id}>)\n\n"
        description += f"**Server Created:** <t:{int(guild.created_at.timestamp())}:F>\n\n"
        description += f"**Members:** {guild.member_count}\n\n"
        try:
            banned_count = len(await guild.bans().flatten()) if guild.me.guild_permissions.ban_members else 'No Permission'
        except:
            banned_count = 'Unable to fetch'
        description += f"**Banned:** {banned_count}\n\n"
        description += f"**Description:** {guild.description or 'No description'}\n\n\n"
        
        description += "**__Extra__**\n\n"
        description += f"**Verification Level:** {verification_levels.get(guild.verification_level, 'Unknown')}\n\n"
        description += f"**Upload Limit:** {guild.filesize_limit // 1024 // 1024} MB\n\n"
        description += f"**Inactive Timeout:** {guild.afk_timeout // 60} minutes\n\n"
        description += f"**System Message Channel:** {guild.system_channel.mention if guild.system_channel else 'None'}\n\n"
        description += f"**System Welcome Messages:** {'Enabled' if guild.system_channel_flags.join_notifications else 'Disabled'}\n\n"
        description += f"**System Boost Messages:** {'Enabled' if guild.system_channel_flags.premium_subscriptions else 'Disabled'}\n\n"
        description += f"**Default Notifications:** {notification_settings.get(guild.default_notifications, 'Unknown')}\n\n"
        description += f"**Explicit Media Content Filter:** {content_filters.get(guild.explicit_content_filter, 'Unknown')}\n\n"
        description += f"**2FA Requirements:** {'Enabled' if guild.mfa_level else 'Disabled'}"
        
        embed.description = description
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        view = ServerInfoView(guild)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(ServerInfo(bot))