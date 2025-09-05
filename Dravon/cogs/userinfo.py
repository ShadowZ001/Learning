import discord
from discord.ext import commands
from datetime import datetime
from utils.embed_utils import add_dravon_footer

class UserInfoView(discord.ui.View):
    def __init__(self, user, guild):
        super().__init__(timeout=300)
        self.user = user
        self.guild = guild
    
    @discord.ui.button(label="Avatar", style=discord.ButtonStyle.secondary, emoji="🖼️")
    async def avatar_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title=f"🖼️ {self.user.display_name}'s Avatar",
            color=self.user.color if hasattr(self.user, 'color') else 0x7289da
        )
        embed.set_image(url=self.user.display_avatar.url)
        embed = add_dravon_footer(embed)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Banner", style=discord.ButtonStyle.secondary, emoji="🎨")
    async def banner_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user = await interaction.client.fetch_user(self.user.id)
        
        if user.banner:
            embed = discord.Embed(
                title=f"🎨 {self.user.display_name}'s Banner",
                color=self.user.color if hasattr(self.user, 'color') else 0x7289da
            )
            embed.set_image(url=user.banner.url)
        else:
            embed = discord.Embed(
                title="❌ No Banner",
                description=f"{self.user.display_name} doesn't have a banner set.",
                color=0xff0000
            )
        
        embed = add_dravon_footer(embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="Roles", style=discord.ButtonStyle.secondary, emoji="🏷️")
    async def roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if hasattr(self.user, 'roles'):
            roles = [role.mention for role in reversed(self.user.roles[1:])]  # Exclude @everyone
            
            embed = discord.Embed(
                title=f"🏷️ {self.user.display_name}'s Roles",
                color=self.user.color
            )
            
            if roles:
                # Split roles into chunks to avoid embed limits
                role_chunks = [roles[i:i+20] for i in range(0, len(roles), 20)]
                for i, chunk in enumerate(role_chunks):
                    field_name = f"Roles ({len(roles)} total)" if i == 0 else f"Roles (continued)"
                    embed.add_field(
                        name=field_name,
                        value=" ".join(chunk),
                        inline=False
                    )
            else:
                embed.add_field(
                    name="Roles",
                    value="No roles assigned",
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="❌ No Role Information",
                description="Role information not available for this user.",
                color=0xff0000
            )
        
        embed = add_dravon_footer(embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def get_user_badges(self, user):
        """Get user badges as emoji strings"""
        badges = []
        
        if hasattr(user, 'public_flags'):
            flags = user.public_flags
            
            if flags.staff:
                badges.append("👑 Discord Staff")
            if flags.partner:
                badges.append("🤝 Discord Partner")
            if flags.hypesquad:
                badges.append("⚡ HypeSquad Events")
            if flags.bug_hunter:
                badges.append("🐛 Bug Hunter")
            if flags.hypesquad_bravery:
                badges.append("💜 HypeSquad Bravery")
            if flags.hypesquad_brilliance:
                badges.append("💙 HypeSquad Brilliance")
            if flags.hypesquad_balance:
                badges.append("💚 HypeSquad Balance")
            if flags.early_supporter:
                badges.append("⭐ Early Supporter")
            if flags.bug_hunter_level_2:
                badges.append("🐛 Bug Hunter Level 2")
            if flags.verified_bot_developer:
                badges.append("🔧 Verified Bot Developer")
            if flags.active_developer:
                badges.append("💻 Active Developer")
        
        return badges if badges else ["None"]
    
    def get_key_permissions(self, member):
        """Get key permissions for the member"""
        if not hasattr(member, 'guild_permissions'):
            return "N/A"
        
        perms = member.guild_permissions
        key_perms = []
        
        if perms.administrator:
            key_perms.append("Administrator")
        if perms.manage_guild:
            key_perms.append("Manage Server")
        if perms.manage_roles:
            key_perms.append("Manage Roles")
        if perms.manage_channels:
            key_perms.append("Manage Channels")
        if perms.manage_messages:
            key_perms.append("Manage Messages")
        if perms.kick_members:
            key_perms.append("Kick Members")
        if perms.ban_members:
            key_perms.append("Ban Members")
        if perms.moderate_members:
            key_perms.append("Timeout Members")
        
        return ", ".join(key_perms) if key_perms else "None"
    
    @commands.hybrid_command(name="userinfo", aliases=["ui"])
    async def userinfo(self, ctx, user: discord.Member = None):
        """Display detailed information about a user"""
        if user is None:
            user = ctx.author
        
        # Check if user has premium
        premium_cog = self.bot.get_cog('Premium')
        is_premium = False
        if premium_cog:
            is_premium = await premium_cog.is_premium(user.id)
        
        embed = discord.Embed(
            title=f"👤 User Information",
            color=0x000000
        )
        
        # Set user avatar as thumbnail
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # General Information
        general_info = f"**Name:** {user.name}\n"
        general_info += f"**ID:** {user.id}\n"
        general_info += f"**Nickname:** {user.nick if hasattr(user, 'nick') and user.nick else 'None'}\n"
        general_info += f"**Bot?:** {'Yes' if user.bot else 'No'}\n"
        
        badges = self.get_user_badges(user)
        general_info += f"**Badges:** {', '.join(badges)}\n"
        
        general_info += f"**Account Created:** <t:{int(user.created_at.timestamp())}:F>\n"
        
        if hasattr(user, 'joined_at') and user.joined_at:
            general_info += f"**Server Joined:** <t:{int(user.joined_at.timestamp())}:F>"
        else:
            general_info += f"**Server Joined:** N/A"
        
        embed.add_field(
            name="__General Information__",
            value=general_info,
            inline=False
        )
        
        # Role Info (only for guild members)
        if hasattr(user, 'roles'):
            role_info = f"**Highest Role:** {user.top_role.mention}\n"
            role_info += f"**Roles [{len(user.roles) - 1}]:** "
            
            if len(user.roles) > 1:
                roles = [role.mention for role in reversed(user.roles[1:])][:5]  # Show first 5 roles
                role_info += " ".join(roles)
                if len(user.roles) > 6:
                    role_info += f" and {len(user.roles) - 6} more..."
            else:
                role_info += "None"
            
            role_info += f"\n**Color:** {str(user.color)}"
            
            embed.add_field(
                name="__Role Info__",
                value=role_info,
                inline=False
            )
        
        # Extra Info
        extra_info = ""
        if hasattr(user, 'premium_since'):
            extra_info += f"**Boosting:** {'Yes' if user.premium_since else 'None'}\n"
        else:
            extra_info += f"**Boosting:** None\n"
        
        if hasattr(user, 'voice') and user.voice:
            extra_info += f"**Voice:** {user.voice.channel.mention}"
        else:
            extra_info += f"**Voice:** None"
        
        embed.add_field(
            name="__Extra__",
            value=extra_info,
            inline=False
        )
        
        # Key Permissions
        key_perms = self.get_key_permissions(user)
        embed.add_field(
            name="__Key Permissions__",
            value=key_perms,
            inline=False
        )
        
        # Acknowledgement
        acknowledgement = "Regular User"
        if hasattr(user, 'guild_permissions') and user.guild_permissions.administrator:
            acknowledgement = "Server Administrator"
        elif ctx.guild and user.id == ctx.guild.owner_id:
            acknowledgement = "Server Owner"
        elif user.bot:
            acknowledgement = "Bot"
        
        embed.add_field(
            name="__Acknowledgement__",
            value=acknowledgement,
            inline=False
        )
        
        # Add premium badge if user has premium
        if is_premium:
            if embed.footer and embed.footer.text:
                embed.set_footer(text=f"🏆 Premium User • {embed.footer.text}")
            else:
                embed.set_footer(text="🏆 Premium User • Powered by Dravon™")
        else:
            embed = add_dravon_footer(embed)
        
        view = UserInfoView(user, ctx.guild)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))