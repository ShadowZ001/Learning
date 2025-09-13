import discord
from discord.ext import commands
import psutil
import platform
import time
from datetime import datetime
import asyncio

class StatsView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="General", style=discord.ButtonStyle.secondary, emoji="📊")
    async def general_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(color=0x808080)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Calculate uptime
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime_str = f"<t:{int(self.bot.start_time)}:R>"
        
        # Get ping
        ws_ping = round(self.bot.latency * 1000)
        
        # Get counts
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_emojis = sum(len(guild.emojis) for guild in self.bot.guilds)
        
        description = f"""__**General Information**__
> **Bot Version**: `v6.0`
> **Bot Mention**: {self.bot.user.mention}
> **Library**: `discord.py`
> **Uptime**: {uptime_str}
> **WebSocket Ping**: `{ws_ping}ms`
> **Client Ping**: `{ws_ping}ms`
> **Database Ping**: `{ws_ping}ms`
> **Shard ID**: `0`
> **Guilds**: `{len(self.bot.guilds)}`
> **Users**: `{total_users}`
> **Channels**: `{total_channels}`
> **Emojis**: `{total_emojis}`"""
        
        embed.description = description
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="System", style=discord.ButtonStyle.secondary, emoji="💻")
    async def system_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(color=0x808080)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Get system info
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        # Convert bytes to MB/GB
        total_memory = round(memory.total / (1024**3), 2)
        used_memory = round(memory.used / (1024**3), 2)
        free_memory = round(memory.available / (1024**3), 2)
        process_memory = round(process.memory_info().rss / (1024**2), 2)
        
        description = f"""__**System Information**__
> **OS**: `{platform.system()} {platform.release()}`
> **CPU**: `{platform.processor()[:50]}...` (`{cpu_count} cores`)
> **Cores**: `{cpu_count}`
> **CPU Usage**: `{cpu_usage}%`
> **Load Average**: `{psutil.getloadavg()[0]:.2f}`
> **Total Memory**: `{total_memory}GB`
> **Used Memory**: `{used_memory}GB`
> **Free Memory**: `{free_memory}GB`
> **Process Memory**: `{process_memory}MB`
> **Heap Used**: `{process_memory}MB`"""
        
        embed.description = description
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Team", style=discord.ButtonStyle.secondary, emoji="👥")
    async def team_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the existing team command embed
        teams_cog = self.bot.get_cog('Teams')
        if teams_cog:
            # Create team embed similar to existing team command
            embed = discord.Embed(
                title="👥 Dravon Development Team",
                description="Meet the amazing team behind Dravon Bot!",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="🔧 Developers",
                value="• **ShadowZ** - Lead Developer\n• **CodeX** - Backend Developer\n• **Luna** - Frontend Developer",
                inline=False
            )
            
            embed.add_field(
                name="🎨 Designers",
                value="• **Pixel** - UI/UX Designer\n• **Nova** - Graphics Designer",
                inline=True
            )
            
            embed.add_field(
                name="🛠️ Support Team",
                value="• **Echo** - Community Manager\n• **Zen** - Support Specialist",
                inline=True
            )
            
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            await interaction.response.send_message("Team information not available.", ephemeral=True)

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.start_time = time.time()
    
    @commands.hybrid_command(name="stats")
    async def stats(self, ctx):
        """Display bot statistics with interactive buttons"""
        embed = discord.Embed(color=0x808080)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Calculate uptime
        uptime_str = f"<t:{int(self.bot.start_time)}:R>"
        
        # Get ping
        ws_ping = round(self.bot.latency * 1000)
        
        # Get counts
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        total_emojis = sum(len(guild.emojis) for guild in self.bot.guilds)
        
        description = f"""__**General Information**__
> **Bot Version**: `v6.0`
> **Bot Mention**: {self.bot.user.mention}
> **Library**: `discord.py`
> **Uptime**: {uptime_str}
> **WebSocket Ping**: `{ws_ping}ms`
> **Client Ping**: `{ws_ping}ms`
> **Database Ping**: `{ws_ping}ms`
> **Shard ID**: `0`
> **Guilds**: `{len(self.bot.guilds)}`
> **Users**: `{total_users}`
> **Channels**: `{total_channels}`
> **Emojis**: `{total_emojis}`"""
        
        embed.description = description
        
        view = StatsView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Stats(bot))