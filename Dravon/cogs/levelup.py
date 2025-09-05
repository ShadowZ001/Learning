import discord
from discord.ext import commands
import re
import random
import time
from utils.embed_utils import add_dravon_footer

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
            view = LevelUpSetupView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)

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
        
        # Update database
        await self.bot.db.set_user_xp(message.guild.id, message.author.id, new_xp, new_level)
        
        # Check if user leveled up
        if new_level > old_level:
            await self.send_levelup_message(message, new_level, new_xp)
    
    async def send_levelup_message(self, message, level, xp):
        """Send level-up message"""
        config = await self.bot.db.get_levelup_config(message.guild.id)
        
        if not config:
            return
        
        # Get settings
        title = config.get("title", "🎉 Level Up!")
        description = config.get("description", "{user} just reached level {level}!")
        color = config.get("color", "#00ff00")
        image = config.get("image")
        footer = config.get("footer", "Keep chatting to gain XP!")
        channel_id = config.get("channel")
        
        # Replace placeholders
        title = self.replace_placeholders(title, message.author, level, xp)
        description = self.replace_placeholders(description, message.author, level, xp)
        footer = self.replace_placeholders(footer, message.author, level, xp)
        
        # Create embed
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color[1:], 16) if color.startswith('#') else 0x00ff00
        )
        
        if image:
            embed.set_image(url=image)
        
        if footer:
            embed.set_footer(text=footer)
        
        # Send to configured channel or current channel
        if channel_id:
            channel = message.guild.get_channel(channel_id)
            if channel:
                await channel.send(embed=embed)
            else:
                await message.channel.send(embed=embed)
        else:
            await message.channel.send(embed=embed)
    
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
    
    @levelup_group.command(name="test")
    async def levelup_test(self, ctx):
        """Test the level-up system by simulating a level up"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        # Get current user data or create new
        user_data = await self.bot.db.get_user_xp(ctx.guild.id, ctx.author.id)
        
        if not user_data:
            current_xp = 0
            current_level = 1
        else:
            current_xp = user_data.get("xp", 0)
            current_level = user_data.get("level", 1)
        
        # Simulate level up
        new_level = current_level + 1
        new_xp = self.xp_for_level(new_level)
        
        # Update database
        await self.bot.db.set_user_xp(ctx.guild.id, ctx.author.id, new_xp, new_level)
        
        # Send test level-up message
        await self.send_levelup_message(ctx.message, new_level, new_xp)
        
        # Send confirmation
        embed = discord.Embed(
            title="✅ Level Up Test Complete",
            description=f"Successfully tested level-up system!\n\n**Your Stats:**\n• **Level:** {current_level} → {new_level}\n• **XP:** {current_xp:,} → {new_xp:,}\n\nThe level-up message was sent using your current configuration.",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        
        await ctx.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(LevelUp(bot))