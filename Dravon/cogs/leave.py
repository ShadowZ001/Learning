import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio
from datetime import datetime

class LeaveSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose a leave setting to configure...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set the embed title for leave messages", value="title"),
            discord.SelectOption(label="📄 Description", description="Set the embed description", value="description"),
            discord.SelectOption(label="🎨 Color", description="Set the embed color (hex code)", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Set an image to display in the embed", value="image"),
            discord.SelectOption(label="📑 Footer", description="Set the footer text", value="footer"),
            discord.SelectOption(label="📢 Leave Channel", description="Select the channel for leave messages", value="channel"),
            discord.SelectOption(label="📬 Toggle DM Message", description="Enable/disable DMs to leaving members", value="dm_toggle")
        ]
    )
    async def leave_setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        setting = select.values[0]
        
        if setting == "title":
            embed = discord.Embed(
                title="📝 Set Leave Title",
                description="Please type the title for leave messages in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's username\n`{server}` - Server name\n`{member_count}` - Current member count\n`{joined_at}` - When user joined\n\n**Example:** `Goodbye, {user}!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_leave_setting(self.guild_id, "title", msg.content)
                
                embed = discord.Embed(
                    title="✅ Leave Title Set",
                    description=f"Leave title has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "leave")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "description":
            embed = discord.Embed(
                title="📄 Set Leave Description",
                description="Please type the description for leave messages in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's username\n`{server}` - Server name\n`{member_count}` - Current member count\n`{joined_at}` - When user joined\n\n**Example:** `{user} just left {server}. We now have {member_count} members.`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_leave_setting(self.guild_id, "description", msg.content)
                
                embed = discord.Embed(
                    title="✅ Leave Description Set",
                    description=f"Leave description has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "leave")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "color":
            embed = discord.Embed(
                title="🎨 Set Leave Color",
                description="Please type a hex color code in chat.\n\n**Examples:**\n`#ff0000` - Red\n`#00ff00` - Green\n`#0099ff` - Blue\n`#ff69b4` - Pink",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                color_input = msg.content.strip()
                
                if re.match(r'^#[0-9A-Fa-f]{6}$', color_input):
                    await interaction.client.db.set_leave_setting(self.guild_id, "color", color_input)
                    
                    embed = discord.Embed(
                        title="✅ Leave Color Set",
                        description=f"Leave color has been set to: `{color_input}`",
                        color=int(color_input[1:], 16)
                    )
                    from cogs.boost import BackToSetupView
                    view = BackToSetupView(self.bot, self.guild_id, "leave")
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid hex color format. Please use format like `#ff0000`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "image":
            embed = discord.Embed(
                title="🖼️ Set Leave Image",
                description="Please provide an image URL in chat.\n\n**Example:**\n`https://example.com/image.png`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_leave_setting(self.guild_id, "image", msg.content)
                
                embed = discord.Embed(
                    title="✅ Leave Image Set",
                    description=f"Leave image has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "leave")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "footer":
            embed = discord.Embed(
                title="📑 Set Leave Footer",
                description="Please type the footer text in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's username\n`{server}` - Server name\n`{member_count}` - Current member count\n`{joined_at}` - When user joined\n\n**Example:** `We'll miss you!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_leave_setting(self.guild_id, "footer", msg.content)
                
                embed = discord.Embed(
                    title="✅ Leave Footer Set",
                    description=f"Leave footer has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "leave")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "channel":
            embed = discord.Embed(
                title="📢 Set Leave Channel",
                description="Please select the channel for leave messages.",
                color=0x7289da
            )
            view = LeaveChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif setting == "dm_toggle":
            config = await interaction.client.db.get_leave_config(self.guild_id)
            current_dm = config.get("dm_enabled", False) if config else False
            new_dm = not current_dm
            
            await interaction.client.db.set_leave_setting(self.guild_id, "dm_enabled", new_dm)
            
            status = "Enabled" if new_dm else "Disabled"
            embed = discord.Embed(
                title="📬 DM Message Toggle",
                description=f"DM messages to leaving members: **{status}**",
                color=0x00ff00 if new_dm else 0xff0000
            )
            from cogs.boost import BackToSetupView
            view = BackToSetupView(self.bot, self.guild_id, "leave")
            await interaction.response.edit_message(embed=embed, view=view)

class LeaveChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select leave channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        await interaction.response.defer()
        
        channel = select.values[0]
        await interaction.client.db.set_leave_setting(self.guild_id, "channel", channel.id)
        
        embed = discord.Embed(
            title="✅ Leave Channel Set",
            description=f"Leave messages will be sent to {channel.mention}",
            color=0x00ff00
        )
        from cogs.boost import BackToSetupView
        view = BackToSetupView(self.bot, self.guild_id, "leave")
        await interaction.edit_original_response(embed=embed, view=view)

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def replace_variables(self, text: str, user: discord.Member, guild: discord.Guild) -> str:
        """Replace leave variables in text"""
        if not text:
            return text
        
        joined_at = user.joined_at.strftime("%B %d, %Y") if user.joined_at else "Unknown"
        
        replacements = {
            "{user}": user.mention,
            "{username}": user.display_name,
            "{server}": guild.name,
            "{member_count}": str(guild.member_count),
            "{joined_at}": joined_at
        }
        
        for var, replacement in replacements.items():
            text = text.replace(var, replacement)
        
        return text
    
    @commands.hybrid_group(name="leave")
    async def leave_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use leave commands like `leave setup`, `leave config`, etc.")
    
    @leave_group.command(name="setup")
    async def leave_setup(self, ctx):
        """Configure server leave messages"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="👋 Leave Setup",
            description="Configure goodbye messages for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Enter your custom text/value\n**Step 3:** Test with `/leave test`",
            color=0x7289da
        )
        
        view = LeaveSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @leave_group.command(name="config")
    async def leave_config(self, ctx):
        """Display current leave configuration"""
        config = await self.bot.db.get_leave_config(ctx.guild.id)
        
        if not config:
            embed = discord.Embed(
                title="📜 Leave Configuration",
                description="No leave configuration found. Use `/leave setup` to configure.",
                color=0x7289da
            )
        else:
            title = config.get("title", "Not set")
            description = config.get("description", "Not set")
            color = config.get("color", "#7289da")
            image = config.get("image", "Not set")
            footer = config.get("footer", "Not set")
            channel_id = config.get("channel")
            dm_enabled = config.get("dm_enabled", False)
            
            channel_mention = f"<#{channel_id}>" if channel_id else "Not set"
            dm_status = "Enabled" if dm_enabled else "Disabled"
            
            embed = discord.Embed(
                title="📜 Leave Configuration",
                description=f"**Title:** {title}\n**Description:** {description}\n**Color:** {color}\n**Image:** {image}\n**Footer:** {footer}\n**Leave Channel:** {channel_mention}\n**DM Message:** {dm_status}",
                color=int(color[1:], 16) if color.startswith('#') else 0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @leave_group.command(name="reset")
    async def leave_reset(self, ctx):
        """Reset leave configuration to default"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        await self.bot.db.reset_leave_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ Leave System Reset",
            description="Leave system has been reset to default settings.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @leave_group.command(name="test")
    async def leave_test(self, ctx):
        """Send a test leave message"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        config = await self.bot.db.get_leave_config(ctx.guild.id)
        
        if not config or not config.get("channel"):
            await ctx.send("Please configure the leave channel first using `/leave setup`.")
            return
        
        channel = self.bot.get_channel(config["channel"])
        if not channel:
            await ctx.send("Configured leave channel not found.")
            return
        
        # Create test leave embed
        title = self.replace_variables(config.get("title", "Goodbye!"), ctx.author, ctx.guild)
        description = self.replace_variables(config.get("description", "A member has left the server."), ctx.author, ctx.guild)
        footer = self.replace_variables(config.get("footer", "We'll miss you!"), ctx.author, ctx.guild)
        color = config.get("color", "#7289da")
        image = config.get("image")
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color[1:], 16) if color.startswith('#') else 0x7289da
        )
        
        if image:
            embed.set_image(url=image)
        
        if footer:
            embed.set_footer(text=footer)
        
        await channel.send("🧪 **Test Leave Message:**", embed=embed)
        
        # Test DM if enabled
        if config.get("dm_enabled", False):
            try:
                dm_message = f"Goodbye from {ctx.guild.name}, we hope to see you again!"
                await ctx.author.send(f"🧪 **Test Leave DM:** {dm_message}")
                await ctx.send(f"✅ Test leave message sent to {channel.mention} and test DM sent to you.")
            except:
                await ctx.send(f"✅ Test leave message sent to {channel.mention}. Could not send test DM.")
        else:
            await ctx.send(f"✅ Test leave message sent to {channel.mention}")
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Listen for member leave events"""
        config = await self.bot.db.get_leave_config(member.guild.id)
        
        if not config or not config.get("channel"):
            return
        
        channel = self.bot.get_channel(config["channel"])
        if not channel:
            return
        
        # Create leave embed
        title = self.replace_variables(config.get("title", "Goodbye!"), member, member.guild)
        description = self.replace_variables(config.get("description", "A member has left the server."), member, member.guild)
        footer = self.replace_variables(config.get("footer", "We'll miss you!"), member, member.guild)
        color = config.get("color", "#7289da")
        image = config.get("image")
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color[1:], 16) if color.startswith('#') else 0x7289da
        )
        
        if image:
            embed.set_image(url=image)
        
        if footer:
            embed.set_footer(text=footer)
        
        await channel.send(embed=embed)
        
        # Send DM if enabled
        if config.get("dm_enabled", False):
            try:
                dm_message = f"Goodbye from {member.guild.name}, we hope to see you again!"
                await member.send(dm_message)
            except:
                pass  # User has DMs disabled or left before DM could be sent

async def setup(bot):
    await bot.add_cog(Leave(bot))