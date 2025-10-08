import discord
from discord.ext import commands

class VoicePanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.success, row=0)
    async def join_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("❌ You need to be in a voice channel!", ephemeral=True)
            return
        
        try:
            if interaction.guild.voice_client:
                await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            else:
                await interaction.user.voice.channel.connect()
            await interaction.response.send_message(f"✅ Joined {interaction.user.voice.channel.mention}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to join: {str(e)}", ephemeral=True)
    
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.danger, row=0)
    async def leave_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
            return
        
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("✅ Left voice channel", ephemeral=True)
    
    @discord.ui.button(emoji="🔇", style=discord.ButtonStyle.secondary, row=0)
    async def mute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
            return
        
        try:
            await interaction.guild.me.edit(mute=True)
            await interaction.response.send_message("🔇 Bot muted", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to mute: {str(e)}", ephemeral=True)
    
    @discord.ui.button(emoji="🔊", style=discord.ButtonStyle.secondary, row=0)
    async def unmute_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
            return
        
        try:
            await interaction.guild.me.edit(mute=False)
            await interaction.response.send_message("🔊 Bot unmuted", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to unmute: {str(e)}", ephemeral=True)
    
    @discord.ui.button(emoji="🔕", style=discord.ButtonStyle.secondary, row=0)
    async def deafen_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.guild.voice_client:
            await interaction.response.send_message("❌ Bot is not in a voice channel!", ephemeral=True)
            return
        
        try:
            await interaction.guild.me.edit(deafen=True)
            await interaction.response.send_message("🔕 Bot deafened", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to deafen: {str(e)}", ephemeral=True)

class VoicePanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="voicepanel", aliases=["vp"])
    async def voice_panel(self, ctx):
        """Voice control panel"""
        
        embed = discord.Embed(
            title="🎙️ Voice Control Panel",
            description="Control bot voice settings",
            color=0x808080
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        embed.add_field(
            name="Voice Controls",
            value="🔊 **Join** - Connect to your voice channel\n🔇 **Leave** - Disconnect from voice channel\n🔇 **Mute** - Mute bot microphone\n🔊 **Unmute** - Unmute bot microphone\n🔕 **Deafen** - Bot can't hear audio",
            inline=False
        )
        
        view = VoicePanelView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(VoicePanel(bot))