import discord
from discord.ext import commands

class MusicPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success, row=0)
    async def play_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Use `>play <song>` to play music", ephemeral=True)
    
    @discord.ui.button(emoji="⏸️", style=discord.ButtonStyle.secondary, row=0)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return
        
        await player.pause()
        await interaction.response.send_message("⏸️ Paused", ephemeral=True)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.success, row=0)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No player found!", ephemeral=True)
            return
        
        await player.resume()
        await interaction.response.send_message("▶️ Resumed", ephemeral=True)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary, row=0)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player or not player.current:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)
            return
        
        await player.skip()
        await interaction.response.send_message("⏭️ Skipped", ephemeral=True)
    
    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.danger, row=0)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        player = interaction.guild.voice_client
        if not player:
            await interaction.response.send_message("❌ No player found!", ephemeral=True)
            return
        
        await player.stop()
        if hasattr(player, 'queue'):
            player.queue.clear()
        await interaction.response.send_message("⏹️ Stopped", ephemeral=True)

class MusicPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="musicpanel", aliases=["mp"])
    async def music_panel(self, ctx):
        """Music control panel"""
        
        embed = discord.Embed(
            title="🎵 Music Control Panel",
            description="Control music playback",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="Music Controls",
            value="▶️ **Play** - Start playing music (use >play <song>)\n⏸️ **Pause** - Pause current track\n▶️ **Resume** - Resume paused track\n⏭️ **Skip** - Skip to next track\n⏹️ **Stop** - Stop playback and clear queue",
            inline=False
        )
        
        view = MusicPanelView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(MusicPanel(bot))