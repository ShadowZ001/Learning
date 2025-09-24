import discord
from discord.ext import commands
from datetime import datetime

class EditBioModal(discord.ui.Modal, title="Edit Profile Bio"):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
    
    bio_input = discord.ui.TextInput(
        label="Your Bio",
        placeholder="Enter your bio (max 200 characters)...",
        style=discord.TextStyle.paragraph,
        max_length=200,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        bio = self.bio_input.value.strip() if self.bio_input.value else None
        await self.bot.db.set_user_bio(self.user_id, bio)
        
        embed = discord.Embed(
            title="✅ Bio Updated",
            description=f"Your bio has been {'updated' if bio else 'cleared'}!",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ProfileView(discord.ui.View):
    def __init__(self, bot, target_user, requester):
        super().__init__(timeout=300)
        self.bot = bot
        self.target_user = target_user
        self.requester = requester
    
    @discord.ui.button(label="✏️ Edit Profile", style=discord.ButtonStyle.primary)
    async def edit_profile(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.target_user.id:
            await interaction.response.send_message("❌ You can only edit your own profile!", ephemeral=True)
            return
        
        modal = EditBioModal(self.bot, self.target_user.id)
        await interaction.response.send_modal(modal)

class UserProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def get_user_badges(self, user):
        """Get user badges from database"""
        try:
            badges = await self.bot.db.get_user_badges(user.id)
            badge_emojis = []
            
            # Map badge names to emojis
            badge_map = {
                "premium": "💎",
                "developer": "🔧",
                "supporter": "❤️",
                "early_supporter": "⭐",
                "bug_hunter": "🐛",
                "moderator": "🛡️",
                "verified": "✅",
                "partner": "🤝",
                "staff": "👑"
            }
            
            for badge in badges:
                emoji = badge_map.get(badge.lower(), "🏷️")
                badge_emojis.append(emoji)
            
            return badge_emojis
        except Exception as e:
            print(f"Error getting user badges: {e}")
            return []
    
    @commands.hybrid_command(name="banner", aliases=["bn"])
    async def banner(self, ctx, user: discord.Member = None):
        """Get user's banner"""
        user = user or ctx.author
        
        # Fetch user to get banner
        try:
            fetched_user = await self.bot.fetch_user(user.id)
            if fetched_user.banner:
                embed = discord.Embed(
                    title=f"{user.display_name}'s Banner",
                    color=user.color or 0x7289da
                )
                embed.set_image(url=fetched_user.banner.url)
                embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
            else:
                embed = discord.Embed(
                    title="❌ No Banner",
                    description=f"{user.display_name} doesn't have a banner set.",
                    color=0xff0000
                )
        except:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to fetch user banner.",
                color=0xff0000
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="avatar", aliases=["av"])
    async def avatar(self, ctx, user: discord.Member = None):
        """Get user's avatar"""
        user = user or ctx.author
        
        embed = discord.Embed(
            title=f"{user.display_name}'s Avatar",
            color=user.color or 0x7289da
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="profile", aliases=["pr"])
    async def profile(self, ctx, user: discord.Member = None):
        """View user profile with badges and info"""
        user = user or ctx.author
        
        # Get user data
        try:
            bio = await self.bot.db.get_user_bio(user.id)
            commands_used = await self.bot.db.get_user_commands_used(user.id)
        except Exception as e:
            print(f"Database error in profile: {e}")
            bio = None
            commands_used = 0
        
        # Check premium status
        is_premium = False
        premium_expires = None
        try:
            premium_cog = self.bot.get_cog('Premium')
            if premium_cog:
                is_premium = await premium_cog.is_premium(user.id)
                if is_premium:
                    premium_data = await self.bot.db.get_premium_user(user.id)
                    if premium_data and premium_data.get('expiry'):
                        try:
                            premium_expires = datetime.fromisoformat(premium_data['expiry'])
                        except:
                            pass
        except:
            pass
        
        embed = discord.Embed(
            title=f"**{user.display_name} Profile**",
            description="Here's a custom overview of your server badges, subscriptions, and more.",
            color=user.color or 0x7289da
        )
        
        # Set user avatar as thumbnail
        embed.set_thumbnail(url=user.display_avatar.url)
        
        # Bio section
        embed.add_field(
            name="📝 Bio",
            value=bio if bio else "No bio set.",
            inline=False
        )
        
        # Server Badges section
        badges = []
        if is_premium:
            badges.append("💎 Premium")
        
        # Get user badges
        badges = await self.get_user_badges(user)
        
        embed.add_field(
            name="🏷 Server Badges",
            value=" ".join(badges) if badges else "📜 Member",
            inline=False
        )
        
        # Premium subscription info
        premium_status = "Subscription Active" if is_premium else "No active Subscription"
        embed.add_field(
            name="• 💎 Premium",
            value=premium_status,
            inline=True
        )
        
        # No-Prefix status (for premium users)
        noprefix_status = "Active" if is_premium else "Not Active"
        embed.add_field(
            name="🚫 No-Prefix",
            value=f"**Status:** {noprefix_status}",
            inline=True
        )
        
        # Premium expiry
        try:
            if is_premium and premium_expires:
                expire_text = f"<t:{int(premium_expires.timestamp())}:R>"
            else:
                expire_text = "N/A"
        except:
            expire_text = "N/A"
        
        embed.add_field(
            name="**Expires:**",
            value=expire_text,
            inline=True
        )
        
        # Commands used
        embed.add_field(
            name="⚙️ Commands Used",
            value=f"{commands_used:,} commands",
            inline=False
        )
        
        # Footer with requester info and timestamp
        current_time = datetime.now().strftime("%I:%M %p")
        embed.set_footer(
            text=f"Profile request by {ctx.author.display_name} | Today at {current_time}",
            icon_url=self.bot.user.display_avatar.url
        )
        
        # Add edit button if viewing own profile
        try:
            view = ProfileView(self.bot, user, ctx.author) if user.id == ctx.author.id else None
            await ctx.send(embed=embed, view=view)
        except Exception as e:
            print(f"Error sending profile: {e}")
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserProfile(bot))