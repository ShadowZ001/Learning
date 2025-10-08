import discord
from discord.ext import commands
import json

class ApplySetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose setup option...",
        options=[
            discord.SelectOption(label="Title", description="Set embed title", value="title"),
            discord.SelectOption(label="Description", description="Set embed description", value="description"),
            discord.SelectOption(label="Hex Color", description="Set embed color", value="hex"),
            discord.SelectOption(label="Footer (Optional)", description="Set embed footer", value="footer"),
            discord.SelectOption(label="Image (Optional)", description="Set embed image", value="image"),
            discord.SelectOption(label="Button Name", description="Set apply button name", value="button"),
            discord.SelectOption(label="Questions", description="Set application questions", value="questions"),
            discord.SelectOption(label="Apply Inform Channel", description="Set channel for applications", value="channel"),
            discord.SelectOption(label="Apply On Role", description="Set role to give on accept", value="role"),
            discord.SelectOption(label="Apply Panel", description="Send apply panel", value="panel")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "title":
            modal = TitleModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "description":
            modal = DescriptionModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "hex":
            modal = HexModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "footer":
            modal = FooterModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "image":
            modal = ImageModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "button":
            modal = ButtonModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "questions":
            modal = QuestionsModal(self.bot, self.guild_id)
            await interaction.response.send_modal(modal)
        elif value == "channel":
            await interaction.response.send_message("Please mention the channel for applications:", ephemeral=True)
        elif value == "role":
            await interaction.response.send_message("Please mention the role to give on accept:", ephemeral=True)
        elif value == "panel":
            embed = discord.Embed(
                title="📨 Send Apply Panel",
                description="Please select the channel where you want to send the apply panel.",
                color=0x7289da
            )
            view = ApplyChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)

    async def send_apply_panel(self, interaction):
        try:
            config = await self.bot.db.get_apply_config(self.guild_id)
            if not config:
                await interaction.response.send_message("❌ Please configure the application system first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=config.get("title", "Application"),
                description=config.get("description", "Click the button below to apply!"),
                color=int(config.get("hex", "7289da"), 16)
            )
            
            if config.get("footer"):
                embed.set_footer(text=config["footer"])
            if config.get("image"):
                embed.set_image(url=config["image"])
            
            view = ApplyPanelView(self.bot, self.guild_id)
            button_name = config.get("button_name", "Apply")
            view.children[0].label = button_name
            
            await interaction.response.send_message(embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class TitleModal(discord.ui.Modal, title="Set Title"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    title_input = discord.ui.TextInput(label="Title", placeholder="Enter embed title...")
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db.set_apply_config(self.guild_id, "title", self.title_input.value)
        await interaction.response.send_message(f"✅ Title set to: {self.title_input.value}", ephemeral=True)

class DescriptionModal(discord.ui.Modal, title="Set Description"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    desc_input = discord.ui.TextInput(label="Description", placeholder="Enter embed description...", style=discord.TextStyle.paragraph)
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db.set_apply_config(self.guild_id, "description", self.desc_input.value)
        await interaction.response.send_message(f"✅ Description set!", ephemeral=True)

class HexModal(discord.ui.Modal, title="Set Hex Color"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    hex_input = discord.ui.TextInput(label="Hex Color", placeholder="Enter hex color (e.g., ff0000)...")
    
    async def on_submit(self, interaction: discord.Interaction):
        hex_value = self.hex_input.value.replace("#", "")
        await self.bot.db.set_apply_config(self.guild_id, "hex", hex_value)
        await interaction.response.send_message(f"✅ Color set to: #{hex_value}", ephemeral=True)

class FooterModal(discord.ui.Modal, title="Set Footer"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    footer_input = discord.ui.TextInput(label="Footer", placeholder="Enter footer text...")
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db.set_apply_config(self.guild_id, "footer", self.footer_input.value)
        await interaction.response.send_message(f"✅ Footer set!", ephemeral=True)

class ImageModal(discord.ui.Modal, title="Set Image"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    image_input = discord.ui.TextInput(label="Image URL", placeholder="Enter image URL...")
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db.set_apply_config(self.guild_id, "image", self.image_input.value)
        await interaction.response.send_message(f"✅ Image set!", ephemeral=True)

class ButtonModal(discord.ui.Modal, title="Set Button Name"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    button_input = discord.ui.TextInput(label="Button Name", placeholder="Enter button name...")
    
    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db.set_apply_config(self.guild_id, "button_name", self.button_input.value)
        await interaction.response.send_message(f"✅ Button name set to: {self.button_input.value}", ephemeral=True)

class QuestionsModal(discord.ui.Modal, title="Set Questions"):
    def __init__(self, bot, guild_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
    
    questions_input = discord.ui.TextInput(
        label="Questions (Max 20)", 
        placeholder="Enter questions separated by | (e.g., What's your age?|Why do you want to join?)",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        questions = [q.strip() for q in self.questions_input.value.split("|") if q.strip()]
        
        if len(questions) > 20:
            await interaction.response.send_message("❌ Maximum 20 questions allowed!", ephemeral=True)
            return
        
        await self.bot.db.set_apply_config(self.guild_id, "questions", json.dumps(questions))
        await interaction.response.send_message(f"✅ {len(questions)} questions set! (Max: 20)", ephemeral=True)

class ApplyPanelView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.button(label="Apply", style=discord.ButtonStyle.primary, emoji="📝")
    async def apply_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            config = await self.bot.db.get_apply_config(self.guild_id)
            questions = json.loads(config.get("questions", "[]"))
            
            if not questions:
                await interaction.response.send_message("❌ No questions configured!", ephemeral=True)
                return
            
            modal = ApplicationModal(self.bot, self.guild_id, questions)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class ApplicationModal(discord.ui.Modal, title="Application Form"):
    def __init__(self, bot, guild_id, questions):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        self.questions = questions
        
        # Add up to 5 questions as text inputs (Discord modal limit)
        for i, question in enumerate(questions[:5]):
            text_input = discord.ui.TextInput(
                label=f"Q{i+1}: {question[:45]}",
                placeholder=question,
                style=discord.TextStyle.paragraph,
                max_length=1000
            )
            self.add_item(text_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            config = await self.bot.db.get_apply_config(self.guild_id)
            channel_id = config.get("channel_id")
            
            if not channel_id:
                await interaction.response.send_message("❌ No application channel configured!", ephemeral=True)
                return
            
            channel = self.bot.get_channel(int(channel_id))
            if not channel:
                await interaction.response.send_message("❌ Application channel not found!", ephemeral=True)
                return
            
            # Create application embed
            embed = discord.Embed(
                title="📝 New Application",
                description=f"**Applicant:** {interaction.user.mention}\n**User ID:** {interaction.user.id}",
                color=0x00ff00,
                timestamp=interaction.created_at
            )
            
            # Add answers
            for i, child in enumerate(self.children):
                if i < len(self.questions):
                    embed.add_field(
                        name=f"Q{i+1}: {self.questions[i]}",
                        value=child.value or "No answer",
                        inline=False
                    )
            
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            
            # Create action buttons
            view = ApplicationActionView(self.bot, self.guild_id, interaction.user.id)
            
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message("✅ Your application has been submitted!", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error submitting application: {str(e)}", ephemeral=True)

class ApplicationActionView(discord.ui.View):
    def __init__(self, bot, guild_id, user_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.user_id = user_id
    
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.success, emoji="✅")
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            guild = self.bot.get_guild(self.guild_id)
            user = guild.get_member(self.user_id)
            
            if not user:
                await interaction.response.send_message("❌ User not found in server!", ephemeral=True)
                return
            
            # Get role to assign
            config = await self.bot.db.get_apply_config(self.guild_id)
            role_id = config.get("role_id")
            
            if role_id:
                role = guild.get_role(int(role_id))
                if role:
                    await user.add_roles(role, reason=f"Application accepted by {interaction.user}")
            
            # Send DM to user
            try:
                embed = discord.Embed(
                    title="✅ Application Accepted",
                    description=f"Your application for **{guild.name}** has been accepted!",
                    color=0x00ff00
                )
                await user.send(embed=embed)
            except:
                pass
            
            # Update embed
            embed = interaction.message.embeds[0]
            embed.color = 0x00ff00
            embed.add_field(name="Status", value=f"✅ Accepted by {interaction.user.mention}", inline=False)
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Decline", style=discord.ButtonStyle.danger, emoji="❌")
    async def decline_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            guild = self.bot.get_guild(self.guild_id)
            user = guild.get_member(self.user_id)
            
            if user:
                try:
                    embed = discord.Embed(
                        title="❌ Application Declined",
                        description=f"Your application for **{guild.name}** has been declined.",
                        color=0xff0000
                    )
                    await user.send(embed=embed)
                except:
                    pass
            
            # Update embed
            embed = interaction.message.embeds[0]
            embed.color = 0xff0000
            embed.add_field(name="Status", value=f"❌ Declined by {interaction.user.mention}", inline=False)
            
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="Decline with Reason", style=discord.ButtonStyle.secondary, emoji="📝")
    async def decline_reason_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DeclineReasonModal(self.bot, self.guild_id, self.user_id)
        await interaction.response.send_modal(modal)

class DeclineReasonModal(discord.ui.Modal, title="Decline Reason"):
    def __init__(self, bot, guild_id, user_id):
        super().__init__()
        self.bot = bot
        self.guild_id = guild_id
        self.user_id = user_id
    
    reason_input = discord.ui.TextInput(
        label="Reason for decline",
        placeholder="Enter reason...",
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            guild = self.bot.get_guild(self.guild_id)
            user = guild.get_member(self.user_id)
            
            if user:
                try:
                    embed = discord.Embed(
                        title="❌ Application Declined",
                        description=f"Your application for **{guild.name}** has been declined.\n\n**Reason:** {self.reason_input.value}",
                        color=0xff0000
                    )
                    await user.send(embed=embed)
                except:
                    pass
            
            # Update embed
            embed = interaction.message.embeds[0]
            embed.color = 0xff0000
            embed.add_field(name="Status", value=f"❌ Declined by {interaction.user.mention}\n**Reason:** {self.reason_input.value}", inline=False)
            
            await interaction.edit_original_response(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class Apply(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="apply")
    @commands.has_permissions(administrator=True)
    async def apply_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="📝 Application System",
                description="**Commands:**\n• `/apply setup` - Configure application system",
                color=0x7289da
            )
            await ctx.send(embed=embed)
    
    @apply_group.command(name="setup")
    @commands.has_permissions(administrator=True)
    async def apply_setup(self, ctx):
        """Setup application system"""
        embed = discord.Embed(
            title="📝 Application System Setup",
            description="Use the dropdown below to configure your application system.",
            color=0x7289da
        )
        
        view = ApplySetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @apply_group.command(name="list")
    @commands.has_permissions(administrator=True)
    async def apply_list(self, ctx):
        """List all application configurations"""
        try:
            config = await self.bot.db.get_apply_config(ctx.guild.id)
            
            if not config:
                embed = discord.Embed(
                    title="📝 Application System",
                    description="❌ No application system configured yet.",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📝 Application Configuration",
                color=0x7289da
            )
            
            embed.add_field(name="Title", value=config.get("title", "Not set"), inline=True)
            embed.add_field(name="Description", value=config.get("description", "Not set")[:50] + "..." if len(config.get("description", "")) > 50 else config.get("description", "Not set"), inline=True)
            embed.add_field(name="Color", value=f"#{config.get('hex', '7289da')}", inline=True)
            embed.add_field(name="Footer", value=config.get("footer", "Not set"), inline=True)
            embed.add_field(name="Button Name", value=config.get("button_name", "Not set"), inline=True)
            embed.add_field(name="Image", value="Set" if config.get("image") else "Not set", inline=True)
            
            questions = json.loads(config.get("questions", "[]"))
            embed.add_field(name="Questions", value=f"{len(questions)} questions configured", inline=True)
            
            channel_id = config.get("channel_id")
            embed.add_field(name="Inform Channel", value=f"<#{channel_id}>" if channel_id else "Not set", inline=True)
            
            role_id = config.get("role_id")
            embed.add_field(name="Apply Role", value=f"<@&{role_id}>" if role_id else "Not set", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @apply_group.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def apply_reset(self, ctx):
        """Reset application system"""
        embed = discord.Embed(
            title="🔄 Reset Application System",
            description="Select what you want to reset:",
            color=0xff8c00
        )
        
        view = ApplyResetView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @apply_group.command(name="status")
    @commands.has_permissions(administrator=True)
    async def apply_status(self, ctx):
        """Show application system status"""
        try:
            config = await self.bot.db.get_apply_config(ctx.guild.id)
            
            embed = discord.Embed(
                title="📊 Application System Status",
                color=0x7289da
            )
            
            if not config:
                embed.description = "❌ **Status:** Not Configured"
                embed.color = 0xff0000
            else:
                # Check if system is ready
                required_fields = ["title", "description", "questions", "channel_id"]
                missing_fields = [field for field in required_fields if not config.get(field)]
                
                if not missing_fields:
                    embed.description = "✅ **Status:** Fully Configured & Ready"
                    embed.color = 0x00ff00
                else:
                    embed.description = "⚠️ **Status:** Partially Configured"
                    embed.color = 0xff8c00
                    embed.add_field(
                        name="Missing Configuration",
                        value="\n".join([f"• {field.replace('_', ' ').title()}" for field in missing_fields]),
                        inline=False
                    )
                
                # Show configuration summary
                questions = json.loads(config.get("questions", "[]"))
                embed.add_field(name="Questions", value=f"{len(questions)}/20", inline=True)
                embed.add_field(name="Channel", value="✅ Set" if config.get("channel_id") else "❌ Not set", inline=True)
                embed.add_field(name="Role", value="✅ Set" if config.get("role_id") else "❌ Not set", inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle channel and role setup"""
        if message.author.bot:
            return
        
        # Handle channel setup
        if message.content.startswith("<#") and message.content.endswith(">"):
            channel_id = message.content[2:-1]
            try:
                await self.bot.db.set_apply_config(message.guild.id, "channel_id", channel_id)
                await message.reply("✅ Application channel set!")
            except:
                pass
        
        # Handle role setup
        elif message.content.startswith("<@&") and message.content.endswith(">"):
            role_id = message.content[3:-1]
            try:
                await self.bot.db.set_apply_config(message.guild.id, "role_id", role_id)
                await message.reply("✅ Application role set!")
            except:
                pass

class ApplyResetView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Select what to reset...",
        options=[
            discord.SelectOption(label="Title", description="Reset embed title", value="title"),
            discord.SelectOption(label="Description", description="Reset embed description", value="description"),
            discord.SelectOption(label="Color", description="Reset embed color", value="hex"),
            discord.SelectOption(label="Footer", description="Reset embed footer", value="footer"),
            discord.SelectOption(label="Image", description="Reset embed image", value="image"),
            discord.SelectOption(label="Button Name", description="Reset button name", value="button_name"),
            discord.SelectOption(label="Questions", description="Reset all questions", value="questions"),
            discord.SelectOption(label="Channel", description="Reset inform channel", value="channel_id"),
            discord.SelectOption(label="Role", description="Reset apply role", value="role_id")
        ]
    )
    async def reset_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        field = select.values[0]
        
        try:
            config = await self.bot.db.get_apply_config(self.guild_id)
            if config and field in config:
                del config[field]
                await self.bot.db.set_apply_config(self.guild_id, "_full_config", json.dumps(config))
            
            field_name = field.replace("_", " ").title()
            await interaction.response.send_message(f"✅ {field_name} has been reset!", ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="🗑️ Reset All", style=discord.ButtonStyle.danger)
    async def reset_all_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Clear all configuration
            await self.bot.db.set_apply_config(self.guild_id, "_full_config", json.dumps({}))
            
            embed = discord.Embed(
                title="✅ Configuration Reset",
                description="All application system settings have been reset!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class ApplyChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select channel for apply panel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        await interaction.response.defer()
        
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        config = await self.bot.db.get_apply_config(self.guild_id)
        
        if not config:
            await interaction.followup.send("❌ Please configure the application system first!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title=config.get("title", "Application"),
            description=config.get("description", "Click the button below to apply!"),
            color=int(config.get("hex", "7289da"), 16)
        )
        
        if config.get("footer"):
            embed.set_footer(text=config["footer"])
        if config.get("image"):
            embed.set_image(url=config["image"])
        
        view = ApplyPanelView(self.bot, self.guild_id)
        button_name = config.get("button_name", "Apply")
        view.children[0].label = button_name
        
        try:
            await channel.send(embed=embed, view=view)
            
            success_embed = discord.Embed(
                title="✅ Apply Panel Sent",
                description=f"Apply panel has been sent to {channel.mention}",
                color=0x00ff00
            )
            await interaction.edit_original_response(embed=success_embed, view=None)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed to send apply panel: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Apply(bot))