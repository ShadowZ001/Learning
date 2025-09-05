import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class HelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="Select a category to view commands...",
        options=[
            discord.SelectOption(label="🛡️ Moderation", description="Moderation and punishment commands", value="moderation"),
            discord.SelectOption(label="🔒 Security", description="AntiNuke and security features", value="security"),
            discord.SelectOption(label="🎫 Tickets", description="Ticket system management", value="tickets"),
            discord.SelectOption(label="🎉 Giveaways", description="Giveaway creation and management", value="giveaways"),
            discord.SelectOption(label="⚙️ Server Setup", description="Welcome, leave, boost messages", value="setup"),
            discord.SelectOption(label="🤖 AutoMod", description="Automatic moderation features", value="automod"),
            discord.SelectOption(label="📊 Information", description="Server and bot information", value="info"),
            discord.SelectOption(label="🎨 Embed Builder", description="Custom embed creation", value="embeds"),
            discord.SelectOption(label="🎵 Music Player", description="Play music from YouTube, Spotify", value="music"),
            discord.SelectOption(label="🎮 Fun Commands", description="Kiss, slap, kill and other fun interactions", value="fun"),
            discord.SelectOption(label="🔧 Utility", description="Prefix, purge, and other utilities", value="utility")
        ]
    )
    async def help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "moderation":
            embed = discord.Embed(
                title="🛡️ Moderation Commands",
                description="Manage your server with powerful moderation tools",
                color=0xff6b6b
            )
            embed.add_field(
                name="Commands",
                value="`>ban <user> [reason]` - Ban a user\n`>unban <user>` - Unban a user\n`>kick <user> [reason]` - Kick a user\n`>mute <user> [time] [reason]` - Mute a user\n`>unmute <user>` - Unmute a user\n`>warn <user> [reason]` - Warn a user\n`>warnings <user>` - View user warnings\n`>purge <amount>` - Delete messages",
                inline=False
            )
        
        elif category == "security":
            embed = discord.Embed(
                title="🔒 Security Commands",
                description="Protect your server with AntiNuke v6.0",
                color=0x4ecdc4
            )
            embed.add_field(
                name="Commands",
                value="`>antinuke setup` - Configure AntiNuke protection\n`>antinuke config` - View current settings\n`>antinuke whitelist <user>` - Add extra owner\n`>antinuke logs <channel>` - Set logs channel\n`>antinuke enable <feature>` - Enable protection\n`>antinuke disable <feature>` - Disable protection",
                inline=False
            )
        
        elif category == "tickets":
            embed = discord.Embed(
                title="🎫 Ticket Commands",
                description="Complete ticket system with categories",
                color=0x45b7d1
            )
            embed.add_field(
                name="Commands",
                value="`>ticket setup` - Configure ticket system\n`>ticket config` - View ticket settings\n`>ticket logs <channel>` - Set ticket logs\n`>ticket add <user>` - Add user to ticket\n`>ticket close` - Close current ticket",
                inline=False
            )
        
        elif category == "giveaways":
            embed = discord.Embed(
                title="🎉 Giveaway Commands",
                description="Falcon-style giveaway system",
                color=0xf39c12
            )
            embed.add_field(
                name="Commands",
                value="`>giveaway create` - Create a new giveaway\n`>giveaway end <id>` - End giveaway early\n`>giveaway reroll <id>` - Reroll winners\n`>giveaway list` - View active giveaways\n`>giveaway pause <id>` - Pause/unpause giveaway\n`>giveaway delete <id>` - Delete giveaway",
                inline=False
            )
        
        elif category == "setup":
            embed = discord.Embed(
                title="⚙️ Server Setup Commands",
                description="Configure welcome, leave, and boost messages",
                color=0x9b59b6
            )
            embed.add_field(
                name="Commands",
                value="`>welcome setup` - Configure welcome messages\n`>leave setup` - Configure leave messages\n`>boost setup` - Configure boost messages\n`>autorole setup` - Configure auto roles\n`>logs setup` - Configure logging system",
                inline=False
            )
        
        elif category == "automod":
            embed = discord.Embed(
                title="🤖 AutoMod Commands",
                description="Automatic moderation and filtering",
                color=0xe74c3c
            )
            embed.add_field(
                name="Commands",
                value="`>automod setup` - Configure AutoMod\n`>automod config` - View AutoMod settings\n`>automod logs <channel>` - Set AutoMod logs\n`>automod enable <filter>` - Enable filter\n`>automod disable <filter>` - Disable filter\n`>autoresponder add` - Add auto response",
                inline=False
            )
        
        elif category == "info":
            embed = discord.Embed(
                title="📊 Information Commands",
                description="Get information about server and bot",
                color=0x3498db
            )
            embed.add_field(
                name="Commands",
                value="`>serverinfo` - Server information\n`>userinfo <user>` - User information\n`>botinfo` - Bot information and stats\n`>support` - Get support links\n`>stats` - Bot statistics\n`>ping` - Bot latency",
                inline=False
            )
        
        elif category == "embeds":
            embed = discord.Embed(
                title="🎨 Embed Builder Commands",
                description="Create custom embeds with variables",
                color=0x1abc9c
            )
            embed.add_field(
                name="Commands",
                value="`>embed setup` - Create custom embed\n`>embed list` - View saved embeds\n`>embed edit <name>` - Edit existing embed\n`>embed delete <name>` - Delete saved embed\n\n**Variables:** `{user}`, `{server}`, `{member_count}`, `{date}`",
                inline=False
            )
        
        elif category == "music":
            embed = discord.Embed(
                title="🎵 Music Player Commands",
                description="Play music from YouTube, Spotify, and SoundCloud",
                color=0xe91e63
            )
            embed.add_field(
                name="Commands",
                value="`>play <song/url>` - Play music or add to queue\n`>skip` - Skip current track\n`>stop` - Stop music and clear queue\n`>queue` - View current queue\n`>volume <1-100>` - Adjust volume\n\n**Features:** Interactive player, autoplay, shuffle, multi-platform support",
                inline=False
            )
        
        elif category == "fun":
            embed = discord.Embed(
                title="🎮 Fun Commands",
                description="Interactive fun commands with anime GIFs",
                color=0xff69b4
            )
            embed.add_field(
                name="Commands",
                value="`>kiss <user>` - Kiss someone with a cute anime GIF\n`>slap <user>` - Slap someone with an anime GIF\n`>kill <user>` - Playfully eliminate someone with a funny GIF\n\n**Features:** Random GIFs, different animations every time!",
                inline=False
            )
        
        elif category == "utility":
            embed = discord.Embed(
                title="🔧 Utility Commands",
                description="Helpful utility and configuration commands",
                color=0x95a5a6
            )
            embed.add_field(
                name="Commands",
                value="`>prefix set <prefix>` - Change bot prefix\n`>prefix reset` - Reset to default prefix\n`>purge <amount>` - Delete messages\n`>invite` - Get bot invite link\n`>avatar <user>` - Get user avatar",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        view = HelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help_command(self, ctx):
        """Display bot help with categories"""
        
        embed = discord.Embed(
            title="🌟 Dravon Help Center",
            description="**Your all-in-one Discord server management solution**\n\nDravon offers comprehensive server management with advanced features including moderation, security, tickets, giveaways, premium perks, and much more!\n\n**📂 Command Categories:**\n🛡️ **Moderation** - Ban, kick, mute, warn users\n🔒 **Security** - AntiNuke protection system\n🎫 **Tickets** - Complete ticket management\n🎉 **Giveaways** - Falcon-style giveaway system\n⚙️ **Server Setup** - Welcome, leave, boost messages\n🤖 **AutoMod** - Automatic moderation\n📊 **Information** - Server and bot stats\n🎨 **Embed Builder** - Custom embed creation\n🎵 **Music Player** - Play music from multiple platforms\n🎮 **Fun Commands** - Interactive anime GIF commands\n💎 **Premium** - Exclusive premium features\n🔧 **Utility** - Prefix, purge, and more\n\n*Select a category from the dropdown below to view detailed commands!*",
            color=0x7289da
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413146132405817487/f41e57df-936d-428a-8aa8-a0b4ca2a1e64.jpg?ex=68bade64&is=68b98ce4&hm=b47dca3ee7abd906adf59b9a6974c047a2ee5079928e6b3ba37255ea7b9945f7&")
        embed = add_dravon_footer(embed)
        
        view = HelpView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Help(bot))