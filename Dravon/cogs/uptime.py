import discord
from discord.ext import commands
from datetime import datetime
import time

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()
    
    @commands.hybrid_command(name="uptime")
    async def uptime_command(self, ctx):
        """Show bot uptime"""
        current_time = datetime.now()
        uptime_duration = current_time - self.start_time
        
        # Calculate uptime components
        days = uptime_duration.days
        hours, remainder = divmod(uptime_duration.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        # Format uptime string
        uptime_parts = []
        if days > 0:
            uptime_parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            uptime_parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            uptime_parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
        if seconds > 0 or not uptime_parts:
            uptime_parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
        
        uptime_str = ", ".join(uptime_parts)
        
        embed = discord.Embed(
            title="Dravon Uptime",
            description=f"🟢 Last rebooted {uptime_str} ago",
            color=0x00ff00
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Uptime(bot))