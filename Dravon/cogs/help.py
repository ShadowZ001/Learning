import discord
from discord.ext import commands

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="📋 Select a category to view commands...",
        options=[
            discord.SelectOption(label="🛡️ Moderation", description="Ban, kick, mute, warn commands", value="moderation"),
            discord.SelectOption(label="🔒 Security", description="AntiNuke & AutoMod protection", value="security"),
            discord.SelectOption(label="🎵 Music", description="Play music from multiple sources", value="music"),
            discord.SelectOption(label="🎫 Tickets", description="Support ticket system", value="tickets"),
            discord.SelectOption(label="⚡ Reaction Roles", description="Emoji-based role assignment", value="reactions"),
            discord.SelectOption(label="🔐 Verification", description="Server verification system", value="verification"),
            discord.SelectOption(label="📝 Embeds", description="Custom embed creation", value="embeds"),
            discord.SelectOption(label="🎮 Fun", description="Memes and interaction commands", value="fun"),
            discord.SelectOption(label="🔧 Utility", description="Server info and helpful tools", value="utility"),
            discord.SelectOption(label="👑 Admin", description="Server administration tools", value="admin"),
            discord.SelectOption(label="🏠 Welcome", description="Welcome and leave messages", value="welcome"),
            discord.SelectOption(label="🎁 Giveaways", description="Giveaway management system", value="giveaways"),
            discord.SelectOption(label="📊 Stats", description="Server statistics and analytics", value="stats"),
            discord.SelectOption(label="💎 Premium", description="Premium features and benefits", value="premium"),
            discord.SelectOption(label="🔄 AutoMod", description="Advanced auto moderation", value="automod"),
            discord.SelectOption(label="📢 Logs", description="Server logging system", value="logs"),
            discord.SelectOption(label="🚀 Boost", description="Server boost rewards", value="boost"),
            discord.SelectOption(label="📱 Voice Panel", description="Voice channel management", value="voice"),
            discord.SelectOption(label="🎶 Music Panel", description="Music control panel", value="musicpanel"),
            discord.SelectOption(label="💤 AFK", description="AFK status system", value="afk"),
            discord.SelectOption(label="📨 Invites", description="Invite tracking system", value="invites"),
            discord.SelectOption(label="🎯 AutoRole", description="Automatic role assignment", value="autorole"),
            discord.SelectOption(label="⚙️ AutoRule", description="Automatic server rules", value="autorule"),
            discord.SelectOption(label="🏆 Teams", description="Team management system", value="teams"),
            discord.SelectOption(label="📈 Level Up", description="Leveling and XP system", value="levelup")
        ]
    )
    async def help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        embed = discord.Embed(color=0x7289da)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        if category == "moderation":
            embed.title = "🛡️ Moderation Commands"
            embed.description = "Keep your server safe with powerful moderation tools"
            embed.add_field(
                name="Basic Moderation",
                value="`/ban <user> [reason]` - Ban a member\n`/kick <user> [reason]` - Kick a member\n`/mute <user> <time> [reason]` - Mute a member\n`/purge <amount>` - Delete messages",
                inline=False
            )
            embed.add_field(
                name="Role Management",
                value="`/roleadd <user> <role>` - Add role to user\n`/roleremove <user> <role>` - Remove role from user",
                inline=False
            )
            embed.add_field(
                name="Warning System",
                value="`/warn <user> [reason]` - Warn a user\n`/warnclear <user>` - Clear user warnings\n`/warnlist` - List warned users\n`/warnconfig` - Configure warning system",
                inline=False
            )
        
        elif category == "security":
            embed.title = "🔒 Security Commands"
            embed.description = "Advanced server protection and security systems"
            embed.add_field(
                name="AntiNuke System",
                value="`/antinuke setup` - Configure protection\n`/antinuke fastsetup` - Quick setup\n`/antinuke whitelist` - Manage trusted users",
                inline=False
            )
            embed.add_field(
                name="AutoMod System",
                value="`/automod setup` - Configure auto moderation\n`/automod logs` - Set logging channel",
                inline=False
            )
        
        elif category == "music":
            embed.title = "🎵 Music Commands"
            embed.description = "High-quality music streaming from multiple platforms"
            embed.add_field(
                name="Playback Controls",
                value="`/play <song>` - Play music\n`/skip` - Skip current track\n`/stop` - Stop playback\n`/queue` - View queue",
                inline=False
            )
            embed.add_field(
                name="Premium Features",
                value="`/247 enable` - 24/7 mode\n`/node switch` - Change music source",
                inline=False
            )
        
        elif category == "tickets":
            embed.title = "🎫 Ticket Commands"
            embed.description = "Professional support ticket management system"
            embed.add_field(
                name="Ticket Management",
                value="`/ticket setup` - Configure tickets\n`/ticket close` - Close ticket\n`/ticket logs` - Set logs channel",
                inline=False
            )
        
        elif category == "reactions":
            embed.title = "⚡ Reaction Role Commands"
            embed.description = "Automated role assignment with emoji reactions"
            embed.add_field(
                name="Reaction Roles",
                value="`/reaction role setup` - Create reaction roles\n`/reaction role list` - View all setups\n`/reaction role reset` - Reset configuration",
                inline=False
            )
        
        elif category == "verification":
            embed.title = "🔐 Verification Commands"
            embed.description = "Server verification and member screening system"
            embed.add_field(
                name="Verification System",
                value="`/verify setup` - Configure verification\n`/verify reset` - Reset verification",
                inline=False
            )
        
        elif category == "embeds":
            embed.title = "📝 Embed Commands"
            embed.description = "Create beautiful custom embeds for your server"
            embed.add_field(
                name="Embed Management",
                value="`/embed setup` - Create custom embed\n`/embed list` - View saved embeds\n`/embed delete` - Delete embeds",
                inline=False
            )
        
        elif category == "fun":
            embed.title = "🎮 Fun Commands"
            embed.description = "Entertainment and interactive commands for your community"
            embed.add_field(
                name="Interactive Commands",
                value="`/meme` - Get random memes\n`/kiss <user>` - Kiss someone\n`/hug <user>` - Hug someone\n`/slap <user>` - Slap someone",
                inline=False
            )
        
        elif category == "utility":
            embed.title = "🔧 Utility Commands"
            embed.description = "Helpful tools and server information commands"
            embed.add_field(
                name="Information",
                value="`/serverinfo` - Server details\n`/userinfo` - User information\n`/botinfo` - Bot statistics\n`/ping` - Bot latency",
                inline=False
            )
            embed.add_field(
                name="User Tools",
                value="`/afk <reason>` - Set AFK status\n`/premium` - Check premium status",
                inline=False
            )
            embed.add_field(
                name="Profile System",
                value="`/avatar <user>` - Get user avatar\n`/banner <user>` - Get user banner\n`/profile <user>` - View user profile",
                inline=False
            )
        
        elif category == "admin":
            embed.title = "👑 Admin Commands"
            embed.description = "Server administration and management tools"
            embed.add_field(
                name="Server Management",
                value="`/extraowner set <user>` - Add extra owner\n`/extraowner remove <user>` - Remove extra owner\n`/extraowner list` - List extra owners",
                inline=False
            )
            embed.add_field(
                name="Configuration",
                value="`/prefix set <prefix>` - Change bot prefix\n`/botadmin add <user>` - Add bot admin\n`/botadmin remove <user>` - Remove bot admin",
                inline=False
            )
        
        elif category == "welcome":
            embed.title = "🏠 Welcome Commands"
            embed.description = "Welcome and leave message system"
            embed.add_field(
                name="Welcome System",
                value="`/welcome setup` - Setup welcome messages\n`/welcome test` - Test welcome message\n`/welcome reset` - Reset configuration\n`/welcome config` - View current settings",
                inline=False
            )
            embed.add_field(
                name="Leave System",
                value="`/leave setup` - Setup leave messages\n`/leave test` - Test leave message\n`/leave reset` - Reset leave config",
                inline=False
            )
        
        elif category == "giveaways":
            embed.title = "🎁 Giveaway Commands"
            embed.description = "Complete giveaway management system"
            embed.add_field(
                name="Giveaway Management",
                value="`/giveaway start` - Start a giveaway\n`/giveaway end` - End a giveaway\n`/giveaway reroll` - Reroll winners\n`/giveaway list` - List active giveaways",
                inline=False
            )
        
        elif category == "stats":
            embed.title = "📊 Stats Commands"
            embed.description = "Server statistics and analytics"
            embed.add_field(
                name="Statistics",
                value="`/stats server` - Server statistics\n`/stats user <user>` - User statistics\n`/stats bot` - Bot statistics",
                inline=False
            )
        
        elif category == "premium":
            embed.title = "💎 Premium Commands"
            embed.description = "Premium features and benefits"
            embed.add_field(
                name="Premium System",
                value="`/premium` - Check premium status\n`/premium activate` - Activate premium\n`/premium features` - View premium features",
                inline=False
            )
        
        elif category == "automod":
            embed.title = "🔄 AutoMod Commands"
            embed.description = "Advanced automatic moderation system"
            embed.add_field(
                name="AutoMod Setup",
                value="`/automod setup` - Configure automod\n`/automod logs <channel>` - Set logs channel\n`/automod toggle <rule>` - Toggle rules",
                inline=False
            )
        
        elif category == "logs":
            embed.title = "📢 Logs Commands"
            embed.description = "Server logging and monitoring system"
            embed.add_field(
                name="Logging System",
                value="`/logs setup` - Setup logging\n`/logs channel <type> <channel>` - Set log channels\n`/logs toggle <type>` - Toggle log types",
                inline=False
            )
        
        elif category == "boost":
            embed.title = "🚀 Boost Commands"
            embed.description = "Server boost rewards and management"
            embed.add_field(
                name="Boost System",
                value="`/boost setup` - Setup boost rewards\n`/boost role <role>` - Set boost role\n`/boost message` - Set boost message",
                inline=False
            )
        
        elif category == "voice":
            embed.title = "📱 Voice Panel Commands"
            embed.description = "Voice channel management and controls"
            embed.add_field(
                name="Voice Controls",
                value="`/voicepanel` - Create voice panel\n`/voice lock` - Lock voice channel\n`/voice unlock` - Unlock voice channel",
                inline=False
            )
        
        elif category == "musicpanel":
            embed.title = "🎶 Music Panel Commands"
            embed.description = "Interactive music control panel"
            embed.add_field(
                name="Music Panel",
                value="`/musicpanel` - Create music panel\n`/nowplaying` - Show current song\n`/queue panel` - Queue management panel",
                inline=False
            )
        
        elif category == "afk":
            embed.title = "💤 AFK Commands"
            embed.description = "Away from keyboard status system"
            embed.add_field(
                name="AFK System",
                value="`/afk <reason>` - Set AFK status\n`/afk global <reason>` - Set global AFK\n`/afk remove` - Remove AFK status",
                inline=False
            )
        
        elif category == "invites":
            embed.title = "📨 Invite Commands"
            embed.description = "Invite tracking and management system"
            embed.add_field(
                name="Invite Tracking",
                value="`/invites <user>` - Check user invites\n`/invites leaderboard` - Invite leaderboard\n`/invites add <user> <amount>` - Add bonus invites",
                inline=False
            )
        
        elif category == "autorole":
            embed.title = "🎯 AutoRole Commands"
            embed.description = "Automatic role assignment system"
            embed.add_field(
                name="AutoRole System",
                value="`/autorole setup` - Setup auto roles\n`/autorole add <role>` - Add auto role\n`/autorole remove <role>` - Remove auto role",
                inline=False
            )
        
        elif category == "autorule":
            embed.title = "⚙️ AutoRule Commands"
            embed.description = "Automatic server rules and enforcement"
            embed.add_field(
                name="AutoRule System",
                value="`/autorule setup` - Setup auto rules\n`/autorule add <rule>` - Add new rule\n`/autorule list` - List all rules",
                inline=False
            )
        
        elif category == "teams":
            embed.title = "🏆 Team Commands"
            embed.description = "Team management and organization system"
            embed.add_field(
                name="Team Management",
                value="`/team create <name>` - Create team\n`/team join <team>` - Join team\n`/team leave` - Leave current team",
                inline=False
            )
        
        elif category == "levelup":
            embed.title = "📈 Level Up Commands"
            embed.description = "Leveling and XP progression system"
            embed.add_field(
                name="Leveling System",
                value="`/level` - Check your level\n`/level <user>` - Check user level\n`/leaderboard` - View level leaderboard",
                inline=False
            )
        
        view = HelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)
    
    @discord.ui.button(label="🔗 Invite", style=discord.ButtonStyle.link, url="https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot", row=1)
    async def invite_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass
    
    @discord.ui.button(label="🛠️ Support", style=discord.ButtonStyle.link, url="https://discord.gg/UKR78VcEtg", row=1)
    async def support_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="help")
    async def help_command(self, ctx):
        """Display bot help with categories"""
        embed = discord.Embed(
            title="🤖 Dravon Bot - Help Center",
            description="**Welcome to Dravon!** Your all-in-one Discord server management solution.\n\n🛡️ **Advanced Security** - AntiNuke & AutoMod protection\n🎵 **Premium Music** - Multi-platform streaming\n⚡ **Reaction Roles** - Automated role management\n🔐 **Verification** - Member screening system\n\n*Select a category from the dropdown below to explore commands!*",
            color=0x7289da
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Dravon™ • Advanced Discord Server Management", icon_url=self.bot.user.display_avatar.url)
        
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))