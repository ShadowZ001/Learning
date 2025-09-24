import discord
from discord.ext import commands

class HelpView(discord.ui.View):
    
    @discord.ui.select(
        placeholder="📋 Select a category to view commands...",
        options=[
            discord.SelectOption(label="🛡️ Moderation", description="Ban, kick, mute, warn, purge", value="moderation"),
            discord.SelectOption(label="🔒 Security", description="AntiNuke, AutoMod, AutoRule", value="security"),
            discord.SelectOption(label="🎵 Music & Fun", description="Music, games, memes, interactions", value="music_fun"),
            discord.SelectOption(label="🎫 Support Systems", description="Tickets, applications, giveaways", value="support"),
            discord.SelectOption(label="📊 Analytics", description="Stats, messages, invites, levels", value="analytics"),
            discord.SelectOption(label="🏠 Server Features", description="Welcome, boost, autorole, logs", value="server"),
            discord.SelectOption(label="👑 Administration", description="Admin tools, extra owners, badges", value="administration"),
            discord.SelectOption(label="🔧 Utilities", description="Info commands, ping, emoji, media", value="utilities"),
            discord.SelectOption(label="💎 Premium & Special", description="Premium features, YouTube, AI", value="premium_special"),
            discord.SelectOption(label="⚙️ Configuration", description="Prefix, embeds, verification", value="configuration"),
            discord.SelectOption(label="👥 User Management", description="Profiles, AFK, teams, users", value="user_management")
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
                value="`/ban <user> [reason]` - Ban a member\n`/kick <user> [reason]` - Kick a member\n`/mute <user> <time> [reason]` - Mute a member\n`/unmute <user>` - Unmute a member",
                inline=False
            )
            embed.add_field(
                name="Role Management",
                value="`/role add <user> <role>` - Add role to user\n`/role add humans <role>` - Add role to all humans\n`/role add bots <role>` - Add role to all bots\n`/role remove <user> <role>` - Remove role from user",
                inline=False
            )
            embed.add_field(
                name="Warning System",
                value="`/warn user <user> [reason]` - Warn a user\n`/warn clear <user>` - Clear user warnings\n`/warn list` - List warned users\n`/warn status` - View warning status\n`/warn config` - Configure warning system",
                inline=False
            )
            embed.add_field(
                name="Message Cleanup",
                value="`/purge <amount>` - Delete messages\n`/purge user <user> <amount>` - Delete user messages\n`/purge bots <amount>` - Delete bot messages",
                inline=False
            )
        
        elif category == "security":
            embed.title = "🔒 Security Commands"
            embed.description = "Advanced server protection and security systems"
            embed.add_field(
                name="AntiNuke System",
                value="`/antinuke setup` - Interactive setup wizard\n`/antinuke fastsetup` - Quick secure setup\n`/antinuke whitelist add <user>` - Add trusted user\n`/antinuke whitelist remove <user>` - Remove user\n`/antinuke whitelist list` - View whitelisted users\n`/antinuke logs <channel>` - Set logs channel\n`/antinuke config` - View configuration\n`/antinuke reset` - Reset all settings",
                inline=False
            )
            embed.add_field(
                name="AutoMod System",
                value="`/automod setup` - Configure auto moderation\n`/automod enable` - Enable all filters\n`/automod disable` - Disable AutoMod\n`/automod status` - View current settings",
                inline=False
            )
            embed.add_field(
                name="AutoRule System",
                value="`/autorule setup` - Configure automatic rules\n`/autorule enable` - Enable all rules\n`/autorule disable` - Disable AutoRule\n`/autorule status` - View rule status",
                inline=False
            )
        
        elif category == "music_fun":
            embed.title = "🎵 Music & Fun Commands"
            embed.description = "Entertainment and interactive features"
            embed.add_field(
                name="Music Player",
                value="`/play <song>` - Play music\n`/skip` - Skip current track\n`/stop` - Stop playback\n`/pause` - Pause music\n`/resume` - Resume music\n`/queue` - View queue\n`/volume <1-100>` - Adjust volume\n`/nowplaying` - Show current song",
                inline=False
            )
            embed.add_field(
                name="Music Panels",
                value="`/musicpanel` - Create music control panel\n`/voicepanel` - Create voice channel controls",
                inline=False
            )
            embed.add_field(
                name="Games & Fun",
                value="`/rps <user>` - Play Rock Paper Scissors\n`/meme` - Get random memes\n`/interactions` - User interaction commands\n• Kiss, hug, slap, and more interactions",
                inline=False
            )
        
        elif category == "support":
            embed.title = "🎫 Support Systems"
            embed.description = "Professional support and management tools"
            embed.add_field(
                name="Ticket System",
                value="`/ticket setup` - Configure ticket system\n`/ticket config` - View current settings\n`/ticket logs <channel>` - Set logs channel\n`/ticket add <user>` - Add user to ticket\n`/ticket close` - Close current ticket\n`/ticket reset` - Reset all configuration",
                inline=False
            )
            embed.add_field(
                name="Application System",
                value="`/apply setup` - Configure application system\n`/apply list` - View all configurations\n`/apply reset` - Reset specific or all settings\n`/apply status` - Check system readiness\n• Up to 20 custom questions\n• Automatic role assignment on acceptance",
                inline=False
            )
            embed.add_field(
                name="Giveaway System",
                value="`/giveaway create <prize> <duration> <winners> [channel]` - Start giveaway\n`/giveaway end <message_id>` - End giveaway early\n`/giveaway reroll <message_id>` - Reroll winners\n`/giveaway list` - List active giveaways\n`/giveaway pause <message_id>` - Pause giveaway\n`/giveaway resume <message_id>` - Resume giveaway",
                inline=False
            )
        
        elif category == "analytics":
            embed.title = "📊 Analytics Commands"
            embed.description = "Server statistics and tracking systems"
            embed.add_field(
                name="Message Tracking",
                value="`/message [user]` - Check message count\n`>messages [user]` or `>m [user]` - Check messages (prefix)\n• Shows all-time and daily message counts\n• Automatic message tracking",
                inline=False
            )
            embed.add_field(
                name="Leaderboards",
                value="`/leaderboard message` - Message leaderboard\n`>lb message` or `>lb m` - Message leaderboard (prefix)\n• Top message senders with navigation\n• 5 emoji navigation buttons",
                inline=False
            )
            embed.add_field(
                name="Invite Tracking",
                value="`/invites [user]` - Check user invites\n`/invites leaderboard` - Invite leaderboard\n`/invites add <user> <amount>` - Add bonus invites",
                inline=False
            )
            embed.add_field(
                name="Level System",
                value="`/level [user]` - Check level\n`/leaderboard xp` - XP leaderboard\n• Automatic XP gain from messages\n• Customizable level rewards",
                inline=False
            )
        
        elif category == "server":
            embed.title = "🏠 Server Features"
            embed.description = "Server enhancement and automation features"
            embed.add_field(
                name="Welcome System",
                value="`/welcome setup` - Setup welcome messages\n`/welcome test` - Test welcome message\n`/welcome reset` - Reset configuration\n`/welcome config` - View current settings\n• Custom welcome messages with variables\n• Image backgrounds and leave messages",
                inline=False
            )
            embed.add_field(
                name="Server Boost",
                value="`/boost setup` - Setup boost rewards\n`/boost role <role>` - Set boost role\n`/boost message` - Set boost message",
                inline=False
            )
            embed.add_field(
                name="Auto Features",
                value="`/autorole setup` - Setup auto roles\n`/autorole add <role>` - Add auto role\n`/autoresponder setup` - Auto responses\n`/logs setup` - Server logging system",
                inline=False
            )
        
        elif category == "administration":
            embed.title = "👑 Administration Commands"
            embed.description = "Server administration and management tools"
            embed.add_field(
                name="Extra Owner Management",
                value="`/extraowner set <user>` - Add extra owner\n`/extraowner remove <user>` - Remove extra owner\n`/extraowner list` - List extra owners\n• Extra owners bypass security systems\n• Server owner only commands",
                inline=False
            )
            embed.add_field(
                name="Bot Administration",
                value="• Bot admin commands (hidden from normal users)\n• Global announcements and premium management\n• Blacklist system and maintenance tools",
                inline=False
            )
            embed.add_field(
                name="Badge System",
                value="• User badge management (Bot Admin Only)\n• Custom badges for special users\n• Automatic badges for premium and bot owner",
                inline=False
            )
        
        elif category == "utilities":
            embed.title = "🔧 Utility Commands"
            embed.description = "Helpful tools and information commands"
            embed.add_field(
                name="Information Commands",
                value="`/serverinfo` or `>si` - Server details\n`/userinfo [user]` or `>ui [user]` - User information\n`/botinfo` or `>bi` - Bot statistics\n`/ping` - Bot latency\n`/uptime` - Bot uptime",
                inline=False
            )
            embed.add_field(
                name="Media & Display",
                value="`/avatar [user]` - Get user avatar\n`/banner [user]` - Get user banner\n`/emoji` - View all server emojis with navigation\n`/media` - Media commands",
                inline=False
            )
            embed.add_field(
                name="Voting",
                value="`/vote` - Vote for Dravon on Top.gg\n• Direct link to voting page\n• Automatic thank you DM\n• Help support bot development",
                inline=False
            )
        
        elif category == "premium_special":
            embed.title = "💎 Premium & Special Features"
            embed.description = "Premium features and special integrations"
            embed.add_field(
                name="Premium System",
                value="`/premium` - Check premium status\n`/premium activate` - Activate premium\n`/premium features` - View premium features\n• No-prefix commands\n• Enhanced music quality\n• Priority support",
                inline=False
            )
            embed.add_field(
                name="YouTube Notifications",
                value="`/youtube notify` - Setup YouTube notifications\n`/youtube status` - View current settings\n`/youtube reset` - Reset configuration\n• Real-time video notifications\n• Custom notification channels",
                inline=False
            )
            embed.add_field(
                name="AI Chat",
                value="`/ai setup` - Configure AI chat\n`/ai channel <channel>` - Set AI channel\n• Natural conversation in designated channels\n• Powered by advanced AI models",
                inline=False
            )
        
        elif category == "configuration":
            embed.title = "⚙️ Configuration Commands"
            embed.description = "Bot and server configuration tools"
            embed.add_field(
                name="Bot Configuration",
                value="`/prefix [prefix]` - Set or view bot prefix\n• Change bot prefix for your server\n• View current prefix settings",
                inline=False
            )
            embed.add_field(
                name="Embed System",
                value="`/embed setup` - Interactive embed builder\n`/embed list` - View saved embeds\n`/embed delete` - Delete saved embeds\n`/embed edit <name>` - Edit existing embed\n• Variable support ({user}, {server}, etc.)\n• Save and reuse embeds",
                inline=False
            )
            embed.add_field(
                name="Verification & Roles",
                value="`/verify setup` - Setup verification system\n`/reactionrole setup` - Create reaction roles\n• Automated role assignment\n• Member screening system",
                inline=False
            )
        
        elif category == "user_management":
            embed.title = "👥 User Management"
            embed.description = "User profiles, status, and team management"
            embed.add_field(
                name="User Profiles",
                value="`/profile [user]` - View user profile with badges\n• Custom bio system\n• Badge display (Crown, Premium, Member)\n• Commands used tracking\n• Premium status display",
                inline=False
            )
            embed.add_field(
                name="AFK System",
                value="`/afk [reason]` - Set AFK status\n• DM preference selection (DMs/No DMs)\n• Mention tracking while away\n• Duration tracking and welcome back messages\n• Shows all mentions when returning",
                inline=False
            )
            embed.add_field(
                name="Team Information",
                value="`/teams` - View bot team information\n• Meet the developers and staff\n• Interactive team member profiles\n• Learn about the people behind Dravon",
                inline=False
            )
            embed.add_field(
                name="User Tools",
                value="`/users` - User management tools\n• Various user-related utilities",
                inline=False
            )
        
        embed.set_footer(text="Dravon™ • Advanced Discord Server Management", icon_url=self.bot.user.display_avatar.url)
        view = HelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)
    
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        
        # Add buttons manually
        invite_btn = discord.ui.Button(
            label="🔗 Invite",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot",
            row=1
        )
        
        support_btn = discord.ui.Button(
            label="🛠️ Support",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/UKR78VcEtg",
            row=1
        )
        
        self.add_item(invite_btn)
        self.add_item(support_btn)

class HelpNew(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="help")
    async def help_command(self, ctx):
        """Display bot help with categories"""
        embed = discord.Embed(
            title="🤖 Dravon Bot - Help Center",
            description="**Welcome to Dravon!** Your all-in-one Discord server management solution.\n\n🛡️ **Advanced Security** - AntiNuke & AutoMod protection\n🎵 **Premium Music** - Multi-platform streaming\n🎫 **Support Systems** - Tickets, applications, giveaways\n📊 **Analytics** - Message tracking, levels, invites\n🏠 **Server Features** - Welcome, boost, autorole\n👑 **Administration** - Extra owners, badges, bot admin\n💎 **Premium Features** - YouTube, AI, no-prefix commands\n\n*Select a category from the dropdown below to explore commands!*",
            color=0x7289da
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Dravon™ • Advanced Discord Server Management", icon_url=self.bot.user.display_avatar.url)
        
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(HelpNew(bot))