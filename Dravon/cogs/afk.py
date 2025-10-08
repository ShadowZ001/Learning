import discord
from discord.ext import commands
from datetime import datetime

class AFKView(discord.ui.View):
    def __init__(self, bot, user_id, reason):
        super().__init__(timeout=300)
        self.bot = bot
        self.user_id = user_id
        self.reason = reason
    
    @discord.ui.button(label="DMs", style=discord.ButtonStyle.primary)
    async def dms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only set your own AFK status!", ephemeral=True)
            return
            
        await self.bot.db.set_afk(self.user_id, self.reason, datetime.now(), True)
        
        embed = discord.Embed(
            title="✅ AFK Status Set",
            description=f"Your AFK status has been set with DM notifications enabled.\n**Reason:** {self.reason}",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="No DMs", style=discord.ButtonStyle.secondary)
    async def no_dms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message("❌ You can only set your own AFK status!", ephemeral=True)
            return
            
        await self.bot.db.set_afk(self.user_id, self.reason, datetime.now(), False)
        
        embed = discord.Embed(
            title="✅ AFK Status Set",
            description=f"Your AFK status has been set with DM notifications disabled.\n**Reason:** {self.reason}",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mention_storage = {}
    
    @commands.hybrid_command(name="afk")
    async def afk(self, ctx, *, reason: str = "AFK"):
        """Set your AFK status"""
        
        # Send initial message
        await ctx.send(f"@{ctx.author.display_name} ??")
        
        # Send embed with buttons
        embed = discord.Embed(
            title="Where do you want your AFK status shown?",
            description=f"**DMs On Mention** (We will inform you) or **No DMs** (We will not inform you)\n\n**Reason:** {reason}",
            color=0x7289da
        )
        
        view = AFKView(self.bot, ctx.author.id, reason)
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Check if user is AFK and remove status
        try:
            afk_data = await self.bot.db.get_afk(message.author.id)
            if afk_data:
                # Calculate AFK duration
                afk_start = datetime.fromisoformat(afk_data['timestamp'])
                afk_duration = datetime.now() - afk_start
                
                # Format duration
                hours, remainder = divmod(int(afk_duration.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                
                if hours > 0:
                    duration_str = f"{hours}h {minutes}m"
                elif minutes > 0:
                    duration_str = f"{minutes}m {seconds}s"
                else:
                    duration_str = f"{seconds}s"
                
                # Get mentions while AFK
                mentions_text = ""
                if message.author.id in self.mention_storage:
                    mentions = self.mention_storage[message.author.id]
                    if mentions:
                        mentions_text = f"\n**Mentions:**\n" + "\n".join(mentions)
                    del self.mention_storage[message.author.id]
                
                # Remove AFK status
                await self.bot.db.remove_afk(message.author.id)
                
                # Send welcome back message
                welcome_msg = f"Welcome back {message.author.display_name}! I removed your AFK. You were AFK for **{duration_str}**{mentions_text}"
                await message.channel.send(welcome_msg)
                
        except Exception as e:
            print(f"Error in AFK removal: {e}")
        
        # Check for mentions of AFK users
        if message.mentions:
            for mentioned_user in message.mentions:
                try:
                    afk_data = await self.bot.db.get_afk(mentioned_user.id)
                    if afk_data:
                        reason = afk_data.get("reason", "AFK")
                        dm_enabled = afk_data.get("dm_enabled", False)
                        
                        # Send AFK notification in channel
                        await message.channel.send(f"{mentioned_user.display_name} is currently AFK: {reason}")
                        
                        # Store mention for when user returns
                        if mentioned_user.id not in self.mention_storage:
                            self.mention_storage[mentioned_user.id] = []
                        
                        mention_info = f"{message.author.display_name} in #{message.channel.name}"
                        self.mention_storage[mentioned_user.id].append(mention_info)
                        
                        # Keep only last 10 mentions
                        if len(self.mention_storage[mentioned_user.id]) > 10:
                            self.mention_storage[mentioned_user.id] = self.mention_storage[mentioned_user.id][-10:]
                        
                        # Send DM if enabled
                        if dm_enabled:
                            try:
                                dm_embed = discord.Embed(
                                    title="📩 You were mentioned while AFK",
                                    description=f"**Server:** {message.guild.name}\n**Channel:** #{message.channel.name}\n**User:** {message.author.display_name}\n**Message:** {message.content[:200]}{'...' if len(message.content) > 200 else ''}",
                                    color=0x7289da,
                                    timestamp=message.created_at
                                )
                                await mentioned_user.send(embed=dm_embed)
                            except:
                                pass
                                
                except Exception as e:
                    print(f"Error checking AFK mention: {e}")

async def setup(bot):
    await bot.add_cog(AFK(bot))