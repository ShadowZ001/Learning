import discord
from discord.ext import commands
import time
from datetime import datetime

class Uptime(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="uptime")
    async def uptime(self, ctx):
        """Display bot uptime"""
        
        uptime_seconds = int(time.time() - self.bot.start_time)
        uptime_str = f"<t:{int(self.bot.start_time)}:R>"
        
        embed = discord.Embed(
            title="⏰ Bot Uptime",
            description=f"**Started:** {uptime_str}",
            color=0x2f3136
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Calculate time components
        days = uptime_seconds // 86400
        hours = (uptime_seconds % 86400) // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        uptime_formatted = f"{days}d {hours}h {minutes}m {seconds}s"
        
        embed.add_field(
            name="📊 Duration",
            value=f"`{uptime_formatted}`",
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Uptime(bot))