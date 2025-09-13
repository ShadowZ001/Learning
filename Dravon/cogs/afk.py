import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class AFKSettingsView(discord.ui.View):
    def __init__(self, bot, user_id, reason):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.reason = reason
    
    @discord.ui.button(label="DM on Mention", style=discord.ButtonStyle.secondary, emoji="📩")
    async def dm_on_mention(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.client.db.set_afk_user(self.user_id, self.reason, dm_enabled=True)
        
        embed = discord.Embed(
            title="💤 AFK Status Set",
            description=f"<@{self.user_id}>: You're now AFK with the status: {self.reason}\n*You will receive DMs when mentioned*",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=interaction.client.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="No DMs", style=discord.ButtonStyle.secondary, emoji="🔕")
    async def no_dms(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.client.db.set_afk_user(self.user_id, self.reason, dm_enabled=False)
        
        embed = discord.Embed(
            title="💤 AFK Status Set",
            description=f"<@{self.user_id}>: You're now AFK with the status: {self.reason}\n*You will not receive DMs when mentioned*",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=interaction.client.user.display_avatar.url)
        
        await interaction.response.edit_message(embed=embed, view=None)

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="afk")
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set your AFK status"""
        
        embed = discord.Embed(
            title="💤 AFK Settings",
            description=f"Setting AFK status: **{reason}**\n\nChoose your notification preference:",
            color=0x808080
        )
        embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
        
        view = AFKSettingsView(self.bot, ctx.author.id, reason)
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Check if user is AFK and remove status if they send a message
        afk_data = await self.bot.db.get_afk_user(message.author.id)
        if afk_data:
            await self.bot.db.remove_afk_user(message.author.id)
            
            embed = discord.Embed(
                title="👋 Welcome Back!",
                description=f"{message.author.mention}, your AFK status has been removed.",
                color=0x808080
            )
            embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
            
            await message.channel.send(embed=embed, delete_after=5)
        
        # Check for mentions of AFK users
        if message.mentions:
            for mentioned_user in message.mentions:
                afk_data = await self.bot.db.get_afk_user(mentioned_user.id)
                if afk_data:
                    reason = afk_data.get("reason", "AFK")
                    dm_enabled = afk_data.get("dm_enabled", False)
                    
                    # Send AFK notification in channel
                    embed = discord.Embed(
                        title="💤 User is AFK",
                        description=f"{mentioned_user.mention} is currently AFK: **{reason}**",
                        color=0x808080
                    )
                    embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
                    
                    await message.channel.send(embed=embed, delete_after=10)
                    
                    # Send DM if enabled
                    if dm_enabled:
                        try:
                            dm_embed = discord.Embed(
                                title="📩 You were mentioned while AFK",
                                description=f"**Server:** {message.guild.name}\n**Channel:** {message.channel.mention}\n**User:** {message.author.mention}\n**Message:** {message.content[:100]}{'...' if len(message.content) > 100 else ''}",
                                color=0x808080
                            )
                            dm_embed.set_author(name="Dravon", icon_url=self.bot.user.display_avatar.url)
                            
                            await mentioned_user.send(embed=dm_embed)
                        except:
                            pass  # User has DMs disabled

async def setup(bot):
    await bot.add_cog(AFK(bot))