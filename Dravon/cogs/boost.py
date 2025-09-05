import discord
from discord.ext import commands
from discord import app_commands
import re

class BackToSetupView(discord.ui.View):
    def __init__(self, bot, guild_id, setup_type):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.setup_type = setup_type
    
    @discord.ui.button(label="🔙 Back to Setup", style=discord.ButtonStyle.secondary)
    async def back_to_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.setup_type == "boost":
            embed = discord.Embed(
                title="✨ Boost Setup",
                description="Configure boost messages for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Enter your custom text/value\n**Step 3:** Test with `/boost test`",
                color=0x7289da
            )
            view = BoostSetupView(self.bot, self.guild_id)
        elif self.setup_type == "leave":
            embed = discord.Embed(
                title="👋 Leave Setup",
                description="Configure goodbye messages for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Enter your custom text/value\n**Step 3:** Test with `/leave test`",
                color=0x7289da
            )
            from cogs.leave import LeaveSetupView
            view = LeaveSetupView(self.bot, self.guild_id)
        elif self.setup_type == "ticket":
            embed = discord.Embed(
                title="🎟️ Ticket Setup",
                description="Create a fully customized ticket panel for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Configure your ticket system\n**Step 3:** Send panel to a channel",
                color=0x7289da
            )
            from cogs.ticket import TicketSetupView
            view = TicketSetupView(self.bot, self.guild_id)
        
        await interaction.response.edit_message(embed=embed, view=view)

class BoostSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose a boost setting to configure...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set the embed title for boost messages", value="title"),
            discord.SelectOption(label="📄 Description", description="Set the embed description", value="description"),
            discord.SelectOption(label="🎨 Color", description="Set the embed color (hex code)", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Set an image to display in the embed", value="image"),
            discord.SelectOption(label="📑 Footer", description="Set the footer text", value="footer"),
            discord.SelectOption(label="📢 Booster Channel", description="Select the channel for boost messages", value="channel")
        ]
    )
    async def boost_setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        setting = select.values[0]
        
        if setting == "title":
            embed = discord.Embed(
                title="📝 Set Boost Title",
                description="Please type the title for boost messages in chat.\n\n**Variables:**\n`{user}` - Mentions the booster\n`{server}` - Server name\n`{server_level}` - Server boost level\n`{boost_count}` - Total boosts\n\n**Example:** `Thanks for Boosting, {user}!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_boost_setting(self.guild_id, "title", msg.content)
                
                embed = discord.Embed(
                    title="✅ Boost Title Set",
                    description=f"Boost title has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = BackToSetupView(self.bot, self.guild_id, "boost")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "description":
            embed = discord.Embed(
                title="📄 Set Boost Description",
                description="Please type the description for boost messages in chat.\n\n**Variables:**\n`{user}` - Mentions the booster\n`{server}` - Server name\n`{server_level}` - Server boost level\n`{boost_count}` - Total boosts\n\n**Example:** `Our server is now level {server_level} thanks to your boost!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_boost_setting(self.guild_id, "description", msg.content)
                
                embed = discord.Embed(
                    title="✅ Boost Description Set",
                    description=f"Boost description has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = BackToSetupView(self.bot, self.guild_id, "boost")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "color":
            embed = discord.Embed(
                title="🎨 Set Boost Color",
                description="Please type a hex color code in chat.\n\n**Examples:**\n`#ff0000` - Red\n`#00ff00` - Green\n`#0099ff` - Blue\n`#ff69b4` - Pink",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                color_input = msg.content.strip()
                
                # Validate hex color
                if re.match(r'^#[0-9A-Fa-f]{6}$', color_input):
                    await interaction.client.db.set_boost_setting(self.guild_id, "color", color_input)
                    
                    embed = discord.Embed(
                        title="✅ Boost Color Set",
                        description=f"Boost color has been set to: `{color_input}`",
                        color=int(color_input[1:], 16)
                    )
                    view = BackToSetupView(self.bot, self.guild_id, "boost")
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid hex color format. Please use format like `#ff0000`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "image":
            embed = discord.Embed(
                title="🖼️ Set Boost Image",
                description="Please provide an image URL in chat.\n\n**Example:**\n`https://example.com/image.png`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_boost_setting(self.guild_id, "image", msg.content)
                
                embed = discord.Embed(
                    title="✅ Boost Image Set",
                    description=f"Boost image has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = BackToSetupView(self.bot, self.guild_id, "boost")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "footer":
            embed = discord.Embed(
                title="📑 Set Boost Footer",
                description="Please type the footer text in chat.\n\n**Variables:**\n`{user}` - Mentions the booster\n`{server}` - Server name\n`{server_level}` - Server boost level\n`{boost_count}` - Total boosts\n\n**Example:** `Boosted by {user}`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_boost_setting(self.guild_id, "footer", msg.content)
                
                embed = discord.Embed(
                    title="✅ Boost Footer Set",
                    description=f"Boost footer has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = BackToSetupView(self.bot, self.guild_id, "boost")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "channel":
            embed = discord.Embed(
                title="📢 Set Booster Channel",
                description="Please select the channel for boost messages.",
                color=0x7289da
            )
            view = ChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)

class ChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select boost channel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        await interaction.response.defer()
        
        channel = select.values[0]
        await interaction.client.db.set_boost_setting(self.guild_id, "channel", channel.id)
        
        embed = discord.Embed(
            title="✅ Booster Channel Set",
            description=f"Boost messages will be sent to {channel.mention}",
            color=0x00ff00
        )
        view = BackToSetupView(self.bot, self.guild_id, "boost")
        await interaction.edit_original_response(embed=embed, view=view)

class Boost(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def replace_variables(self, text: str, user: discord.Member, guild: discord.Guild) -> str:
        """Replace boost variables in text"""
        if not text:
            return text
        
        replacements = {
            "{user}": user.mention,
            "{server}": guild.name,
            "{server_level}": str(guild.premium_tier),
            "{boost_count}": str(guild.premium_subscription_count or 0)
        }
        
        for var, replacement in replacements.items():
            text = text.replace(var, replacement)
        
        return text
    
    @commands.hybrid_group(name="boost")
    async def boost_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use boost commands like `boost setup`, `boost config`, etc.")
    
    @boost_group.command(name="setup")
    async def boost_setup(self, ctx):
        """Configure server boost messages"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="✨ Boost Setup",
            description="Configure boost messages for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Enter your custom text/value\n**Step 3:** Test with `/boost test`",
            color=0x7289da
        )
        
        view = BoostSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @boost_group.command(name="config")
    async def boost_config(self, ctx):
        """Display current boost configuration"""
        config = await self.bot.db.get_boost_config(ctx.guild.id)
        
        if not config:
            embed = discord.Embed(
                title="🔧 Boost Configuration",
                description="No boost configuration found. Use `/boost setup` to configure.",
                color=0x7289da
            )
        else:
            title = config.get("title", "Not set")
            description = config.get("description", "Not set")
            color = config.get("color", "#7289da")
            image = config.get("image", "Not set")
            footer = config.get("footer", "Not set")
            channel_id = config.get("channel")
            
            channel_mention = f"<#{channel_id}>" if channel_id else "Not set"
            
            embed = discord.Embed(
                title="🔧 Boost Configuration",
                description=f"**Title:** {title}\n**Description:** {description}\n**Color:** {color}\n**Image:** {image}\n**Footer:** {footer}\n**Channel:** {channel_mention}",
                color=int(color[1:], 16) if color.startswith('#') else 0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @boost_group.command(name="reset")
    async def boost_reset(self, ctx):
        """Reset boost configuration to default"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        await self.bot.db.reset_boost_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ Boost System Reset",
            description="Boost system has been reset to default settings.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @boost_group.command(name="test")
    async def boost_test(self, ctx):
        """Send a test boost message"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        config = await self.bot.db.get_boost_config(ctx.guild.id)
        
        if not config or not config.get("channel"):
            await ctx.send("Please configure the boost channel first using `/boost setup`.")
            return
        
        channel = self.bot.get_channel(config["channel"])
        if not channel:
            await ctx.send("Configured boost channel not found.")
            return
        
        # Create test boost embed
        title = self.replace_variables(config.get("title", "Thanks for Boosting!"), ctx.author, ctx.guild)
        description = self.replace_variables(config.get("description", "Thank you for boosting our server!"), ctx.author, ctx.guild)
        footer = self.replace_variables(config.get("footer", "Boosted by {user}"), ctx.author, ctx.guild)
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
        
        await channel.send("🧪 **Test Boost Message:**", embed=embed)
        await ctx.send(f"✅ Test boost message sent to {channel.mention}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Listen for boost events"""
        # Check if user started boosting
        if not before.premium_since and after.premium_since:
            config = await self.bot.db.get_boost_config(after.guild.id)
            
            if not config or not config.get("channel"):
                return
            
            channel = self.bot.get_channel(config["channel"])
            if not channel:
                return
            
            # Create boost embed
            title = self.replace_variables(config.get("title", "Thanks for Boosting!"), after, after.guild)
            description = self.replace_variables(config.get("description", "Thank you for boosting our server!"), after, after.guild)
            footer = self.replace_variables(config.get("footer", "Boosted by {user}"), after, after.guild)
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

async def setup(bot):
    await bot.add_cog(Boost(bot))