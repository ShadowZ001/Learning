import discord
from discord.ext import commands
from datetime import datetime, timedelta
import time

class BotInfoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
        # Add invite button
        invite_button = discord.ui.Button(
            label="Invite Me",
            style=discord.ButtonStyle.link,
            url="https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot",
            emoji="🔗"
        )
        self.add_item(invite_button)
        
        # Add support button
        support_button = discord.ui.Button(
            label="Support Server",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/UKR78VcEtg",
            emoji="💬"
        )
        self.add_item(support_button)

class BotInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @commands.hybrid_command(name="botinfo")
    async def botinfo(self, ctx):
        """Display bot information"""
        
        # Calculate bot age (assuming created September 4, 2025)
        created_date = datetime(2025, 9, 4)
        current_date = datetime.now()
        age_days = (current_date - created_date).days
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.start_time)
        uptime_delta = timedelta(seconds=uptime_seconds)
        uptime_days = uptime_delta.days
        uptime_hours = uptime_delta.seconds // 3600
        uptime_minutes = (uptime_delta.seconds % 3600) // 60
        
        # Get bot stats
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        
        # Get bot ping
        ping = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="Dravon Bot Information",
            description="*Your all-in-one Discord server management solution*",
            color=0x7289da
        )
        
        # Basic Information
        basic_info = f"```yaml\nName: Dravon™\nID: {self.bot.user.id}\nCreated: September 4, 2025\nAge: {age_days} days\n```"
        embed.add_field(name="Basic Information", value=basic_info, inline=False)
        
        # Developer
        developer_info = f"```yaml\nCreated by: Shadow (@1037768611126841405)\nVersion: 3.3.6\nLanguage: Python 3.11\nFramework: discord.py\n```"
        embed.add_field(name="Developer", value=developer_info, inline=False)
        
        # Presence
        presence_info = f"```yaml\nServers: {len(self.bot.guilds)}\nUsers: {total_users:,}\nChannels: {total_channels:,}\n```"
        embed.add_field(name="Presence", value=presence_info, inline=False)
        
        # Latest Features
        features = "> - Advanced Ticket System\n> - Enhanced Security\n> - New Moderation System"
        embed.add_field(name="✨ Latest Features", value=features, inline=False)
        
        # Performance
        performance_info = f"```yaml\nPing: {ping}ms\nUptime: {uptime_days} days, {uptime_hours} hours, {uptime_minutes} minutes\nStatus: 🟢 Online\n```"
        embed.add_field(name="Performance", value=performance_info, inline=False)
        
        # Set bot avatar as thumbnail
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Footer
        embed.set_footer(text="Powered by Dravon™")
        
        view = BotInfoView()
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="support")
    async def support(self, ctx):
        """Get official support and invite links"""
        
        embed = discord.Embed(
            title="🛠️ Dravon Support",
            description="Need help with Dravon? Join our official support server!\n\n🔗 **Support Server:** [Click Here](https://discord.gg/UKR78VcEtg)\n\n📥 **Add Dravon to Your Server:** [Invite Me](https://discord.com/oauth2/authorize?client_id=1412942933405208668&permissions=8&integration_type=0&scope=bot)",
            color=0x7289da
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413147301295423649/18cd287d-46a1-42d5-9626-028c88f90225.jpg?ex=68badf7b&is=68b98dfb&hm=89ccdda5d63c9b65e4d3e4898cbdf1ddb2f75412172cfff6aea7cf18e3bf714a&")
        embed.set_footer(text="Powered by Dravon™")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="partnership")
    async def partnership(self, ctx):
        """Display BlazeNode hosting partnership information"""
        
        embed = discord.Embed(
            title="BlazeNode Hosting || Partnership",
            description="**🤝 Official Partnership with BlazeNode Hosting**\n\nWe're proud to partner with BlazeNode Hosting to provide you with the best Discord bot hosting experience!\n\n**🎆 What BlazeNode Offers:**\n• **High-Performance Servers** - Lightning-fast bot hosting\n• **24/7 Uptime** - Your bots stay online around the clock\n• **Easy Setup** - Get your bot running in minutes\n• **Affordable Pricing** - Premium hosting at great prices\n• **Expert Support** - Professional help when you need it\n\n*Experience reliable hosting with our trusted partner!*",
            color=0x87ceeb
        )
        
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413202901521797180/5e80888f-ecff-42cf-a6e5-95d0a5c28dcc.jpg?ex=68bb1343&is=68b9c1c3&hm=88f71353035ff865b29778cfe3465ed4642682490d4c2127da9fe61495e4c199&")
        embed.set_footer(text="Powered by Dravon™")
        
        # Add BlazeNode button
        view = discord.ui.View(timeout=None)
        blazenode_button = discord.ui.Button(
            label="Join BlazeNode",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/NCDpChD6US",
            emoji="🔥"
        )
        view.add_item(blazenode_button)
        
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))