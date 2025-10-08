import discord
from discord.ext import commands
import re

class VerifySetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=900)  # 15 minutes
        self.bot = bot
        self.guild_id = guild_id
        self.config = {}
    
    @discord.ui.select(
        placeholder="Configure verification embed...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set embed title", value="title"),
            discord.SelectOption(label="📄 Description", description="Set embed description", value="description"),
            discord.SelectOption(label="🎨 Hex Color", description="Set embed color", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Set embed image (optional)", value="image"),
            discord.SelectOption(label="👥 Roles", description="Set verification roles", value="roles"),
            discord.SelectOption(label="🔘 Button", description="Configure verify button", value="button"),
            discord.SelectOption(label="📤 Send", description="Send verification embed", value="send")
        ]
    )
    async def setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        value = select.values[0]
        
        if value == "title":
            modal = TitleModal(self)
            await interaction.response.send_modal(modal)
        elif value == "description":
            modal = DescriptionModal(self)
            await interaction.response.send_modal(modal)
        elif value == "color":
            modal = ColorModal(self)
            await interaction.response.send_modal(modal)
        elif value == "image":
            modal = ImageModal(self)
            await interaction.response.send_modal(modal)
        elif value == "roles":
            modal = RolesModal(self)
            await interaction.response.send_modal(modal)
        elif value == "button":
            modal = ButtonModal(self)
            await interaction.response.send_modal(modal)
        elif value == "send":
            if not all(k in self.config for k in ["title", "description", "button_name", "roles"]):
                await interaction.response.send_message("Please configure title, description, button, and roles first!", ephemeral=True)
                return
            
            view = ChannelSelectView(self.bot, self.guild_id, self.config)
            embed = discord.Embed(
                title="📤 Select Verification Channel",
                description="Choose where to send the verification embed.",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=view)

class TitleModal(discord.ui.Modal, title="Set Verification Title"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    title_input = discord.ui.TextInput(
        label="Verification Title",
        placeholder="Enter verification embed title...",
        max_length=256
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["title"] = self.title_input.value
        embed = discord.Embed(
            title="✅ Title Set",
            description=f"Title: `{self.title_input.value}`",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class DescriptionModal(discord.ui.Modal, title="Set Verification Description"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    desc_input = discord.ui.TextInput(
        label="Verification Description",
        placeholder="Enter verification embed description...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["description"] = self.desc_input.value
        embed = discord.Embed(
            title="✅ Description Set",
            description=f"Description: `{self.desc_input.value}`",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class ColorModal(discord.ui.Modal, title="Set Embed Color"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    color_input = discord.ui.TextInput(
        label="Hex Color",
        placeholder="Enter hex color (e.g., #7289da)...",
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        color = self.color_input.value
        if not color.startswith("#"):
            color = "#" + color
        
        if re.match(r'^#[0-9A-Fa-f]{6}$', color):
            self.view.config["color"] = color
            embed = discord.Embed(
                title="✅ Color Set",
                description=f"Color: `{color}`",
                color=int(color[1:], 16)
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
        else:
            await interaction.response.send_message("Invalid hex color format!", ephemeral=True)

class ImageModal(discord.ui.Modal, title="Set Embed Image"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    image_input = discord.ui.TextInput(
        label="Image URL",
        placeholder="Enter image URL (leave empty to skip)...",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["image"] = self.image_input.value or None
        embed = discord.Embed(
            title="✅ Image Set",
            description=f"Image: `{self.image_input.value or 'None'}`",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class RolesModal(discord.ui.Modal, title="Set Verification Roles"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    roles_input = discord.ui.TextInput(
        label="Role Names/IDs",
        placeholder="Enter role names or IDs separated by commas...",
        style=discord.TextStyle.paragraph
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        role_names = [r.strip() for r in self.roles_input.value.split(",")]
        roles = []
        
        for role_name in role_names:
            if role_name.isdigit():
                role = interaction.guild.get_role(int(role_name))
            else:
                role = discord.utils.get(interaction.guild.roles, name=role_name)
            
            if role:
                roles.append(role.id)
        
        if not roles:
            await interaction.response.send_message("No valid roles found!", ephemeral=True)
            return
        
        self.view.config["roles"] = roles
        role_mentions = [f"<@&{r}>" for r in roles]
        embed = discord.Embed(
            title="✅ Roles Set",
            description=f"Roles: {', '.join(role_mentions)}",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class ButtonModal(discord.ui.Modal, title="Configure Verify Button"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    button_name = discord.ui.TextInput(
        label="Button Name",
        placeholder="Enter button text...",
        max_length=80
    )
    
    button_emoji = discord.ui.TextInput(
        label="Button Emoji",
        placeholder="Enter emoji (leave empty to skip)...",
        required=False,
        max_length=10
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["button_name"] = self.button_name.value
        self.view.config["button_emoji"] = self.button_emoji.value or None
        
        embed = discord.Embed(
            title="✅ Button Configured",
            description=f"Button: `{self.button_emoji.value or ''} {self.button_name.value}`",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class ChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id, config):
        super().__init__(timeout=900)  # 15 minutes
        self.bot = bot
        self.guild_id = guild_id
        self.config = config
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        
        # Save config to database
        await self.bot.db.set_verify_config(self.guild_id, self.config)
        
        # Create verification embed
        embed = discord.Embed(
            title=self.config["title"],
            description=self.config["description"],
            color=int(self.config.get("color", "#7289da")[1:], 16)
        )
        
        if self.config.get("image"):
            embed.set_image(url=self.config["image"])
        
        # Create verify button
        view = VerifyButtonView(self.bot, self.guild_id)
        
        try:
            await channel.send(embed=embed, view=view)
            
            success_embed = discord.Embed(
                title="✅ Verification Setup Complete",
                description=f"Verification embed sent to {channel.mention}",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=success_embed, view=None)
        except Exception as e:
            await interaction.response.send_message(f"Failed to send embed: {str(e)}", ephemeral=True)

class VerifyButtonView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.success, custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        config = await self.bot.db.get_verify_config(self.guild_id)
        if not config:
            await interaction.response.send_message("Verification not configured!", ephemeral=True)
            return
        
        # Update button text and emoji from config
        button.label = config.get("button_name", "Verify")
        if config.get("button_emoji"):
            button.emoji = config["button_emoji"]
        
        # Check if user already has roles
        user_roles = [role.id for role in interaction.user.roles]
        verify_roles = config.get("roles", [])
        
        if any(role_id in user_roles for role_id in verify_roles):
            await interaction.response.send_message("You are already verified!", ephemeral=True)
            return
        
        # Add roles to user
        roles_to_add = []
        for role_id in verify_roles:
            role = interaction.guild.get_role(role_id)
            if role:
                roles_to_add.append(role)
        
        try:
            await interaction.user.add_roles(*roles_to_add, reason="Verification")
            
            # Remove unverified role if exists
            unverified_role = discord.utils.get(interaction.guild.roles, name="Unverified")
            if unverified_role and unverified_role in interaction.user.roles:
                await interaction.user.remove_roles(unverified_role, reason="Verified")
            
            role_mentions = [role.mention for role in roles_to_add]
            
            embed = discord.Embed(
                title="✅ Verification Successful",
                description=f"You have been verified and given the following roles:\n{', '.join(role_mentions)}",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Failed to verify: {str(e)}", ephemeral=True)

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Hide channels from unverified users"""
        config = await self.bot.db.get_verify_config(member.guild.id)
        if not config:
            return
        
        # Create or get unverified role
        unverified_role = discord.utils.get(member.guild.roles, name="Unverified")
        if not unverified_role:
            try:
                unverified_role = await member.guild.create_role(
                    name="Unverified",
                    color=0x808080,
                    reason="Verification system"
                )
                
                # Hide all channels except verification channel
                for channel in member.guild.channels:
                    if isinstance(channel, (discord.TextChannel, discord.VoiceChannel)):
                        await channel.set_permissions(unverified_role, view_channel=False)
            except:
                pass
        
        # Add unverified role to new member
        if unverified_role:
            try:
                await member.add_roles(unverified_role, reason="New member - needs verification")
            except:
                pass
    
    @commands.hybrid_group(name="verify")
    async def verify_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `/verify setup` or `/verify reset`")
    
    @verify_group.command(name="setup")
    async def verify_setup(self, ctx):
        """Setup verification system"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🔐 Verification Setup",
            description="Configure your server verification system using the dropdown below.",
            color=0x7289da
        )
        
        view = VerifySetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @verify_group.command(name="reset")
    async def verify_reset(self, ctx):
        """Reset verification configuration"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        await self.bot.db.reset_verify_config(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ Verification Reset",
            description="Verification configuration has been reset.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Verify(bot))