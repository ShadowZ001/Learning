import discord
from discord.ext import commands
import re
import random
import time
from utils.embed_utils import add_dravon_footer
try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import aiohttp
    import io
    import math
    CANVA_AVAILABLE = True
except ImportError:
    CANVA_AVAILABLE = False
    print("⚠️ PIL not installed. Canvacard features disabled.")

class CanvaSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose Canvacard configuration...",
        options=[
            discord.SelectOption(label="Enable Canvacard", description="Turn on beautiful visual level-up cards", value="enable", emoji="✅"),
            discord.SelectOption(label="Disable Canvacard", description="Use normal text embeds for level-ups", value="disable", emoji="❌"),
            discord.SelectOption(label="Set Channel", description="Choose channel for level-up messages", value="channel", emoji="📍"),
            discord.SelectOption(label="Canva Test", description="Test the Canvacard in selected channel", value="test", emoji="🧪")
        ]
    )
    async def canva_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "enable":
            await interaction.client.db.set_canva_setting(self.guild_id, "enabled", True)
            
            embed = discord.Embed(
                title="✅ Canvacard Enabled",
                description="Beautiful visual level-up cards are now enabled!\nLevel-up messages will show custom rank cards with user avatars.",
                color=0x00ff00
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=self)
            
        elif value == "disable":
            await interaction.client.db.set_canva_setting(self.guild_id, "enabled", False)
            
            embed = discord.Embed(
                title="❌ Canvacard Disabled",
                description="Level-up messages will use normal text embeds.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=self)
            
        elif value == "channel":
            embed = discord.Embed(
                title="📍 Set Level-Up Channel",
                description="Please mention the channel where level-up messages should be sent.\n\n**Example:** #level-ups",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=ChannelSetupView(self.bot, self.guild_id))
            
        elif value == "test":
            # Get configured channel
            config = await interaction.client.db.get_levelup_config(self.guild_id)
            channel_id = config.get("channel") if config else None
            
            if not channel_id:
                await interaction.response.send_message("❌ **No channel configured!** Please set a channel first using 'Set Channel' option.", ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("❌ **Channel not found!** Please reconfigure the channel.", ephemeral=True)
                return
            
            # Create and send test card
            cog = interaction.client.get_cog("LevelUp")
            card_bytes = await cog.create_canva_card(interaction.user, 5, 750, 12)
            
            if card_bytes:
                file = discord.File(io.BytesIO(card_bytes), filename="canva-test.png")
                # Send test message in chat format
                test_msg = f"🧪 **Test:** {interaction.user.display_name} just leveled up to **Level 5**! This is a Canvacard test! 🎉"
                await channel.send(test_msg, file=file)
                await interaction.response.send_message(f"✅ **Test sent to {channel.mention}!** Check the channel to see your Canvacard.", ephemeral=True)
            else:
                await interaction.response.send_message("❌ **Failed to create test card.** Please check the logs.", ephemeral=True)

class ChannelSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select level-up channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        
        await interaction.client.db.set_levelup_setting(self.guild_id, "channel", channel.id)
        
        embed = discord.Embed(
            title="✅ Channel Set",
            description=f"Level-up messages will be sent to {channel.mention}\n\nYou can now test the Canvacard using the dropdown menu.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await interaction.response.edit_message(embed=embed, view=CanvaSetupView(self.bot, self.guild_id))

class TestLevelUpView(discord.ui.View):
    def __init__(self, bot, guild_id, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.user = user
    
    @discord.ui.select(
        placeholder="Choose test type...",
        options=[
            discord.SelectOption(label="Test Normal Levelup", description="Test standard embed level-up message", value="normal", emoji="📝"),
            discord.SelectOption(label="Test Canvacard Levelup", description="Test visual Canvacard level-up (Premium)", value="canva", emoji="🎨"),
            discord.SelectOption(label="Set Test Channel", description="Choose channel for test messages", value="channel", emoji="📍")
        ]
    )
    async def test_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "normal":
            # Get configured channel
            config = await interaction.client.db.get_levelup_config(self.guild_id)
            channel_id = config.get("channel") if config else None
            
            if not channel_id:
                await interaction.response.send_message("❌ **No channel configured!** Please set a channel first using 'Set Test Channel' option.", ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("❌ **Channel not found!** Please reconfigure the channel using 'Set Test Channel' option.", ephemeral=True)
                return
            
            # Get current user data
            user_data = await interaction.client.db.get_user_xp(self.guild_id, self.user.id)
            current_level = user_data.get("level", 1) if user_data else 1
            new_level = current_level + 1
            new_xp = ((new_level - 1) ** 2) * 100
            
            # Get user rank
            leaderboard = await interaction.client.db.get_leaderboard(self.guild_id, 0)
            user_rank = 1
            for i, user_entry in enumerate(leaderboard):
                if user_entry.get("user_id") == self.user.id:
                    user_rank = i + 1
                    break
            
            # Update database
            await interaction.client.db.set_user_xp(self.guild_id, self.user.id, new_xp, new_level)
            
            # Create fake message for testing
            class FakeMessage:
                def __init__(self, author, guild, channel):
                    self.author = author
                    self.guild = guild
                    self.channel = channel
            
            fake_msg = FakeMessage(self.user, interaction.guild, channel)
            
            # Send normal level-up message with full tracking
            cog = interaction.client.get_cog("LevelUp")
            await cog.send_levelup_message(fake_msg, new_level, new_xp, user_rank, use_canva=False)
            
            await interaction.response.send_message(f"✅ **Normal levelup tested in {channel.mention}!** You are now level {new_level} with full XP tracking.", ephemeral=True)
            
        elif value == "canva":
            # Check premium status
            is_premium = await interaction.client.db.is_premium_server(self.guild_id)
            if not is_premium:
                await interaction.response.send_message("❌ **Premium Required!** Canvacard is only available for premium servers.", ephemeral=True)
                return
            
            # Get configured channel
            config = await interaction.client.db.get_levelup_config(self.guild_id)
            channel_id = config.get("channel") if config else None
            
            if not channel_id:
                await interaction.response.send_message("❌ **No channel configured!** Please set a channel first using 'Set Test Channel' option.", ephemeral=True)
                return
            
            channel = interaction.guild.get_channel(channel_id)
            if not channel:
                await interaction.response.send_message("❌ **Channel not found!** Please reconfigure the channel using 'Set Test Channel' option.", ephemeral=True)
                return
            
            # Get current user data
            user_data = await interaction.client.db.get_user_xp(self.guild_id, self.user.id)
            current_level = user_data.get("level", 1) if user_data else 1
            new_level = current_level + 1
            new_xp = ((new_level - 1) ** 2) * 100
            
            # Get user rank
            leaderboard = await interaction.client.db.get_leaderboard(self.guild_id, 0)
            user_rank = 1
            for i, user_entry in enumerate(leaderboard):
                if user_entry.get("user_id") == self.user.id:
                    user_rank = i + 1
                    break
            
            # Update database
            await interaction.client.db.set_user_xp(self.guild_id, self.user.id, new_xp, new_level)
            
            # Create fake message for testing
            class FakeMessage:
                def __init__(self, author, guild, channel):
                    self.author = author
                    self.guild = guild
                    self.channel = channel
            
            fake_msg = FakeMessage(self.user, interaction.guild, channel)
            
            # Send canva level-up message with full tracking
            cog = interaction.client.get_cog("LevelUp")
            await cog.send_levelup_message(fake_msg, new_level, new_xp, user_rank, use_canva=True)
            
            await interaction.response.send_message(f"✅ **Canvacard levelup tested in {channel.mention}!** You are now level {new_level} with full XP tracking.", ephemeral=True)
            
        elif value == "channel":
            embed = discord.Embed(
                title="📍 Set Test Channel",
                description="Please select the channel where test messages should be sent.",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=TestChannelSetupView(self.bot, self.guild_id, self.user))

class TestChannelSetupView(discord.ui.View):
    def __init__(self, bot, guild_id, user):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.user = user
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select test channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        
        await interaction.client.db.set_levelup_setting(self.guild_id, "channel", channel.id)
        
        embed = discord.Embed(
            title="✅ Test Channel Set",
            description=f"Test messages will be sent to {channel.mention}\n\nYou can now test both normal and Canvacard level-ups.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await interaction.response.edit_message(embed=embed, view=TestLevelUpView(self.bot, self.guild_id, self.user))

class LevelUpSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose a setting to configure...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set embed title", value="title"),
            discord.SelectOption(label="🖊️ Description", description="Customize level-up message", value="description"),
            discord.SelectOption(label="🎨 Color", description="Choose embed color", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Add image or banner", value="image"),
            discord.SelectOption(label="🦶 Footer", description="Set footer text", value="footer"),
            discord.SelectOption(label="📢 Level Up Channel", description="Select level-up channel", value="channel"),
            discord.SelectOption(label="💾 Save", description="Save all configurations", value="save")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        setting = select.values[0]
        
        if setting == "title":
            embed = discord.Embed(
                title="📝 Set Level Up Title",
                description="Please type the title for level-up embeds in chat.\n\n**Placeholders:**\n`{user}` - User mention\n`{username}` - User's name\n`{level}` - New level\n\n**Example:** `🎉 Congratulations {user}!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_levelup_setting(self.guild_id, "title", msg.content)
                
                embed = discord.Embed(
                    title="✅ Title Set",
                    description=f"Level-up title has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                view = LevelUpSetupView(self.bot, self.guild_id)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "description":
            embed = discord.Embed(
                title="🖊️ Set Level Up Description",
                description="Please type the description for level-up embeds in chat.\n\n**Placeholders:**\n`{user}` - User mention\n`{username}` - User's name\n`{level}` - New level\n`{xp}` - Total XP\n\n**Example:** `{user} just reached level {level}! Keep chatting to earn more XP!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_levelup_setting(self.guild_id, "description", msg.content)
                
                embed = discord.Embed(
                    title="✅ Description Set",
                    description=f"Level-up description has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                view = LevelUpSetupView(self.bot, self.guild_id)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "color":
            embed = discord.Embed(
                title="🎨 Set Level Up Color",
                description="Please type a hex color code in chat.\n\n**Examples:**\n`#ff0000` - Red\n`#00ff00` - Green\n`#0099ff` - Blue\n`#ffd700` - Gold",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                color_input = msg.content.strip()
                
                if re.match(r'^#[0-9A-Fa-f]{6}$', color_input):
                    await interaction.client.db.set_levelup_setting(self.guild_id, "color", color_input)
                    
                    embed = discord.Embed(
                        title="✅ Color Set",
                        description=f"Level-up color has been set to: `{color_input}`",
                        color=int(color_input[1:], 16)
                    )
                    embed = add_dravon_footer(embed)
                    view = LevelUpSetupView(self.bot, self.guild_id)
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid hex color format. Please use format like `#ff0000`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "image":
            embed = discord.Embed(
                title="🖼️ Set Level Up Image",
                description="Please provide an image URL in chat.\n\n**Example:**\n`https://example.com/levelup.png`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_levelup_setting(self.guild_id, "image", msg.content)
                
                embed = discord.Embed(
                    title="✅ Image Set",
                    description=f"Level-up image has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                view = LevelUpSetupView(self.bot, self.guild_id)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "footer":
            embed = discord.Embed(
                title="🦶 Set Level Up Footer",
                description="Please type the footer text in chat.\n\n**Example:** `Keep chatting to gain XP!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_levelup_setting(self.guild_id, "footer", msg.content)
                
                embed = discord.Embed(
                    title="✅ Footer Set",
                    description=f"Level-up footer has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                view = LevelUpSetupView(self.bot, self.guild_id)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "channel":
            embed = discord.Embed(
                title="📢 Set Level Up Channel",
                description="Please select the channel for level-up messages.",
                color=0x7289da
            )
            view = LevelUpChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif setting == "save":
            embed = discord.Embed(
                title="✅ Configuration Saved",
                description="All level-up settings have been saved successfully!\n\nYour level-up system is now ready to use.",
                color=0x00ff00
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)

class LevelUpChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select level-up channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        
        await interaction.client.db.set_levelup_setting(self.guild_id, "channel", channel.id)
        
        embed = discord.Embed(
            title="✅ Channel Set",
            description=f"Level-up messages will be sent to {channel.mention}",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        view = LevelUpSetupView(self.bot, self.guild_id)
        await interaction.response.edit_message(embed=embed, view=view)

class LeaderboardView(discord.ui.View):
    def __init__(self, bot, guild_id, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.page = page
    
    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
            embed = await self.create_leaderboard_embed(interaction.guild)
            view = LeaderboardView(self.bot, self.guild_id, self.page)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("You're already on the first page!", ephemeral=True)
    
    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        leaderboard = await interaction.client.db.get_leaderboard(self.guild_id, self.page + 1)
        if leaderboard:
            self.page += 1
            embed = await self.create_leaderboard_embed(interaction.guild)
            view = LeaderboardView(self.bot, self.guild_id, self.page)
            await interaction.response.edit_message(embed=embed, view=view)
        else:
            await interaction.response.send_message("No more pages available!", ephemeral=True)
    
    async def create_leaderboard_embed(self, guild):
        leaderboard = await self.bot.db.get_leaderboard(self.guild_id, self.page)
        
        embed = discord.Embed(
            title="🏆 Level Leaderboard",
            description="Here are the most active members climbing the ranks!",
            color=0xffd700
        )
        
        if leaderboard:
            leaderboard_text = ""
            start_rank = self.page * 10 + 1
            
            for i, user_data in enumerate(leaderboard):
                rank = start_rank + i
                user_id = user_data.get("user_id")
                level = user_data.get("level", 1)
                xp = user_data.get("xp", 0)
                
                if rank == 1:
                    emoji = "🥇"
                elif rank == 2:
                    emoji = "🥈"
                elif rank == 3:
                    emoji = "🥉"
                else:
                    emoji = f"{rank}."
                
                leaderboard_text += f"{emoji} <@{user_id}> – Level {level} | {xp:,} XP\n"
            
            embed.add_field(
                name=f"Page {self.page + 1}",
                value=leaderboard_text,
                inline=False
            )
        else:
            embed.add_field(
                name="No Data",
                value="No users found on this page.",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        return embed

class LevelUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_cooldowns = {}
    
    def calculate_level(self, xp):
        """Calculate level from XP"""
        return int((xp / 100) ** 0.5) + 1
    
    def xp_for_level(self, level):
        """Calculate XP needed for a specific level"""
        return ((level - 1) ** 2) * 100
    
    def replace_placeholders(self, text, user, level, xp):
        """Replace placeholders in text"""
        if not text:
            return text
        
        replacements = {
            "{user}": user.mention,
            "{username}": user.display_name,
            "{level}": str(level),
            "{xp}": str(xp)
        }
        
        for placeholder, replacement in replacements.items():
            text = text.replace(placeholder, replacement)
        
        return text
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return
        
        # Cooldown check (60 seconds)
        user_key = f"{message.guild.id}_{message.author.id}"
        current_time = time.time()
        
        if user_key in self.user_cooldowns:
            if current_time - self.user_cooldowns[user_key] < 60:
                return
        
        self.user_cooldowns[user_key] = current_time
        
        # Add XP (15-25 per message)
        xp_gain = random.randint(15, 25)
        user_data = await self.bot.db.get_user_xp(message.guild.id, message.author.id)
        
        if not user_data:
            new_xp = xp_gain
            old_level = 1
        else:
            new_xp = user_data.get("xp", 0) + xp_gain
            old_level = user_data.get("level", 1)
        
        new_level = self.calculate_level(new_xp)
        
        # Update database with rank calculation
        await self.bot.db.set_user_xp(message.guild.id, message.author.id, new_xp, new_level)
        
        # Check if user leveled up
        if new_level > old_level:
            # Get user's rank in the server
            leaderboard = await self.bot.db.get_leaderboard(message.guild.id, 0)
            user_rank = 1
            for i, user_entry in enumerate(leaderboard):
                if user_entry.get("user_id") == message.author.id:
                    user_rank = i + 1
                    break
            
            await self.send_levelup_message(message, new_level, new_xp, user_rank)
    
    async def create_canva_card(self, user, level, xp, rank=1):
        """Create a Canvacard using Python PIL"""
        if not CANVA_AVAILABLE:
            return None
            
        try:
            WIDTH, HEIGHT = 800, 350
            
            # Get user banner or avatar for background
            background_url = None
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f'https://discord.com/api/v10/users/{user.id}', 
                                         headers={'Authorization': f'Bot {self.bot.token}'}) as resp:
                        if resp.status == 200:
                            user_data = await resp.json()
                            if user_data.get('banner'):
                                background_url = f"https://cdn.discordapp.com/banners/{user.id}/{user_data['banner']}.png?size=1024"
            except:
                pass
            
            # If no banner, use avatar
            if not background_url:
                background_url = str(user.display_avatar.with_size(1024).url)
            
            # Create base image
            img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
            
            # Create blurred background
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(background_url) as resp:
                        bg_bytes = await resp.read()
                
                bg_img = Image.open(io.BytesIO(bg_bytes)).convert('RGBA')
                bg_ratio = max(WIDTH / bg_img.width, HEIGHT / bg_img.height)
                new_width = int(bg_img.width * bg_ratio)
                new_height = int(bg_img.height * bg_ratio)
                bg_img = bg_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                left = (new_width - WIDTH) // 2
                top = (new_height - HEIGHT) // 2
                bg_img = bg_img.crop((left, top, left + WIDTH, top + HEIGHT))
                bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=8))
                
                img.paste(bg_img, (0, 0))
                
                # Dark overlay
                overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 150))
                img = Image.alpha_composite(img, overlay)
                
            except:
                # Fallback gradient
                for y in range(HEIGHT):
                    r = int(35 + (y / HEIGHT) * 20)
                    g = int(39 + (y / HEIGHT) * 25) 
                    b = int(42 + (y / HEIGHT) * 30)
                    for x in range(WIDTH):
                        img.putpixel((x, y), (r, g, b, 255))
            
            draw = ImageDraw.Draw(img)
            
            # Get fonts
            try:
                font_name = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
                font_info = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
            except:
                font_name = font_info = font_small = font_time = ImageFont.load_default()
            
            # Get user avatar
            async with aiohttp.ClientSession() as session:
                async with session.get(str(user.display_avatar.with_size(256).url)) as resp:
                    avatar_bytes = await resp.read()
            
            # Process avatar
            avatar = Image.open(io.BytesIO(avatar_bytes)).convert('RGBA')
            avatar = avatar.resize((140, 140), Image.Resampling.LANCZOS)
            
            # Circular mask
            mask = Image.new('L', (140, 140), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 140, 140), fill=255)
            avatar.putalpha(mask)
            
            # Paste avatar
            img.paste(avatar, (30, 71), avatar)
            
            # User status indicator
            status_colors = {
                'online': (67, 181, 129),
                'idle': (250, 166, 26), 
                'dnd': (240, 71, 71),
                'offline': (116, 127, 141)
            }
            status = getattr(user, 'status', 'offline')
            status_color = status_colors.get(str(status), status_colors['offline'])
            draw.ellipse((155, 195, 175, 215), fill=status_color, outline=(255, 255, 255), width=4)
            
            # Username
            username = user.display_name or user.name
            if len(username) > 20:
                username = username[:17] + "..."
            draw.text((200, 75), username, fill=(255, 255, 255), font=font_name)
            
            # XP Progress bar
            xp_needed = 100 + level * 25
            percent = min(xp / xp_needed, 1)
            
            bar_x, bar_y = 200, 150
            bar_width, bar_height = 550, 32
            
            # Progress bar background
            draw.rounded_rectangle([(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)],
                                 radius=16, fill=(50, 50, 50, 200))
            
            # Green progress fill
            progress_width = int(bar_width * percent)
            if progress_width > 16:
                for i in range(progress_width):
                    ratio = i / bar_width
                    r = int(34 + ratio * 20)    # Green gradient
                    g = int(197 - ratio * 30)   
                    b = int(94 + ratio * 20)    
                    
                    draw.rectangle([(bar_x + i, bar_y + 3), (bar_x + i + 1, bar_y + bar_height - 3)],
                                 fill=(r, g, b, 255))
            
            # XP and Rank info boxes
            info_box_width = 120
            info_box_height = 25
            info_x = WIDTH - info_box_width - 15
            info_y = HEIGHT - info_box_height - 50
            
            # XP box
            draw.rounded_rectangle([(info_x, info_y), (info_x + info_box_width, info_y + info_box_height)],
                                 radius=12, fill=(0, 0, 0, 120))
            
            xp_text = f"{xp} / {xp_needed} XP"
            xp_bbox = draw.textbbox((0, 0), xp_text, font=font_small)
            xp_text_x = info_x + (info_box_width - (xp_bbox[2] - xp_bbox[0])) // 2
            draw.text((xp_text_x, info_y + 6), xp_text, fill=(255, 255, 255), font=font_small)
            
            # Rank box
            rank_y = info_y - 35
            draw.rounded_rectangle([(info_x, rank_y), (info_x + info_box_width, rank_y + info_box_height)],
                                 radius=12, fill=(0, 0, 0, 120))
            
            rank_text = f"RANK #{rank} • LVL {level}"
            rank_bbox = draw.textbbox((0, 0), rank_text, font=font_small)
            rank_text_x = info_x + (info_box_width - (rank_bbox[2] - rank_bbox[0])) // 2
            draw.text((rank_text_x, rank_y + 6), rank_text, fill=(255, 255, 255), font=font_small)
            
            # Time box
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            
            time_box_width = 80
            time_box_height = 25
            time_x = WIDTH - time_box_width - 15
            time_y = HEIGHT - time_box_height - 15
            
            draw.rounded_rectangle([(time_x, time_y), (time_x + time_box_width, time_y + time_box_height)],
                                 radius=12, fill=(0, 0, 0, 120))
            
            time_bbox = draw.textbbox((0, 0), current_time, font=font_time)
            time_text_x = time_x + (time_box_width - (time_bbox[2] - time_bbox[0])) // 2
            draw.text((time_text_x, time_y + 6), current_time, fill=(255, 255, 255), font=font_time)
            
            # Convert to bytes
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error creating canva card: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def send_levelup_message(self, message, level, xp, rank=1, use_canva=None):
        """Send level-up message with full XP tracking"""
        config = await self.bot.db.get_levelup_config(message.guild.id)
        
        if not config:
            return
        
        # Check if canva should be used
        if use_canva is None:
            canva_config = await self.bot.db.get_canva_config(message.guild.id)
            use_canva = canva_config.get("enabled", False) if canva_config else False
        
        # Get channel
        channel_id = config.get("channel")
        if channel_id:
            channel = message.guild.get_channel(channel_id)
            if not channel:
                channel = message.channel
        else:
            channel = message.channel
        
        if use_canva and CANVA_AVAILABLE:
            # Create and send canva card with full tracking
            card_bytes = await self.create_canva_card(message.author, level, xp, rank)
            if card_bytes:
                file = discord.File(io.BytesIO(card_bytes), filename="levelup.png")
                # Send congratulations message in chat format
                congrats_msg = f"🎉 **{message.author.display_name}** just leveled up to **Level {level}**! Keep chatting to earn more XP! 🚀"
                await channel.send(congrats_msg, file=file)
                return
        
        # Enhanced normal embed with full XP tracking
        title = config.get("title", "🎉 Level Up!")
        description = config.get("description", "{user} just reached level {level}!")
        color = config.get("color", "#00ff00")
        image = config.get("image")
        footer = config.get("footer", "Keep chatting to gain XP!")
        
        # Calculate XP progress
        xp_needed = 100 + level * 25
        xp_for_current = ((level - 1) ** 2) * 100
        xp_progress = xp - xp_for_current
        xp_required = xp_needed - xp_for_current
        
        # Enhanced placeholders with full tracking
        enhanced_replacements = {
            "{user}": message.author.mention,
            "{username}": message.author.display_name,
            "{level}": str(level),
            "{xp}": str(xp),
            "{rank}": str(rank),
            "{xp_progress}": str(xp_progress),
            "{xp_required}": str(xp_required),
            "{xp_needed}": str(xp_needed)
        }
        
        # Replace placeholders
        for placeholder, replacement in enhanced_replacements.items():
            title = title.replace(placeholder, replacement)
            description = description.replace(placeholder, replacement)
            footer = footer.replace(placeholder, replacement)
        
        # Create enhanced embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color[1:], 16) if color.startswith('#') else 0x00ff00
        )
        
        # Add XP tracking fields
        embed.add_field(
            name="📊 Progress",
            value=f"**Level:** {level}\n**Rank:** #{rank}\n**Total XP:** {xp:,}",
            inline=True
        )
        
        embed.add_field(
            name="🎯 Next Level",
            value=f"**Progress:** {xp_progress}/{xp_required} XP\n**Needed:** {xp_required - xp_progress} XP\n**Percentage:** {(xp_progress/xp_required)*100:.1f}%",
            inline=True
        )
        
        if image:
            embed.set_image(url=image)
        
        if footer:
            embed.set_footer(text=footer)
        
        await channel.send(embed=embed)
    
    @commands.hybrid_group(name="levelup")
    async def levelup_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use levelup commands like `levelup setup`, `levelup config`, etc.")
    
    @levelup_group.command(name="setup")
    async def levelup_setup(self, ctx):
        """Setup the level up system"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🆙 Level Up System Setup",
            description="Customize your server's Level Up system!\nWith this setup, you can design the message style, embed look, and channel where level-up messages will appear.\nUse the dropdown menu below to configure each setting.",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        
        view = LevelUpSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @levelup_group.command(name="config")
    async def levelup_config(self, ctx):
        """Display current level up configuration"""
        config = await self.bot.db.get_levelup_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="⚙️ Level Up Config",
            color=0x7289da
        )
        
        if config:
            title = config.get("title", "Not set")
            description = config.get("description", "Not set")
            color = config.get("color", "Not set")
            image = config.get("image", "None")
            footer = config.get("footer", "Not set")
            channel_id = config.get("channel")
            
            channel_text = f"<#{channel_id}>" if channel_id else "Not set"
            
            embed.add_field(name="Title", value=title, inline=False)
            embed.add_field(name="Description", value=description, inline=False)
            embed.add_field(name="Color", value=color, inline=True)
            embed.add_field(name="Image", value=image, inline=True)
            embed.add_field(name="Footer", value=footer, inline=False)
            embed.add_field(name="Level Up Channel", value=channel_text, inline=False)
        else:
            embed.add_field(
                name="No Configuration",
                value="Level up system is not configured. Use `/levelup setup` to get started.",
                inline=False
            )
        
        embed.set_footer(text="Use /levelup setup to update settings.")
        await ctx.send(embed=embed)
    
    @levelup_group.command(name="reset")
    async def levelup_reset(self, ctx):
        """Reset the level up system"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        await self.bot.db.reset_levelup_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="🔄 Reset Complete",
            description="All Level Up settings have been restored to default.\nUse /levelup setup to configure again.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    @levelup_group.command(name="leaderboard")
    async def levelup_leaderboard(self, ctx):
        """Show the server leaderboard"""
        view = LeaderboardView(self.bot, ctx.guild.id)
        embed = await view.create_leaderboard_embed(ctx.guild)
        
        await ctx.send(embed=embed, view=view)
    
    @levelup_group.command(name="rewards")
    async def levelup_rewards(self, ctx):
        """Manage level rewards (coming soon)"""
        embed = discord.Embed(
            title="🎁 Level Rewards",
            description="Level rewards system is coming soon!\n\nThis will allow you to:\n• Set role rewards for specific levels\n• Manage reward configurations\n• View all active rewards",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed)
    
    @levelup_group.command(name="canva")
    async def levelup_canva(self, ctx):
        """Setup Canvacard level-up system (Premium only)"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        # Check premium status
        is_premium = await self.bot.db.is_premium_server(ctx.guild.id)
        if not is_premium:
            embed = discord.Embed(
                title="🔒 Premium Feature",
                description="**Canvacard is a premium feature!**\n\nUpgrade to premium to unlock:\n• Beautiful visual level-up cards\n• Custom rank card designs\n• User avatar integration\n• Advanced styling options",
                color=0xffd700
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        if not CANVA_AVAILABLE:
            embed = discord.Embed(
                title="❌ Canvacard Unavailable",
                description="**PIL library not installed**\n\nTo use Canvacard features, install the required dependencies:\n```\npip install Pillow\n```",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # No need for Node.js service check - using Python PIL
        
        # Create preview card
        card_bytes = await self.create_canva_card(ctx.author, 5, 750, 12)
        
        embed = discord.Embed(
            title="🎨 Canvacard Level System",
            description="**Preview of beautiful visual level-up cards**\n\nThis creates stunning level-up notifications with user avatars, XP progress bars, and custom styling.",
            color=0x7289da
        )
        
        if card_bytes:
            file = discord.File(io.BytesIO(card_bytes), filename="canva-preview.png")
            embed.set_image(url="attachment://canva-preview.png")
            embed = add_dravon_footer(embed)
            
            view = CanvaSetupView(self.bot, ctx.guild.id)
            await ctx.send(embed=embed, file=file, view=view)
        else:
            embed = discord.Embed(
                title="❌ Failed to create preview card",
                description="**Troubleshooting:**\n• Make sure Node.js Canvacard service is running\n• Check if port 3007 is available\n• Verify all dependencies are installed",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @levelup_group.command(name="test")
    async def levelup_test(self, ctx):
        """Test both normal and canvacard level-up systems"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🧪 Test Level-Up System",
            description="Choose which type of level-up message to test:\n\n📝 **Normal:** Standard embed level-up message\n🎨 **Canvacard:** Beautiful visual level-up card (Premium only)",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        
        view = TestLevelUpView(self.bot, ctx.guild.id, ctx.author)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(LevelUp(bot))