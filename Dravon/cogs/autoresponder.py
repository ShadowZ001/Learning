import discord
from discord.ext import commands
from discord import app_commands

class TitleModal(discord.ui.Modal, title="Set Embed Title"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    title_input = discord.ui.TextInput(
        label="Embed Title",
        placeholder="Enter the embed title...",
        max_length=256
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["title"] = self.title_input.value
        await interaction.response.send_message(f"Title set to: `{self.title_input.value}`", ephemeral=True)

class DescriptionModal(discord.ui.Modal, title="Set Embed Description"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    description_input = discord.ui.TextInput(
        label="Embed Description",
        placeholder="Enter the embed description...",
        style=discord.TextStyle.paragraph,
        max_length=4000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["description"] = self.description_input.value
        await interaction.response.send_message(f"Description set successfully!", ephemeral=True)

class ColorModal(discord.ui.Modal, title="Set Embed Color"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    color_input = discord.ui.TextInput(
        label="Hex Color",
        placeholder="Enter hex color (e.g., #ff0000)...",
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        color = self.color_input.value
        if not color.startswith("#"):
            color = "#" + color
        
        try:
            int(color.replace("#", ""), 16)
            self.view.config["color"] = color
            await interaction.response.send_message(f"Color set to: `{color}`", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("Invalid hex color format!", ephemeral=True)

class AuthorModal(discord.ui.Modal, title="Set Embed Author"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    author_input = discord.ui.TextInput(
        label="Author Name",
        placeholder="Enter author name (leave empty to remove)...",
        required=False,
        max_length=256
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["author"] = self.author_input.value or None
        await interaction.response.send_message(f"Author set to: `{self.author_input.value or 'None'}`", ephemeral=True)

class ThumbnailModal(discord.ui.Modal, title="Set Embed Thumbnail"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    thumbnail_input = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="Enter thumbnail URL (leave empty to remove)...",
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["thumbnail"] = self.thumbnail_input.value or None
        await interaction.response.send_message(f"Thumbnail set successfully!", ephemeral=True)

class EmbedSetupView(discord.ui.View):
    def __init__(self, trigger: str, pattern: str):
        super().__init__(timeout=900)
        self.trigger = trigger
        self.pattern = pattern
        self.config = {}
    
    @discord.ui.select(
        placeholder="Choose embed property to configure...",
        options=[
            discord.SelectOption(label="Title", description="Main embed heading (required)", value="title"),
            discord.SelectOption(label="Description", description="Main embed content (required)", value="description"),
            discord.SelectOption(label="Color", description="Embed border color (required)", value="color"),
            discord.SelectOption(label="Author", description="Author name display (optional)", value="author"),
            discord.SelectOption(label="Thumbnail", description="Small image in corner (optional)", value="thumbnail"),
            discord.SelectOption(label="Save Autoresponder", description="Save and activate the autoresponder", value="save")
        ]
    )
    async def embed_property_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        property_type = select.values[0]
        
        if property_type == "save":
            # Save autoresponder to database
            autoresponder_config = {
                "pattern": self.pattern.lower(),
                "title": self.config.get("title", "Autoresponder"),
                "description": self.config.get("description", "Automated response"),
                "color": self.config.get("color", "#7289da"),
                "author": self.config.get("author"),
                "thumbnail": self.config.get("thumbnail")
            }
            
            # Get bot instance from interaction
            bot = interaction.client
            await bot.db.set_autoresponder(interaction.guild.id, self.trigger.lower(), autoresponder_config)
            
            embed = discord.Embed(
                title="✅ Autoresponder Saved",
                description=f"**Trigger:** `{self.trigger}`\n**Pattern:** {self.pattern}\n\nAutoresponder has been created and activated!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)
        elif property_type == "title":
            modal = TitleModal(self)
            await interaction.response.send_modal(modal)
        elif property_type == "description":
            modal = DescriptionModal(self)
            await interaction.response.send_modal(modal)
        elif property_type == "color":
            modal = ColorModal(self)
            await interaction.response.send_modal(modal)
        elif property_type == "author":
            modal = AuthorModal(self)
            await interaction.response.send_modal(modal)
        elif property_type == "thumbnail":
            modal = ThumbnailModal(self)
            await interaction.response.send_modal(modal)

class PatternSelectView(discord.ui.View):
    def __init__(self, trigger: str):
        super().__init__(timeout=900)  # 15 minutes
        self.trigger = trigger
    
    @discord.ui.select(
        placeholder="Choose pattern matching type...",
        options=[
            discord.SelectOption(label="Exact", description="Message must match exactly", value="exact"),
            discord.SelectOption(label="Starts With", description="Message begins with trigger", value="starts_with"),
            discord.SelectOption(label="Contains", description="Message contains trigger anywhere", value="contains"),
            discord.SelectOption(label="Regex", description="Advanced pattern matching", value="regex")
        ]
    )
    async def pattern_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        pattern_type = select.values[0]
        pattern_name = select.options[int(['exact', 'starts_with', 'contains', 'regex'].index(pattern_type))].label
        
        embed = discord.Embed(
            title="🎨 Rich Embed Response Setup",
            description=f"**Trigger:** `{self.trigger}`\n\nUse the dropdown menu below to configure your embed properties.\n\n📝 **Available Properties**\n\n• **Title** → Main embed heading (required)\n• **Description** → Main embed content (required)\n• **Color** → Embed border color (required)\n• **Author** → Author name display (optional)\n• **Thumbnail** → Small image in corner (optional)\n• **Save Autoresponder** → Save and activate\n\n💡 **Pro Tips**\n• Configure at least a title or description\n• Use hex colors like `#ff0000` for red\n• Thumbnail URLs must be valid image links",
            color=0x7289da
        )
        
        view = EmbedSetupView(self.trigger, pattern_name)
        await interaction.response.edit_message(embed=embed, view=view)

class EditResponseView(discord.ui.View):
    def __init__(self, trigger: str, config: dict, bot):
        super().__init__(timeout=900)
        self.trigger = trigger
        self.config = config.copy()
        self.bot = bot
    
    @discord.ui.button(label="Edit Response", style=discord.ButtonStyle.primary)
    async def edit_response(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Create embed setup view similar to create command
        view = EmbedSetupView(self.trigger, self.config["pattern"].title())
        view.config = self.config.copy()  # Pre-fill with existing config
        
        embed = discord.Embed(
            title="🎨 Rich Embed Response Setup",
            description=f"**Trigger:** `{self.trigger}`\n\nUse the dropdown menu below to configure your embed properties.\n\n📝 **Available Properties**\n\n• **Title** → Main embed heading (required)\n• **Description** → Main embed content (required)\n• **Color** → Embed border color (required)\n• **Author** → Author name display (optional)\n• **Thumbnail** → Small image in corner (optional)\n• **Save Autoresponder** → Save and activate\n\n💡 **Pro Tips**\n• Configure at least a title or description\n• Use hex colors like `#ff0000` for red\n• Thumbnail URLs must be valid image links",
            color=0x7289da
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class TriggerSelectView(discord.ui.View):
    def __init__(self, autoresponders: dict, bot):
        super().__init__(timeout=900)
        self.autoresponders = autoresponders
        self.bot = bot
        
        # Create select options from triggers
        options = []
        for trigger, config in list(autoresponders.items())[:25]:  # Discord limit of 25 options
            options.append(
                discord.SelectOption(
                    label=trigger,
                    description=f"Pattern: {config['pattern'].title()}",
                    value=trigger
                )
            )
        
        if options:
            self.add_item(TriggerSelect(options, self.autoresponders, self.bot))

class TriggerSelect(discord.ui.Select):
    def __init__(self, options, autoresponders, bot):
        super().__init__(placeholder="Choose a trigger to edit...", options=options)
        self.autoresponders = autoresponders
        self.bot = bot
    
    async def callback(self, interaction: discord.Interaction):
        selected_trigger = self.values[0]
        config = self.autoresponders[selected_trigger]
        
        # Create response preview
        response_preview = f"**Title:** {config.get('title', 'Not set')}\n**Description:** {config.get('description', 'Not set')}\n**Color:** {config.get('color', 'Not set')}"
        if config.get('author'):
            response_preview += f"\n**Author:** {config['author']}"
        if config.get('thumbnail'):
            response_preview += f"\n**Thumbnail:** Set"
        
        embed = discord.Embed(
            title="✏️ Trigger Editor",
            description=f"**Selected Trigger:** `{selected_trigger}`\n**Pattern Type:** `{config['pattern'].title()}`\n\n📝 **Current Response**\n```\n{response_preview}\n```\n\n**Next Step**\nClick the **Edit Response** button below to modify the autoresponse message.",
            color=0x7289da
        )
        
        view = EditResponseView(selected_trigger, config, self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class AutoresponderListView(discord.ui.View):
    def __init__(self, autoresponders: dict, per_page: int = 5):
        super().__init__(timeout=300)
        self.autoresponders = list(autoresponders.items())
        self.per_page = per_page
        self.current_page = 0
        self.max_pages = (len(self.autoresponders) - 1) // per_page + 1 if self.autoresponders else 1
    
    def get_embed(self):
        if not self.autoresponders:
            return discord.Embed(
                title="📋 Autoresponders",
                description="No autoresponders configured for this server.",
                color=0x7289da
            )
        
        start = self.current_page * self.per_page
        end = start + self.per_page
        page_items = self.autoresponders[start:end]
        
        embed = discord.Embed(
            title="📋 Server Autoresponders",
            description=f"Found **{len(self.autoresponders)}** autoresponder(s) in this server:",
            color=0x7289da
        )
        
        for i, (trigger, config) in enumerate(page_items, start + 1):
            pattern = config["pattern"].title()
            title = config.get("title", "No title")
            embed.add_field(
                name=f"{i}. `{trigger}`",
                value=f"**Pattern:** {pattern}\n**Title:** {title}",
                inline=True
            )
        
        embed.set_footer(text=f"Page {self.current_page + 1}/{self.max_pages}")
        return embed
    
    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        else:
            self.current_page = self.max_pages - 1
        
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.max_pages - 1:
            self.current_page += 1
        else:
            self.current_page = 0
        
        embed = self.get_embed()
        await interaction.response.edit_message(embed=embed, view=self)

class AutoResponder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        autoresponders = await self.bot.db.get_autoresponders(message.guild.id)
        
        for trigger, config in autoresponders.items():
            pattern = config["pattern"]
            message_content = message.content.lower()
            
            should_respond = False
            
            if pattern == "exact" and message_content == trigger:
                should_respond = True
            elif pattern == "starts with" and message_content.startswith(trigger):
                should_respond = True
            elif pattern == "contains" and trigger in message_content:
                should_respond = True
            elif pattern == "regex":
                import re
                try:
                    if re.search(trigger, message_content):
                        should_respond = True
                except:
                    pass
            
            if should_respond:
                embed = discord.Embed(
                    title=config["title"],
                    description=config["description"],
                    color=int(config["color"].replace("#", ""), 16)
                )
                
                if config.get("author"):
                    embed.set_author(name=config["author"])
                
                if config.get("thumbnail"):
                    embed.set_thumbnail(url=config["thumbnail"])
                
                await message.channel.send(embed=embed)
                break
    
    @commands.hybrid_group(name="autoresponder")
    async def autoresponder_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `autoresponder create` to create a new autoresponder.")
    
    @autoresponder_group.command(name="create")
    @app_commands.describe(trigger="The trigger word/phrase for the autoresponder")
    async def create_autoresponder(self, ctx, trigger: str):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🎯 Pattern Selection",
            description=f"**Creating trigger:** `{trigger}`\n\nChoose how this trigger should match incoming messages:\n\n📋 **Available Patterns**\n\n🎯 **Exact** → Message must match exactly\n🔤 **Starts With** → Message begins with trigger\n🔍 **Contains** → Message contains trigger anywhere\n⚙️ **Regex** → Advanced pattern matching\n\n⏱️ **Timeout**\nThis selection expires in **15 minutes**",
            color=0x7289da
        )
        
        view = PatternSelectView(trigger)
        await ctx.send(embed=embed, view=view)
    
    @autoresponder_group.command(name="delete")
    @app_commands.describe(trigger="The trigger to delete")
    async def delete_autoresponder(self, ctx, trigger: str):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        success = await self.bot.db.delete_autoresponder(ctx.guild.id, trigger.lower())
        
        if success:
            embed = discord.Embed(
                title="🗑️ Autoresponder Deleted",
                description=f"Autoresponder for trigger `{trigger}` has been deleted.",
                color=0xff0000
            )
        else:
            embed = discord.Embed(
                title="❌ Not Found",
                description=f"No autoresponder found for trigger `{trigger}`.",
                color=0xff0000
            )
        
        await ctx.send(embed=embed)
    
    @autoresponder_group.command(name="list")
    async def list_autoresponders(self, ctx):
        autoresponders = await self.bot.db.get_autoresponders(ctx.guild.id)
        
        view = AutoresponderListView(autoresponders)
        embed = view.get_embed()
        
        await ctx.send(embed=embed, view=view)
    
    @autoresponder_group.command(name="edit")
    async def edit_autoresponder(self, ctx):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("You need 'Manage Messages' permission to use this command.")
            return
        
        autoresponders = await self.bot.db.get_autoresponders(ctx.guild.id)
        
        if not autoresponders:
            embed = discord.Embed(
                title="❌ No Autoresponders",
                description="No autoresponders found in this server. Use `/autoresponder create` to create one.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="✏️ Trigger Editor",
            description=f"Select the trigger you want to modify from the dropdown menu below.\n\n📊 **Available Triggers**\n**{len(autoresponders)}** triggers ready for editing\n\n⏱️ **Timeout**\nSelection expires in **15 minutes**",
            color=0x7289da
        )
        
        view = TriggerSelectView(autoresponders, self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AutoResponder(bot))