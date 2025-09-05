import discord
from discord.ext import commands
import time

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
        self.session_messages = 0
        self.session_commands = 0
        self.total_messages = 0
        self.total_commands = 0
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            self.session_messages += 1
            self.total_messages += 1
    
    @commands.Cog.listener()
    async def on_command(self, ctx):
        self.session_commands += 1
        self.total_commands += 1
    
    @commands.hybrid_command(name="stats")
    async def stats(self, ctx):
        """Display bot statistics"""
        
        # Get channel counts
        text_channels = 0
        voice_channels = 0
        stage_channels = 0
        
        for guild in self.bot.guilds:
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text_channels += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice_channels += 1
                elif isinstance(channel, discord.StageChannel):
                    stage_channels += 1
        
        # Get other stats
        guild_count = len(self.bot.guilds)
        user_count = sum(guild.member_count for guild in self.bot.guilds)
        
        # Send normal message first
        await ctx.send(f"📊 Stats For **{self.bot.user.name}** || **v3.3.6**")
        
        # Create embed
        embed = discord.Embed(color=0xffffff)  # White color
        
        embed.add_field(
            name="Last Boot",
            value=f"<t:{int(self.start_time)}:R>",
            inline=True
        )
        
        embed.add_field(
            name="Developer",
            value="dev_shadowz",
            inline=True
        )
        
        embed.add_field(
            name="Server Count",
            value=f"{guild_count:,}",
            inline=True
        )
        
        embed.add_field(
            name="Text Channels",
            value=f"{text_channels:,}",
            inline=True
        )
        
        embed.add_field(
            name="Voice Channels",
            value=f"{voice_channels:,}",
            inline=True
        )
        
        embed.add_field(
            name="Stage Channels",
            value=f"{stage_channels:,}",
            inline=True
        )
        
        embed.add_field(
            name="Member Count",
            value=f"{user_count:,}",
            inline=True
        )
        
        embed.add_field(
            name="Total Messages",
            value=f"{self.total_messages:,}",
            inline=True
        )
        
        embed.add_field(
            name="Session Messages",
            value=f"{self.session_messages:,}",
            inline=True
        )
        
        embed.add_field(
            name="Command Count",
            value=f"{len(self.bot.commands)}",
            inline=True
        )
        
        embed.add_field(
            name="Total Commands",
            value=f"{self.total_commands:,}",
            inline=True
        )
        
        embed.add_field(
            name="Session Commands",
            value=f"{self.session_commands:,}",
            inline=True
        )
        
        # Set bot avatar as thumbnail
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.set_footer(text="Powered by Dravon™")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Stats(bot))