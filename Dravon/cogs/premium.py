import discord
from discord.ext import commands
from datetime import datetime, timedelta
from utils.embed_utils import add_dravon_footer

class PremiumGrantView(discord.ui.View):
    def __init__(self, bot, target_user):
        super().__init__(timeout=300)
        self.bot = bot
        self.target_user = target_user
    
    @discord.ui.select(
        placeholder="Select Premium duration...",
        options=[
            discord.SelectOption(label="1 Day", description="Premium for 1 day", value="1"),
            discord.SelectOption(label="5 Days", description="Premium for 5 days", value="5"),
            discord.SelectOption(label="10 Days", description="Premium for 10 days", value="10"),
            discord.SelectOption(label="20 Days", description="Premium for 20 days", value="20"),
            discord.SelectOption(label="30 Days", description="Premium for 30 days", value="30"),
            discord.SelectOption(label="2 Months", description="Premium for 2 months", value="60"),
            discord.SelectOption(label="5 Months", description="Premium for 5 months", value="150"),
            discord.SelectOption(label="7 Months", description="Premium for 7 months", value="210"),
            discord.SelectOption(label="1 Year", description="Premium for 1 year", value="365"),
            discord.SelectOption(label="Lifetime", description="Lifetime Premium", value="lifetime")
        ]
    )
    async def duration_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        duration = select.values[0]
        
        if duration == "lifetime":
            expiry_date = None
            expiry_text = "Lifetime"
        else:
            days = int(duration)
            expiry_date = datetime.now() + timedelta(days=days)
            expiry_text = f"{days} days"
        
        # Grant premium to user
        await interaction.client.db.set_premium_user(self.target_user.id, expiry_date)
        
        embed = discord.Embed(
            title="✅ Premium Granted",
            description=f"Premium has been granted to {self.target_user.mention} for **{expiry_text}**!\n\nAll premium perks are now active for this user.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        
        await interaction.response.edit_message(embed=embed, view=None)

class Premium(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_admin_id = 1037768611126841405
    
    async def is_premium(self, user_id: int) -> bool:
        """Check if user has active premium"""
        premium_data = await self.bot.db.get_premium_user(user_id)
        if not premium_data:
            return False
        
        if premium_data.get("expiry") is None:  # Lifetime
            return True
        
        expiry = premium_data.get("expiry")
        if isinstance(expiry, str):
            expiry = datetime.fromisoformat(expiry)
        
        return datetime.now() < expiry
    
    @commands.hybrid_group(name="premium")
    async def premium_group(self, ctx):
        if ctx.invoked_subcommand is None:
            # Show premium perks
            embed = discord.Embed(
                title="✨ Premium Perks",
                description="Unlock the ultimate experience with Premium!\nHere's what you get when you go Premium:",
                color=0xffd700
            )
            
            perks = [
                "📩 **Direct DMs to Owner** – Get instant support",
                "⚡ **No Prefix Needed** – Use commands naturally",
                "🎶 **High-Quality Music Sound** – Crystal-clear audio",
                "🎧 **24/7 Voice Music** – Bot stays in VC nonstop",
                "🎟️ **Priority Support** – Faster responses to issues",
                "🛠️ **Early Access Features** – Try new features first",
                "🏆 **Premium Badge** – A badge next to your name in bot embeds"
            ]
            
            embed.add_field(
                name="Premium Benefits",
                value="\n".join(perks),
                inline=False
            )
            
            embed.set_footer(text="Upgrade today for the best experience 🚀")
            
            # Add Get Premium button
            view = discord.ui.View(timeout=None)
            premium_button = discord.ui.Button(
                label="Get Premium",
                style=discord.ButtonStyle.link,
                url="https://discord.gg/UKR78VcEtg",
                emoji="💎"
            )
            view.add_item(premium_button)
            
            await ctx.send(embed=embed, view=view)
    
    @premium_group.command(name="add")
    async def premium_add(self, ctx, user: discord.Member):
        """Grant premium to a user (Bot admin only)"""
        if ctx.author.id != self.bot_admin_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the bot administrator can grant premium access.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🔑 Grant Premium",
            description=f"Select the duration of Premium for {user.mention}.\nAfter selection, perks will be applied automatically.",
            color=0xffd700
        )
        embed = add_dravon_footer(embed)
        
        view = PremiumGrantView(self.bot, user)
        await ctx.send(embed=embed, view=view)
    
    @premium_group.command(name="show")
    async def premium_show(self, ctx, user: discord.Member = None):
        """Show premium status of a user"""
        if user is None:
            user = ctx.author
        
        premium_data = await self.bot.db.get_premium_user(user.id)
        is_premium_active = await self.is_premium(user.id)
        
        embed = discord.Embed(
            title=f"💎 Premium Status – {user.display_name}",
            color=0xffd700 if is_premium_active else 0x7289da
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        if is_premium_active:
            status = "✅ Premium Active"
            if premium_data and premium_data.get("expiry"):
                expiry = premium_data.get("expiry")
                if isinstance(expiry, str):
                    expiry = datetime.fromisoformat(expiry)
                days_left = (expiry - datetime.now()).days
                expiry_text = f"{days_left} Days Left"
            else:
                expiry_text = "Lifetime"
            
            perks = [
                "📩 Direct DMs to Owner",
                "⚡ No Prefix Needed",
                "🎶 High-Quality Music Sound",
                "🎧 24/7 Voice Music",
                "🎟️ Priority Support",
                "🛠️ Early Access Features",
                "🏆 Premium Badge"
            ]
            perks_text = "\n".join(perks)
        else:
            status = "❌ Not Premium"
            expiry_text = "N/A"
            perks_text = "No premium perks active"
        
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Expiry", value=expiry_text, inline=True)
        embed.add_field(name="Perks", value=perks_text, inline=False)
        
        embed.set_footer(text="Powered by Dravon™ Premium System")
        
        await ctx.send(embed=embed)
    
    @premium_group.command(name="remove")
    async def premium_remove(self, ctx, user: discord.Member):
        """Remove premium from a user (Bot admin only)"""
        if ctx.author.id != self.bot_admin_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the bot administrator can remove premium access.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        await self.bot.db.remove_premium_user(user.id)
        
        embed = discord.Embed(
            title="✅ Premium Removed",
            description=f"Premium has been removed from {user.mention}.\nAll premium perks have been revoked.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    @premium_group.command(name="mode")
    async def premium_mode(self, ctx, mode: str = None):
        """Toggle music mode for premium users (spotify/lavalink)"""
        if not await self.is_premium(ctx.author.id):
            embed = discord.Embed(
                title="❌ Premium Required",
                description="This feature is only available for premium users!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        if mode is None:
            # Show current mode
            current_mode = await self.bot.db.get_premium_music_mode(ctx.author.id)
            embed = discord.Embed(
                title="🎵 Premium Music Mode",
                description=f"**Current Mode:** {current_mode or 'lavalink'}\n\n**Available Modes:**\n🎶 `spotify` - High-quality Spotify streaming\n🎵 `lavalink` - Standard Lavalink streaming\n\n**Usage:** `>premium mode <spotify/lavalink>`",
                color=0xffd700
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        if mode.lower() not in ['spotify', 'lavalink']:
            embed = discord.Embed(
                title="❌ Invalid Mode",
                description="Please choose either `spotify` or `lavalink`",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        await self.bot.db.set_premium_music_mode(ctx.author.id, mode.lower())
        
        embed = discord.Embed(
            title="✅ Music Mode Updated",
            description=f"Your premium music mode has been set to **{mode.lower()}**!",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    async def add_premium_badge(self, embed: discord.Embed, user_id: int) -> discord.Embed:
        """Add premium badge to embed if user has premium"""
        if await self.is_premium(user_id):
            if embed.footer and embed.footer.text:
                embed.set_footer(text=f"🏆 Premium User • {embed.footer.text}")
            else:
                embed.set_footer(text="🏆 Premium User • Powered by Dravon™")
        return embed
    
    @premium_group.command(name="activate")
    async def premium_activate(self, ctx):
        """Activate premium guild (Premium users only)"""
        if not await self.is_premium(ctx.author.id):
            embed = discord.Embed(
                title="❌ Premium Required",
                description="Only premium users can activate premium guilds!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Check if guild is already premium
        guild_premium = await self.bot.db.get_premium_guild(ctx.guild.id)
        if guild_premium:
            embed = discord.Embed(
                title="⚠️ Already Activated",
                description="This server is already a premium guild!",
                color=0xffd700
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Get user's linked servers count
        user_guilds = await self.bot.db.get_user_premium_guilds(ctx.author.id)
        linked_count = len(user_guilds) if user_guilds else 0
        
        if linked_count >= 50:
            embed = discord.Embed(
                title="❌ Limit Reached",
                description="You have reached the maximum limit of 50 premium guilds!",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Activate premium guild
        await self.bot.db.set_premium_guild(ctx.guild.id, ctx.author.id)
        
        embed = discord.Embed(
            title="🌟 Premium Guild Activated!",
            description=f"✅ **{ctx.guild.name}** has been successfully activated as one of your premium guilds!\n\n🔹 **Linked by:** {ctx.author.mention}\n🔐 **Tier:** `Premium` | 🧩 **Linked Servers:** `{linked_count + 1}/50`\n\n✨ **What's Next?**\n• Access exclusive Dravon Premium features\n• Enhanced moderation, security, and support tools\n• Faster bot responses, new modules, and more!",
            color=0xffd700
        )
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    async def is_premium_guild(self, guild_id: int) -> bool:
        """Check if guild has premium activated"""
        guild_data = await self.bot.db.get_premium_guild(guild_id)
        if not guild_data:
            return False
        
        # Check if the user who activated it still has premium
        activator_id = guild_data.get("activator_id")
        if activator_id:
            return await self.is_premium(activator_id)
        
        return False
    
    async def get_music_mode(self, user_id: int) -> str:
        """Get premium user's music mode preference"""
        if not await self.is_premium(user_id):
            return "lavalink"  # Non-premium users only get lavalink
        
        mode = await self.bot.db.get_premium_music_mode(user_id)
        return mode or "lavalink"

async def setup(bot):
    await bot.add_cog(Premium(bot))