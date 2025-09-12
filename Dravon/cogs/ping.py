import discord
from discord.ext import commands
import wavelink
import time

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="ping")
    async def ping_command(self, ctx):
        """Show bot, API, and Lavalink ping"""
        # Measure bot latency
        bot_ping = round(self.bot.latency * 1000)
        
        # Measure API latency
        start_time = time.time()
        message = await ctx.send("🏓 Pinging...")
        api_ping = round((time.time() - start_time) * 1000)
        
        # Measure Lavalink latency
        lavalink_ping = "N/A"
        try:
            node = wavelink.Pool.get_node()
            if node and hasattr(node, 'ping'):
                lavalink_ping = f"{round(node.ping)}ms"
            elif node:
                lavalink_ping = "Connected"
        except:
            lavalink_ping = "Disconnected"
        
        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🤖 Bot Latency",
            value=f"{bot_ping}ms",
            inline=True
        )
        
        embed.add_field(
            name="📡 API Latency",
            value=f"{api_ping}ms",
            inline=True
        )
        
        embed.add_field(
            name="🎵 Lavalink",
            value=lavalink_ping,
            inline=True
        )
        
        # Add status indicators
        if bot_ping < 100:
            bot_status = "🟢 Excellent"
        elif bot_ping < 200:
            bot_status = "🟡 Good"
        else:
            bot_status = "🔴 Poor"
        
        embed.add_field(
            name="📊 Connection Status",
            value=bot_status,
            inline=False
        )
        
        await message.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(Ping(bot))