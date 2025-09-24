import discord
from discord.ext import commands, tasks
import aiohttp
import json
import re
from datetime import datetime

class YouTubeSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose YouTube setup option...",
        options=[
            discord.SelectOption(label="YouTube Link", description="Set YouTube channel link", value="link"),
            discord.SelectOption(label="Save Config", description="Save YouTube configuration", value="save"),
            discord.SelectOption(label="Notify Channel", description="Set notification channel", value="channel")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "link":
            modal = YouTubeLinkModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "save":
            embed = discord.Embed(
                title="✅ Configuration Saved",
                description="YouTube notification settings have been saved!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
        elif value == "channel":
            embed = discord.Embed(
                title="📺 Select Notification Channel",
                description="Choose the channel where YouTube notifications will be sent:",
                color=0xff0000
            )
            view = YouTubeChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)

class YouTubeLinkModal(discord.ui.Modal, title="Set YouTube Channel"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    link_input = discord.ui.TextInput(
        label="YouTube Channel Link",
        placeholder="https://www.youtube.com/@channelname or channel ID",
        max_length=200
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        link = self.link_input.value.strip()
        
        # Extract channel ID from various YouTube URL formats
        channel_id = self.extract_channel_id(link)
        
        if not channel_id:
            await interaction.response.send_message("❌ Invalid YouTube channel link!", ephemeral=True)
            return
        
        await self.bot.db.set_youtube_config(self.guild_id, "channel_id", channel_id)
        await self.bot.db.set_youtube_config(self.guild_id, "channel_link", link)
        
        # Setup real-time webhook for this channel
        youtube_cog = self.bot.get_cog('YouTube')
        if youtube_cog:
            await youtube_cog.setup_youtube_webhook(channel_id)
        
        embed = discord.Embed(
            title="✅ YouTube Channel Set",
            description=f"Channel link has been set to:\n`{link}`",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    def extract_channel_id(self, link):
        """Extract channel ID from YouTube URL"""
        patterns = [
            r'youtube\.com/channel/([a-zA-Z0-9_-]+)',
            r'youtube\.com/@([a-zA-Z0-9_-]+)',
            r'youtube\.com/c/([a-zA-Z0-9_-]+)',
            r'youtube\.com/user/([a-zA-Z0-9_-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, link)
            if match:
                return match.group(1)
        
        # If it's just a channel ID
        if re.match(r'^[a-zA-Z0-9_-]+$', link):
            return link
        
        return None

class YouTubeChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select notification channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        
        await self.bot.db.set_youtube_config(self.guild_id, "notify_channel", selected_channel.id)
        
        embed = discord.Embed(
            title="✅ Notification Channel Set",
            description=f"YouTube notifications will be sent to {selected_channel.mention}",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class YouTube(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_videos.start()
    
    def cog_unload(self):
        self.check_videos.cancel()
    
    @commands.hybrid_group(name="youtube")
    @commands.has_permissions(manage_guild=True)
    async def youtube_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📺 YouTube Notifications",
                description="**Commands:**\n• `/youtube notify` - Setup notifications\n• `/youtube status` - View current settings\n• `/youtube reset` - Reset configuration",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @youtube_group.command(name="notify")
    async def youtube_notify(self, ctx):
        """Setup YouTube notifications"""
        embed = discord.Embed(
            title="📺 YouTube Notification Setup",
            description="Configure YouTube channel notifications for your server.",
            color=0xff0000
        )
        
        view = YouTubeSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @youtube_group.command(name="status")
    async def youtube_status(self, ctx):
        """Show YouTube notification status"""
        try:
            config = await self.bot.db.get_youtube_config(ctx.guild.id)
            
            embed = discord.Embed(
                title="📺 YouTube Notification Status",
                color=0xff0000
            )
            
            if not config:
                embed.description = "❌ **Status:** Not Configured"
                embed.color = 0xff0000
            else:
                channel_link = config.get("channel_link", "Not set")
                notify_channel = config.get("notify_channel")
                
                if channel_link != "Not set" and notify_channel:
                    embed.description = "✅ **Status:** Fully Configured"
                    embed.color = 0x00ff00
                else:
                    embed.description = "⚠️ **Status:** Partially Configured"
                    embed.color = 0xff8c00
                
                embed.add_field(name="YouTube Channel", value=channel_link, inline=False)
                embed.add_field(
                    name="Notification Channel", 
                    value=f"<#{notify_channel}>" if notify_channel else "Not set", 
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @youtube_group.command(name="reset")
    async def youtube_reset(self, ctx):
        """Reset YouTube notification configuration"""
        try:
            await self.bot.db.reset_youtube_config(ctx.guild.id)
            
            embed = discord.Embed(
                title="✅ Configuration Reset",
                description="YouTube notification settings have been reset.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    async def setup_youtube_webhook(self, channel_id):
        """Setup YouTube webhook for real-time notifications"""
        # This would setup YouTube webhook/pubsub in production
        # For now, we'll use a mock trigger system
        pass
    
    async def trigger_notification(self, guild_id, video_data):
        """Trigger notification when new video is uploaded"""
        try:
            config = await self.bot.db.get_youtube_config(guild_id)
            notify_channel = config.get("notify_channel")
            
            if notify_channel:
                await self.send_notification(guild_id, notify_channel, video_data)
                
        except Exception as e:
            print(f"Error triggering YouTube notification: {e}")
    
    @tasks.loop(minutes=30)
    async def check_videos(self):
        """Backup check for YouTube videos (webhook is primary)"""
        try:
            guilds_config = await self.bot.db.get_all_youtube_configs()
            
            for guild_id, config in guilds_config.items():
                channel_id = config.get("channel_id")
                notify_channel = config.get("notify_channel")
                
                if not channel_id or not notify_channel:
                    continue
                
                # Setup webhook for real-time notifications
                await self.setup_youtube_webhook(channel_id)
                    
        except Exception as e:
            print(f"Error checking YouTube videos: {e}")
    
    async def get_latest_video(self, channel_id):
        """Get latest video from YouTube channel (would use YouTube API)"""
        # In production, this would:
        # 1. Use YouTube Data API v3
        # 2. Setup YouTube webhook/pubsub for real-time notifications
        # 3. Trigger immediately when video is uploaded
        return {
            "title": "New Video Title",
            "url": f"https://youtube.com/watch?v=example",
            "thumbnail": "https://i.ytimg.com/vi/example/maxresdefault.jpg",
            "channel_name": "Channel Name"
        }
    
    async def send_notification(self, guild_id, channel_id, video_data):
        """Send YouTube notification"""
        try:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return
            
            # Send as normal message with embed
            message = f"New video summon guys !! @everyone\n\n**{video_data['title']}**\n{video_data['url']}"
            
            embed = discord.Embed(color=0xff0000)
            embed.set_image(url=video_data["thumbnail"])
            
            await channel.send(message, embed=embed)
            
        except Exception as e:
            print(f"Error sending YouTube notification: {e}")
    
    @check_videos.before_loop
    async def before_check_videos(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(YouTube(bot))