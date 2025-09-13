import discord
from discord.ext import commands
import wavelink

class MusicControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(emoji="⏯️", style=discord.ButtonStyle.secondary, row=0)
    async def play_pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No music player found!", ephemeral=True)
            return
        
        if player.paused:
            await player.resume()
            await interaction.response.send_message("▶️ Resumed playback!", ephemeral=True)
        else:
            await player.pause()
            await interaction.response.send_message("⏸️ Paused playback!", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary, row=0)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return
        
        await player.skip()
        await interaction.response.send_message("⏭️ Skipped track!", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No music player found!", ephemeral=True)
            return
        
        await player.stop()
        if hasattr(player, 'queue'):
            player.queue.clear()
        await interaction.response.send_message("⏹️ Stopped playback!", ephemeral=True)
    
    @discord.ui.button(emoji="🔀", style=discord.ButtonStyle.secondary, row=0)
    async def shuffle(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.queue:
            await interaction.response.send_message("❌ No queue to shuffle!", ephemeral=True)
            return
        
        player.queue.shuffle()
        await interaction.response.send_message("🔀 Queue shuffled!", ephemeral=True)
    
    @discord.ui.button(emoji="🔁", style=discord.ButtonStyle.secondary, row=0)
    async def loop(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No music player found!", ephemeral=True)
            return
        
        player.autoplay = not player.autoplay
        status = "enabled" if player.autoplay else "disabled"
        await interaction.response.send_message(f"🔁 Autoplay {status}!", ephemeral=True)
    
    @discord.ui.button(emoji="📜", style=discord.ButtonStyle.primary, row=1)
    async def queue(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.queue:
            await interaction.response.send_message("❌ Queue is empty!", ephemeral=True)
            return
        
        queue_list = []
        for i, track in enumerate(list(player.queue)[:10], 1):
            queue_list.append(f"{i}. {track.title}")
        
        embed = discord.Embed(
            title="📜 Current Queue",
            description="\n".join(queue_list),
            color=0x87CEEB
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.primary, row=1)
    async def volume(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No music player found!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔊 Volume Control",
            description=f"Current volume: **{player.volume}%**\nUse `>volume <1-100>` to change volume",
            color=0x87CEEB
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary, row=1)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏮️ Previous track feature coming soon!", ephemeral=True)
    
    @discord.ui.button(emoji="🎵", style=discord.ButtonStyle.success, row=1)
    async def now_playing(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎵 Now Playing",
            description=f"**{player.current.title}**\nBy: {player.current.author}",
            color=0x87CEEB
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(emoji="🔌", style=discord.ButtonStyle.danger, row=1)
    async def disconnect(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ Bot is not connected!", ephemeral=True)
            return
        
        await player.disconnect()
        await interaction.response.send_message("🔌 Disconnected from voice channel!", ephemeral=True)

class VoiceControlView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.secondary, row=0)
    async def mute_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("❌ You don't have permission to mute members!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        muted_count = 0
        
        for member in channel.members:
            if not member.bot and not member.voice.mute:
                try:
                    await member.edit(mute=True)
                    muted_count += 1
                except:
                    pass
        
        await interaction.response.send_message(f"🔇 Muted {muted_count} members!", ephemeral=True)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary, row=0)
    async def unmute_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message("❌ You don't have permission to unmute members!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        unmuted_count = 0
        
        for member in channel.members:
            if not member.bot and member.voice.mute:
                try:
                    await member.edit(mute=False)
                    unmuted_count += 1
                except:
                    pass
        
        await interaction.response.send_message(f"🔊 Unmuted {unmuted_count} members!", ephemeral=True)
    
    @discord.ui.button(emoji="🔕", style=discord.ButtonStyle.secondary, row=0)
    async def deafen_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.deafen_members:
            await interaction.response.send_message("❌ You don't have permission to deafen members!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        deafened_count = 0
        
        for member in channel.members:
            if not member.bot and not member.voice.deaf:
                try:
                    await member.edit(deafen=True)
                    deafened_count += 1
                except:
                    pass
        
        await interaction.response.send_message(f"🔕 Deafened {deafened_count} members!", ephemeral=True)
    
    @discord.ui.button(emoji="🔔", style=discord.ButtonStyle.secondary, row=0)
    async def undeafen_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.deafen_members:
            await interaction.response.send_message("❌ You don't have permission to undeafen members!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        undeafened_count = 0
        
        for member in channel.members:
            if not member.bot and member.voice.deaf:
                try:
                    await member.edit(deafen=False)
                    undeafened_count += 1
                except:
                    pass
        
        await interaction.response.send_message(f"🔔 Undeafened {undeafened_count} members!", ephemeral=True)
    
    @discord.ui.button(emoji="👥", style=discord.ButtonStyle.primary, row=1)
    async def voice_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        members = [m for m in channel.members if not m.bot]
        
        embed = discord.Embed(
            title=f"🎤 {channel.name}",
            description=f"**Members:** {len(members)}\n**Limit:** {channel.user_limit or 'Unlimited'}\n**Bitrate:** {channel.bitrate//1000}kbps",
            color=0x808080
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        
        if members:
            member_list = [f"• {m.display_name}" for m in members[:10]]
            embed.add_field(
                name="👥 Members",
                value="\n".join(member_list),
                inline=False
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(emoji="🎯", style=discord.ButtonStyle.primary, row=1)
    async def move_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("❌ You don't have permission to move members!", ephemeral=True)
            return
            
        await interaction.response.send_message("🎯 Move all feature: Use Discord's built-in drag & drop to move members!", ephemeral=True)
    
    @discord.ui.button(emoji="🔒", style=discord.ButtonStyle.danger, row=1)
    async def lock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage channels!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        try:
            await channel.set_permissions(interaction.guild.default_role, connect=False)
            await interaction.response.send_message(f"🔒 Locked {channel.name}!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Failed to lock channel!", ephemeral=True)
    
    @discord.ui.button(emoji="🔓", style=discord.ButtonStyle.success, row=1)
    async def unlock_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("❌ You don't have permission to manage channels!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        try:
            await channel.set_permissions(interaction.guild.default_role, connect=None)
            await interaction.response.send_message(f"🔓 Unlocked {channel.name}!", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Failed to unlock channel!", ephemeral=True)
    
    @discord.ui.button(emoji="📊", style=discord.ButtonStyle.primary, row=1)
    async def voice_stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        members = channel.members
        muted = len([m for m in members if m.voice.mute])
        deafened = len([m for m in members if m.voice.deaf])
        
        embed = discord.Embed(
            title="📊 Voice Channel Statistics",
            color=0x808080
        )
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.add_field(name="👥 Total Members", value=len(members), inline=True)
        embed.add_field(name="🔇 Muted", value=muted, inline=True)
        embed.add_field(name="🔕 Deafened", value=deafened, inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(emoji="🚫", style=discord.ButtonStyle.danger, row=2)
    async def kick_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.move_members:
            await interaction.response.send_message("❌ You don't have permission to move members!", ephemeral=True)
            return
            
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You must be in a voice channel!", ephemeral=True)
            return
        
        channel = interaction.user.voice.channel
        kicked_count = 0
        
        for member in channel.members:
            if not member.bot and member != interaction.user:
                try:
                    await member.move_to(None)
                    kicked_count += 1
                except:
                    pass
        
        await interaction.response.send_message(f"🚫 Disconnected {kicked_count} members!", ephemeral=True)

class MusicPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="musicpanel", aliases=["mpanel", "mp"])
    async def music_panel(self, ctx):
        """Open the music control panel"""
        embed = discord.Embed(
            title="🎵 Music Control Panel",
            description="Use the buttons below to control music playback",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        view = MusicControlView(self.bot)
        await ctx.send(embed=embed, view=view)
    
    @commands.hybrid_command(name="voicepanel", aliases=["vpanel", "vp"])
    async def voice_panel(self, ctx):
        """Open the voice control panel"""
        embed = discord.Embed(
            title="🎤 Voice Control Panel",
            description="Use the buttons below to control voice channel members",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        view = VoiceControlView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MusicPanel(bot))