import discord
from discord.ext import commands

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="users")
    async def users_command(self, ctx):
        """Show global bot statistics"""
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_servers = len(self.bot.guilds)
        total_shards = self.bot.shard_count or 1
        
        embed = discord.Embed(
            title="Dravon Global Stats",
            description=f"👥 **Total Users:** {total_users:,}\n🛡️ **Servers:** {total_servers:,}\n⚙️ **Shards:** {total_shards}",
            color=0x7289da
        )
        
        # Add shard breakdown if sharded
        if self.bot.shard_count and self.bot.shard_count > 1:
            shard_info = []
            for shard_id in range(min(self.bot.shard_count, 3)):  # Show max 3 shards
                shard_guilds = [g for g in self.bot.guilds if g.shard_id == shard_id]
                shard_users = sum(g.member_count for g in shard_guilds)
                shard_info.append(f"Shard {shard_id}: {len(shard_guilds)} servers, {shard_users:,} users")
            
            if self.bot.shard_count > 3:
                shard_info.append(f"... and {self.bot.shard_count - 3} more shards")
            
            embed.add_field(
                name="- Shard Breakdown -",
                value="\n".join(shard_info),
                inline=False
            )
        else:
            embed.add_field(
                name="- Shard Breakdown -",
                value="Single shard deployment",
                inline=False
            )
        
        embed.set_author(name="Dravon Global Stats", icon_url=self.bot.user.display_avatar.url)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        await ctx.send(embed=embed)
    
    def get_memory_usage(self):
        """Get memory usage in MB"""
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            return round(process.memory_info().rss / 1024 / 1024, 1)
        except:
            return "N/A"

async def setup(bot):
    await bot.add_cog(Users(bot))