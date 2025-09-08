import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_utils import add_dravon_footer

class PremiumHelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="Select a premium category to view commands...",
        options=[
            discord.SelectOption(label="💎 Premium Features", description="Exclusive premium-only features", value="features"),
            discord.SelectOption(label="🎵 Premium Music", description="High-quality Spotify streaming", value="music"),
            discord.SelectOption(label="⚡ No-Prefix Commands", description="Use commands without prefix", value="noprefix"),
            discord.SelectOption(label="🏆 Premium Perks", description="All premium benefits", value="perks"),
            discord.SelectOption(label="🌟 VIP Commands", description="Exclusive VIP features", value="vip"),
            discord.SelectOption(label="🔐 Exclusive Access", description="Premium-only access features", value="exclusive")
        ]
    )
    async def premium_help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "features":
            embed = discord.Embed(
                title="💎 Premium Features",
                description="Exclusive features available only to premium users",
                color=0x808080
            )
            embed.add_field(
                name="Premium Commands",
                value="`premium` - View premium status and perks\n`premium mode <spotify/lavalink>` - Toggle music mode\n`premium activate` - Activate premium guild\n`vip` - Access VIP features\n`exclusive` - Premium exclusive commands",
                inline=False
            )
        
        elif category == "music":
            embed = discord.Embed(
                title="🎵 Premium Music",
                description="High-quality music streaming with Spotify integration",
                color=0x808080
            )
            embed.add_field(
                name="Premium Music Features",
                value="🎶 **Spotify Streaming** - Direct Spotify track playback\n🎧 **24/7 Voice Support** - Bot stays in voice channels\n🔊 **High-Quality Audio** - Crystal clear sound\n⚡ **No Cooldowns** - Instant command responses\n🎵 **Premium Playlists** - Access to exclusive playlists",
                inline=False
            )
        
        elif category == "noprefix":
            embed = discord.Embed(
                title="⚡ No-Prefix Commands",
                description="Use any command without typing the prefix",
                color=0x808080
            )
            embed.add_field(
                name="How It Works",
                value="Premium users can use **ANY** command without the `>` prefix!\n\n**Examples:**\n• `play music` instead of `>play music`\n• `serverinfo` instead of `>serverinfo`\n• `help` instead of `>help`\n\n**Supports both uppercase and lowercase letters!**",
                inline=False
            )
        
        elif category == "perks":
            embed = discord.Embed(
                title="🏆 Premium Perks",
                description="All the benefits you get with premium",
                color=0x808080
            )
            embed.add_field(
                name="Premium Benefits",
                value="📩 **Direct DMs to Owner** - Get instant support\n⚡ **No Prefix Needed** - Use commands naturally\n🎶 **Spotify Music** - High-quality streaming\n🎧 **24/7 Voice Music** - Continuous playback\n🎟️ **Priority Support** - Faster responses\n🛠️ **Early Access** - New features first\n🏆 **Premium Badge** - Special recognition\n🚀 **No Cooldowns** - Instant commands",
                inline=False
            )
        
        elif category == "vip":
            embed = discord.Embed(
                title="🌟 VIP Commands",
                description="Exclusive VIP features for premium users",
                color=0x808080
            )
            embed.add_field(
                name="VIP Features",
                value="`vip status` - Check your VIP status\n`vip perks` - View all VIP benefits\n`vip support` - Get priority support access\n`vip badge` - Display your premium badge",
                inline=False
            )
        
        elif category == "exclusive":
            embed = discord.Embed(
                title="🔐 Exclusive Access",
                description="Premium-only access and features",
                color=0x808080
            )
            embed.add_field(
                name="Exclusive Features",
                value="`exclusive features` - View exclusive features\n`exclusive music` - Access premium music modes\n`exclusive support` - Get exclusive support\n`exclusive beta` - Access beta features",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        view = PremiumHelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class PremiumHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="premiumhelp")
    async def premium_help(self, ctx):
        """Premium help command with categories"""
        
        # Check if user is premium
        premium_cog = self.bot.get_cog('Premium')
        if premium_cog:
            is_premium = await premium_cog.is_premium(ctx.author.id)
            if not is_premium:
                embed = discord.Embed(
                    title="❌ Premium Required",
                    description="This help section is only available for premium users!\n\nUpgrade to premium to access exclusive features and this detailed help system.",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await ctx.send(embed=embed)
                return
        
        embed = discord.Embed(
            title="💎 Premium Help Center",
            description="**Exclusive help for premium users**\n\nWelcome to the premium help center! Here you'll find detailed information about all your exclusive premium features and benefits.\n\n**Premium Categories:**\n💎 **Premium Features** - Exclusive premium-only commands\n🎵 **Premium Music** - High-quality Spotify streaming\n⚡ **No-Prefix Commands** - Use commands without prefix\n🏆 **Premium Perks** - All your premium benefits\n🌟 **VIP Commands** - Exclusive VIP features\n🔐 **Exclusive Access** - Premium-only access\n\n*Select a category from the dropdown below for detailed information!*",
            color=0x808080
        )
        
        embed.set_thumbnail(url=ctx.bot.user.display_avatar.url)
        embed = add_dravon_footer(embed)
        
        view = PremiumHelpView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(PremiumHelp(bot))