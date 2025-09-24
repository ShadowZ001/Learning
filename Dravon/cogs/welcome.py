import discord
from discord.ext import commands
from discord import app_commands
from utils.embeds import create_welcome_embed, create_setup_embed
from typing import Optional

class WelcomeSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
        self.config = {
            "title": "Welcome!",
            "description": "Welcome to the server!",
            "color": "#7289da",
            "image_url": None,
            "thumbnail_url": None,
            "footer": None,
            "dm_welcome": False,
            "channel_id": None,
            "chat_format": False
        }
    
    async def update_preview(self, interaction: discord.Interaction):
        preview_embed = create_welcome_embed(
            title=self.config["title"],
            description=self.config["description"],
            color=self.config["color"],
            image_url=self.config["image_url"],
            thumbnail_url=self.config["thumbnail_url"],
            footer=self.config["footer"]
        )
        setup_embed = create_setup_embed(preview_embed)
        
        await interaction.response.edit_message(embeds=[preview_embed, setup_embed], view=self)
    
    @discord.ui.button(label="Set Footer", style=discord.ButtonStyle.primary)
    async def set_footer(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = FooterModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Toggle DM Welcome", style=discord.ButtonStyle.secondary)
    async def toggle_dm_welcome(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config["dm_welcome"] = not self.config["dm_welcome"]
        button.label = f"DM Welcome: {'ON' if self.config['dm_welcome'] else 'OFF'}"
        await self.update_preview(interaction)
    
    @discord.ui.button(label="Set Thumbnail", style=discord.ButtonStyle.primary)
    async def set_thumbnail(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ThumbnailModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Title", style=discord.ButtonStyle.primary)
    async def set_title(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = TitleModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Description", style=discord.ButtonStyle.primary)
    async def set_description(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = DescriptionModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Hex Color", style=discord.ButtonStyle.primary)
    async def set_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ColorModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Image", style=discord.ButtonStyle.secondary)
    async def set_image(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ImageModal(self)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Channel", style=discord.ButtonStyle.secondary)
    async def set_channel(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = ChannelSelectView(self)
        await interaction.response.edit_message(view=view)
    
    @discord.ui.button(label="Chat Format", style=discord.ButtonStyle.secondary, row=1)
    async def toggle_chat_format(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config["chat_format"] = not self.config["chat_format"]
        button.label = f"Chat Format: {'ON' if self.config['chat_format'] else 'OFF'}"
        await self.update_preview(interaction)
    
    @discord.ui.button(label="Done", style=discord.ButtonStyle.success, row=1)
    async def finish_setup(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.config["channel_id"]:
            await interaction.response.send_message("Please select a channel first!", ephemeral=True)
            return
        
        await self.bot.db.set_welcome_config(interaction.guild.id, self.config)
        
        embed = discord.Embed(
            title="Welcome Setup Complete!",
            description=f"Welcome messages will be sent to <#{self.config['channel_id']}>",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class TitleModal(discord.ui.Modal, title="Set Welcome Title"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    title_input = discord.ui.TextInput(
        label="Welcome Title",
        placeholder="Enter the welcome message title...",
        max_length=256
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["title"] = self.title_input.value
        await self.view.update_preview(interaction)

class DescriptionModal(discord.ui.Modal, title="Set Welcome Description"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    description_input = discord.ui.TextInput(
        label="Welcome Description",
        placeholder="Enter the welcome message description...",
        style=discord.TextStyle.paragraph,
        max_length=2000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["description"] = self.description_input.value
        await self.view.update_preview(interaction)

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
        
        try:
            int(color.replace("#", ""), 16)
            self.view.config["color"] = color
            await self.view.update_preview(interaction)
        except ValueError:
            await interaction.response.send_message("Invalid hex color format!", ephemeral=True)

class FooterModal(discord.ui.Modal, title="Set Welcome Footer"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    footer_input = discord.ui.TextInput(
        label="Footer Text",
        placeholder="Enter footer text (leave empty to remove)...",
        required=False,
        max_length=2048
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["footer"] = self.footer_input.value or None
        await self.view.update_preview(interaction)

class ThumbnailModal(discord.ui.Modal, title="Set Welcome Thumbnail"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    thumbnail_input = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="Enter thumbnail URL (leave empty to remove)...",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["thumbnail_url"] = self.thumbnail_input.value or None
        await self.view.update_preview(interaction)

class ImageModal(discord.ui.Modal, title="Set Welcome Image"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    image_input = discord.ui.TextInput(
        label="Image URL",
        placeholder="Enter image URL (leave empty to remove)...",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["image_url"] = self.image_input.value or None
        await self.view.update_preview(interaction)

class ChannelSelectView(discord.ui.View):
    def __init__(self, welcome_view):
        super().__init__(timeout=60)
        self.welcome_view = welcome_view
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        self.welcome_view.config["channel_id"] = select.values[0].id
        
        preview_embed = create_welcome_embed(
            title=self.welcome_view.config["title"],
            description=self.welcome_view.config["description"],
            color=self.welcome_view.config["color"],
            image_url=self.welcome_view.config["image_url"],
            thumbnail_url=self.welcome_view.config["thumbnail_url"],
            footer=self.welcome_view.config["footer"]
        )
        setup_embed = create_setup_embed(preview_embed)
        setup_embed.add_field(name="Selected Channel", value=f"<#{select.values[0].id}>", inline=False)
        
        await interaction.response.edit_message(embeds=[preview_embed, setup_embed], view=self.welcome_view)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="welcome")
    @app_commands.describe(action="Actions: setup, test, reset, config")
    async def welcome_setup(self, ctx, action: str = "setup"):
        if action.lower() == "setup":
            if not ctx.author.guild_permissions.manage_guild:
                await ctx.send("You need 'Manage Server' permission to use this command.")
                return
            
            view = WelcomeSetupView(self.bot)
            
            preview_embed = create_welcome_embed()
            setup_embed = create_setup_embed(preview_embed)
            
            await ctx.send(embeds=[preview_embed, setup_embed], view=view)
        
        elif action.lower() == "test":
            if not ctx.author.guild_permissions.manage_guild:
                await ctx.send("You need 'Manage Server' permission to use this command.")
                return
            
            config = await self.bot.db.get_welcome_config(ctx.guild.id)
            if not config:
                await ctx.send("No welcome configuration found. Use `welcome setup` first.")
                return
            
            channel = self.bot.get_channel(config["channel_id"])
            if not channel:
                await ctx.send("Welcome channel not found. Please reconfigure with `welcome setup`.")
                return
            
            embed = create_welcome_embed(
                title=config["title"],
                description=config["description"],
                color=config["color"],
                image_url=config["image_url"],
                thumbnail_url=config.get("thumbnail_url"),
                footer=config.get("footer"),
                member=ctx.author
            )
            
            await channel.send(embed=embed)
            
            if config.get("dm_welcome", False):
                try:
                    await ctx.author.send(embed=embed)
                    await ctx.send(f"Test welcome message sent to {channel.mention} and your DMs")
                except:
                    await ctx.send(f"Test welcome message sent to {channel.mention} (DM failed)")
            else:
                await ctx.send(f"Test welcome message sent to {channel.mention}")
        
        elif action.lower() == "reset":
            if not ctx.author.guild_permissions.manage_guild:
                await ctx.send("You need 'Manage Server' permission to use this command.")
                return
            
            await self.bot.db.set_welcome_config(ctx.guild.id, {})
            
            embed = discord.Embed(
                title="Welcome Configuration Reset",
                description="All welcome settings have been cleared.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        
        elif action.lower() == "config":
            config = await self.bot.db.get_welcome_config(ctx.guild.id)
            if not config:
                await ctx.send("No welcome configuration found. Use `welcome setup` to configure.")
                return
            
            channel = self.bot.get_channel(config["channel_id"]) if config.get("channel_id") else None
            
            embed = discord.Embed(
                title="Current Welcome Configuration",
                color=int(config.get("color", "#7289da").replace("#", ""), 16)
            )
            
            embed.add_field(name="Title", value=config.get("title", "Not set"), inline=False)
            embed.add_field(name="Description", value=config.get("description", "Not set"), inline=False)
            embed.add_field(name="Color", value=config.get("color", "Not set"), inline=True)
            embed.add_field(name="Channel", value=channel.mention if channel else "Not set", inline=True)
            embed.add_field(name="DM Welcome", value="Enabled" if config.get("dm_welcome") else "Disabled", inline=True)
            embed.add_field(name="Footer", value=config.get("footer", "Not set"), inline=False)
            embed.add_field(name="Image URL", value=config.get("image_url", "Not set"), inline=False)
            embed.add_field(name="Thumbnail URL", value=config.get("thumbnail_url", "Not set"), inline=False)
            
            await ctx.send(embed=embed)
        
        else:
            await ctx.send("Use `welcome setup`, `welcome test`, `welcome reset`, or `welcome config`.")
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await self.bot.db.get_welcome_config(member.guild.id)
        if not config:
            return
        
        channel = self.bot.get_channel(config["channel_id"])
        if not channel:
            return
        
        if config.get("chat_format", False):
            # Send as normal chat message
            message = f"{config.get('title', 'Welcome!')} {member.mention}\n{config.get('description', 'Welcome to the server!')}"
            await channel.send(message)
        else:
            # Send as embed
            embed = create_welcome_embed(
                title=config["title"],
                description=config["description"],
                color=config["color"],
                image_url=config["image_url"],
                thumbnail_url=config.get("thumbnail_url"),
                footer=config.get("footer"),
                member=member
            )
            await channel.send(embed=embed)
        
        if config.get("dm_welcome", False):
            try:
                if config.get("chat_format", False):
                    message = f"{config.get('title', 'Welcome!')} {member.mention}\n{config.get('description', 'Welcome to the server!')}"
                    await member.send(message)
                else:
                    embed = create_welcome_embed(
                        title=config["title"],
                        description=config["description"],
                        color=config["color"],
                        image_url=config["image_url"],
                        thumbnail_url=config.get("thumbnail_url"),
                        footer=config.get("footer"),
                        member=member
                    )
                    await member.send(embed=embed)
            except:
                pass

async def setup(bot):
    await bot.add_cog(Welcome(bot))