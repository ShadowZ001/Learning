import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class LogsSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
    
    @discord.ui.button(label="AutoRule Logs", style=discord.ButtonStyle.primary, emoji="⚖️")
    async def autorule_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚖️ AutoRule Logs Channel Setup",
            description="Please mention a channel in the chat where AutoRule violations and actions will be logged.\n\nExample: `#autorule-logs`",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
        
        try:
            msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
            
            if msg.channel_mentions:
                channel = msg.channel_mentions[0]
                await interaction.client.db.set_autorule_logs_channel(interaction.guild.id, channel.id)
                
                embed = discord.Embed(
                    title="✅ AutoRule Logs Channel Successfully Configured",
                    description=f"AutoRule violations and enforcement actions will now be logged to {channel.mention}",
                    color=0x00ff00
                )
                await msg.reply(embed=embed)
            else:
                await msg.reply("Please mention a valid channel.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("Setup timed out. Please try again.")
    
    @discord.ui.button(label="Welcome System Logs", style=discord.ButtonStyle.primary, emoji="👋")
    async def welcome_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="👋 Welcome System Logs Channel Setup",
            description="Please mention a channel in the chat where Welcome System events and member joins will be logged.\n\nExample: `#welcome-logs`",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
        
        try:
            msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
            
            if msg.channel_mentions:
                channel = msg.channel_mentions[0]
                await interaction.client.db.set_welcome_logs_channel(interaction.guild.id, channel.id)
                
                embed = discord.Embed(
                    title="✅ Welcome System Logs Channel Successfully Configured",
                    description=f"Welcome system events and member activities will now be logged to {channel.mention}",
                    color=0x00ff00
                )
                await msg.reply(embed=embed)
            else:
                await msg.reply("Please mention a valid channel.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("Setup timed out. Please try again.")
    
    @discord.ui.button(label="AutoMod Logs", style=discord.ButtonStyle.primary, emoji="🤖")
    async def automod_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🤖 AutoMod Logs Channel Setup",
            description="Please mention a channel in the chat where AutoMod detections and actions will be logged.\n\nExample: `#automod-logs`",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
        
        try:
            msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
            
            if msg.channel_mentions:
                channel = msg.channel_mentions[0]
                await interaction.client.db.set_automod_logs_channel(interaction.guild.id, channel.id)
                
                embed = discord.Embed(
                    title="✅ AutoMod Logs Channel Successfully Configured",
                    description=f"AutoMod violations and enforcement actions will now be logged to {channel.mention}",
                    color=0x00ff00
                )
                await msg.reply(embed=embed)
            else:
                await msg.reply("Please mention a valid channel.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("Setup timed out. Please try again.")
    
    @discord.ui.button(label="AntiNuke Logs", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def antinuke_logs(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ AntiNuke Logs Channel Setup",
            description="Please mention a channel in the chat where AntiNuke security events and threat detections will be logged.\n\nExample: `#antinuke-logs`",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
        
        try:
            msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
            
            if msg.channel_mentions:
                channel = msg.channel_mentions[0]
                await interaction.client.db.set_antinuke_logs_channel(interaction.guild.id, channel.id)
                
                embed = discord.Embed(
                    title="✅ AntiNuke Logs Channel Successfully Configured",
                    description=f"AntiNuke security events and threat detections will now be logged to {channel.mention}",
                    color=0x00ff00
                )
                await msg.reply(embed=embed)
            else:
                await msg.reply("Please mention a valid channel.")
                
        except asyncio.TimeoutError:
            await interaction.followup.send("Setup timed out. Please try again.")

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="setuplogs")
    async def setup_logs(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="📋 Comprehensive Logging System Configuration",
            description="**Configure logging channels for all bot systems and features.**\n\nSelect the logging system you want to configure by clicking the appropriate button below. Each system will log different types of events to help you monitor your server effectively.\n\n**Available Logging Systems:**\n\n⚖️ **AutoRule Logs** → Rule violations and enforcement actions\n👋 **Welcome System Logs** → Member joins and welcome events\n🤖 **AutoMod Logs** → Content filtering and moderation actions\n🛡️ **AntiNuke Logs** → Security threats and protection events\n\nClick a button below to configure the logging channel for that system.",
            color=0x7289da
        )
        
        view = LogsSetupView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Logs(bot))