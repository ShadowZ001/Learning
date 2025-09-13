import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer
import asyncio

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="Select a category to view commands...",
        options=[
            discord.SelectOption(label="Moderation", description="Moderation and punishment commands", value="moderation"),
            discord.SelectOption(label="Security", description="AntiNuke and security features", value="security"),
            discord.SelectOption(label="Tickets", description="Ticket system management", value="tickets"),
            discord.SelectOption(label="Giveaways", description="Giveaway creation and management", value="giveaways"),
            discord.SelectOption(label="Server Setup", description="Welcome, leave, boost messages", value="setup"),
            discord.SelectOption(label="AutoMod", description="Automatic moderation features", value="automod"),
            discord.SelectOption(label="Information", description="Server and bot information", value="info"),
            discord.SelectOption(label="Embed Builder", description="Custom embed creation", value="embeds"),
            discord.SelectOption(label="Music Player", description="Play music from YouTube, Spotify", value="music"),
            discord.SelectOption(label="Fun Commands", description="Kiss, slap, kill and other fun interactions", value="fun"),
            discord.SelectOption(label="Utility", description="Prefix, purge, and other utilities", value="utility"),
            discord.SelectOption(label="Invites", description="Invite tracking and management", value="invites"),
            discord.SelectOption(label="Basic Moderation", description="Kick, ban, mute commands", value="basic_mod"),
            discord.SelectOption(label="Media Filter", description="Media-only channel management", value="media")
        ]
    )
    async def help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "moderation":
            embed = discord.Embed(
                title="Moderation Commands",
                description="Manage your server with powerful moderation tools",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>ban <user> [reason]` - Ban a user\n`>unban <user>` - Unban a user\n`>kick <user> [reason]` - Kick a user\n`>mute <user> [time] [reason]` - Mute a user\n`>unmute <user>` - Unmute a user\n`>warn <user> [reason]` - Warn a user\n`>warnings <user>` - View user warnings\n`>purge <amount>` - Delete messages",
                inline=False
            )
        
        elif category == "security":
            embed = discord.Embed(
                title="Security Commands",
                description="Protect your server with AntiNuke v6.0",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>antinuke setup` - Configure AntiNuke protection\n`>antinuke config` - View current settings\n`>antinuke whitelist <user>` - Add extra owner\n`>antinuke logs <channel>` - Set logs channel\n`>antinuke enable <feature>` - Enable protection\n`>antinuke disable <feature>` - Disable protection",
                inline=False
            )
        
        elif category == "tickets":
            embed = discord.Embed(
                title="Ticket Commands",
                description="Complete ticket system with categories",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>ticket setup` - Configure ticket system\n`>ticket config` - View ticket settings\n`>ticket logs <channel>` - Set ticket logs\n`>ticket add <user>` - Add user to ticket\n`>ticket close` - Close current ticket",
                inline=False
            )
        
        elif category == "giveaways":
            embed = discord.Embed(
                title="Giveaway Commands",
                description="Falcon-style giveaway system",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>giveaway create` - Create a new giveaway\n`>giveaway end <id>` - End giveaway early\n`>giveaway reroll <id>` - Reroll winners\n`>giveaway list` - View active giveaways\n`>giveaway pause <id>` - Pause/unpause giveaway\n`>giveaway delete <id>` - Delete giveaway",
                inline=False
            )
        
        elif category == "setup":
            embed = discord.Embed(
                title="Server Setup Commands",
                description="Configure welcome, leave, and boost messages",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>welcome setup` - Configure welcome messages\n`>leave setup` - Configure leave messages\n`>boost setup` - Configure boost messages\n`>autorole setup` - Configure auto roles\n`>logs setup` - Configure logging system",
                inline=False
            )
        
        elif category == "automod":
            embed = discord.Embed(
                title="AutoMod Commands",
                description="Automatic moderation and filtering",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>automod setup` - Configure AutoMod\n`>automod config` - View AutoMod settings\n`>automod logs <channel>` - Set AutoMod logs\n`>automod enable <filter>` - Enable filter\n`>automod disable <filter>` - Disable filter\n`>autoresponder add` - Add auto response",
                inline=False
            )
        
        elif category == "info":
            embed = discord.Embed(
                title="Information Commands",
                description="Get information about server and bot",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>serverinfo` - Server information\n`>userinfo <user>` - User information\n`>botinfo` - Bot information and stats\n`>support` - Get support links\n`>stats` - Bot statistics\n`>ping` - Bot latency",
                inline=False
            )
        
        elif category == "embeds":
            embed = discord.Embed(
                title="Embed Builder Commands",
                description="Create custom embeds with variables",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>embed setup` - Create custom embed\n`>embed list` - View saved embeds\n`>embed edit <name>` - Edit existing embed\n`>embed delete <name>` - Delete saved embed\n\n**Variables:** `{user}`, `{server}`, `{member_count}`, `{date}`",
                inline=False
            )
        
        elif category == "music":
            embed = discord.Embed(
                title="Music Player Commands",
                description="Play music from YouTube, Spotify, and SoundCloud",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>play <song/url>` - Play music or add to queue\n`>skip` - Skip current track\n`>stop` - Stop music and clear queue\n`>disconnect` - Disconnect from voice\n`>247 enable/disable` - 24/7 mode (Premium)\n`>queue` - View current queue\n`>volume <1-100>` - Adjust volume\n`>musicpanel` or `>mp` - Music control panel\n`>voicepanel` or `>vp` - Voice control panel\n`>mhelp` - Detailed music help\n\n**Features:** Interactive player, autoplay, shuffle, 24/7 mode",
                inline=False
            )
        
        elif category == "fun":
            embed = discord.Embed(
                title="Fun Commands",
                description="Interactive fun commands with anime GIFs",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>kiss <user>` - Kiss someone with a cute anime GIF\n`>slap <user>` - Slap someone with an anime GIF\n`>kill <user>` - Playfully eliminate someone with a funny GIF\n`>hug <user>` - Give someone a warm hug\n\n**Features:** Random GIFs, different animations every time!",
                inline=False
            )
        
        elif category == "utility":
            embed = discord.Embed(
                title="Utility Commands",
                description="Helpful utility and configuration commands",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`>prefix set <prefix>` - Change bot prefix\n`>prefix reset` - Reset to default prefix\n`>purge <amount>` - Delete messages\n`>ping` - Bot latency and status\n`>uptime` - Bot uptime\n`>users` - Global bot stats\n`>invite` - Get bot invite link",
                inline=False
            )
        
        elif category == "invites":
            embed = discord.Embed(
                title="Invite Tracking Commands",
                description="Track and manage server invites",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`/invitesetup` - Configure invite logging\n`/invites <user>` - Check user invite stats\n`/inviteboard` - View invite leaderboard\n`/invites add <user> <amount>` - Add bonus invites\n`/invites remove <user> <amount>` - Remove invites\n`/invites clear <user>` - Reset user invites\n`/invites resetall` - Reset all server invites",
                inline=False
            )
        
        elif category == "basic_mod":
            embed = discord.Embed(
                title="Basic Moderation Commands",
                description="Essential moderation commands with DM notifications",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Commands",
                value="`/kick <user> [reason]` - Kick a member\n`/ban <user> [reason]` - Ban a member\n`/mute <user> <time> [reason]` - Mute a member\n`/tempmute <user> <time> [reason]` - Temporarily mute\n\n**Time Format:** 1h, 30m, 2d (hours, minutes, days)\n**Features:** Automatic DM notifications to users",
                inline=False
            )
        
        elif category == "media":
            embed = discord.Embed(
                title="Media Filter Commands",
                description="Manage media-only channels and bypass roles",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            embed.add_field(
                name="Channel Management",
                value="`>media channel add <channel>` - Add media-only channel\n`>media channel remove <channel>` - Remove media channel\n`>media channel list` - View all media channels\n`>media channel reset` - Clear all media channels",
                inline=False
            )
            embed.add_field(
                name="Bypass Management",
                value="`>media bypass add <role>` - Add bypass role\n`>media bypass remove <role>` - Remove bypass role\n`>media bypass list` - View all bypass roles\n`>media bypass reset` - Clear all bypass roles",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        view = HelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="help")
    async def help_command(self, ctx):
        """Display bot help with categories"""
        
        # Loading animation
        loading_embed = discord.Embed(
            title="⏳ Loading Help command...",
            description="Please wait while we prepare the help menu...",
            color=0x808080
        )
        loading_embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
        
        loading_msg = await ctx.send(embed=loading_embed)
        await asyncio.sleep(1)
        
        embed = discord.Embed(
            title="Dravon Help Center",
            description="**Your all-in-one Discord server management solution**\n\nSelect a category from the dropdown below to view commands!",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed = add_dravon_footer(embed)
        
        # Create main view with navigation and dropdown
        view = discord.ui.View(timeout=300)
        
        # Navigation buttons in first row
        back_btn = discord.ui.Button(
            emoji="⏪",
            style=discord.ButtonStyle.secondary,
            custom_id="help_back",
            row=0
        )
        
        forward_btn = discord.ui.Button(
            emoji="⏩",
            style=discord.ButtonStyle.secondary,
            custom_id="help_forward",
            row=0
        )
        
        delete_btn = discord.ui.Button(
            emoji="🗑️",
            style=discord.ButtonStyle.danger,
            custom_id="help_delete",
            row=0
        )
        
        view.add_item(back_btn)
        view.add_item(forward_btn)
        view.add_item(delete_btn)
        
        # Add the help dropdown
        help_view = HelpView(self.bot)
        view.add_item(help_view.children[0])  # Add the select menu
        
        # Add Invite and Support buttons in one row
        invite_btn = discord.ui.Button(
            label="Invite",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot",
            emoji="🔗"
        )
        
        support_btn = discord.ui.Button(
            label="Support",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/UKR78VcEtg",
            emoji="🛠️"
        )
        
        view.add_item(invite_btn)
        view.add_item(support_btn)
        
        await loading_msg.edit(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))