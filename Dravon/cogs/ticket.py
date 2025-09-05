import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio
from utils.embed_utils import add_dravon_footer

class TicketSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="Choose a ticket setting to configure...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set the embed title for ticket panel", value="title"),
            discord.SelectOption(label="📄 Description", description="Set the panel description", value="description"),
            discord.SelectOption(label="🎨 Color", description="Set the embed color (hex code)", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Add an image banner to the panel", value="image"),
            discord.SelectOption(label="📑 Footer", description="Set custom footer text", value="footer"),
            discord.SelectOption(label="📂 Add Category", description="Add a single ticket category", value="category"),
            discord.SelectOption(label="📂 Add Multiple Categories", description="Add multiple ticket categories at once", value="multiple_categories"),
            discord.SelectOption(label="📁 Category Channels", description="Auto-create category channels for tickets", value="auto_categories"),
            discord.SelectOption(label="📨 Send Panel", description="Send ticket panel to a channel", value="send_panel")
        ]
    )
    async def ticket_setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        setting = select.values[0]
        
        if setting == "title":
            embed = discord.Embed(
                title="📝 Set Ticket Panel Title",
                description="Please type the title for the ticket panel in chat.\n\n**Example:** `Need Help? Open a Ticket!`",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_ticket_setting(self.guild_id, "title", msg.content)
                
                embed = discord.Embed(
                    title="✅ Ticket Panel Title Set",
                    description=f"Ticket panel title has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "ticket")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "description":
            embed = discord.Embed(
                title="📄 Set Ticket Panel Description",
                description="Please type the description for the ticket panel in chat.\n\n**Example:** `Select a category below to create your ticket.`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_ticket_setting(self.guild_id, "description", msg.content)
                
                embed = discord.Embed(
                    title="✅ Ticket Panel Description Set",
                    description=f"Ticket panel description has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "ticket")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "color":
            embed = discord.Embed(
                title="🎨 Set Ticket Panel Color",
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
                    await interaction.client.db.set_ticket_setting(self.guild_id, "color", color_input)
                    
                    embed = discord.Embed(
                        title="✅ Ticket Panel Color Set",
                        description=f"Ticket panel color has been set to: `{color_input}`",
                        color=int(color_input[1:], 16)
                    )
                    from cogs.boost import BackToSetupView
                    view = BackToSetupView(self.bot, self.guild_id, "ticket")
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid hex color format. Please use format like `#ff0000`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "image":
            embed = discord.Embed(
                title="🖼️ Set Ticket Panel Image",
                description="Please provide an image URL in chat.\n\n**Example:**\n`https://example.com/banner.png`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_ticket_setting(self.guild_id, "image", msg.content)
                
                embed = discord.Embed(
                    title="✅ Ticket Panel Image Set",
                    description=f"Ticket panel image has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "ticket")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "footer":
            embed = discord.Embed(
                title="📑 Set Ticket Panel Footer",
                description="Please type the footer text in chat.\n\n**Example:** `Support Team - Always here to help!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_ticket_setting(self.guild_id, "footer", msg.content)
                
                embed = discord.Embed(
                    title="✅ Ticket Panel Footer Set",
                    description=f"Ticket panel footer has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "ticket")
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "multiple_categories":
            embed = discord.Embed(
                title="📂 Add Multiple Ticket Categories",
                description="Please type multiple categories, one per line in this format:\n`emoji name - description`\n\n**Example:**\n```\n💰 Billing - Payment and subscription issues\n🛠️ Support - General help and questions\n❓ Other - Everything else\n```",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=120.0, check=check)
                categories_input = msg.content.strip().split('\n')
                
                added_categories = []
                for category_line in categories_input:
                    category_line = category_line.strip()
                    if " - " in category_line:
                        parts = category_line.split(" - ", 1)
                        emoji_name = parts[0].strip()
                        description = parts[1].strip()
                        
                        category = {
                            "label": emoji_name,
                            "description": description,
                            "value": emoji_name.lower().replace(" ", "_").replace("💰", "billing").replace("🛠️", "support").replace("❓", "other")
                        }
                        
                        await interaction.client.db.add_ticket_category(self.guild_id, category)
                        added_categories.append(emoji_name)
                
                if added_categories:
                    embed = discord.Embed(
                        title="✅ Multiple Ticket Categories Added",
                        description=f"Added {len(added_categories)} categories:\n" + "\n".join([f"• {cat}" for cat in added_categories]),
                        color=0x00ff00
                    )
                    from cogs.boost import BackToSetupView
                    view = BackToSetupView(self.bot, self.guild_id, "ticket")
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("No valid categories found. Please use format: `emoji name - description`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "category":
            embed = discord.Embed(
                title="📂 Add Ticket Category",
                description="Please type the category details in this format:\n`emoji name - description`\n\n**Examples:**\n`💰 Billing - Payment and subscription issues`\n`🛠️ Support - General help and questions`\n`❓ Other - Everything else`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                category_input = msg.content.strip()
                
                # Parse category format: "emoji name - description"
                if " - " in category_input:
                    parts = category_input.split(" - ", 1)
                    emoji_name = parts[0].strip()
                    description = parts[1].strip()
                    
                    category = {
                        "label": emoji_name,
                        "description": description,
                        "value": emoji_name.lower().replace(" ", "_")
                    }
                    
                    await interaction.client.db.add_ticket_category(self.guild_id, category)
                    
                    embed = discord.Embed(
                        title="✅ Ticket Category Added",
                        description=f"Category added:\n**{emoji_name}**\n{description}",
                        color=0x00ff00
                    )
                    from cogs.boost import BackToSetupView
                    view = BackToSetupView(self.bot, self.guild_id, "ticket")
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid format. Please use: `emoji name - description`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "auto_categories":
            config = await interaction.client.db.get_ticket_config(self.guild_id)
            categories = config.get("categories", []) if config else []
            
            if not categories:
                embed = discord.Embed(
                    title="❌ No Categories Found",
                    description="Please add ticket categories first before creating category channels.",
                    color=0xff0000
                )
                from cogs.boost import BackToSetupView
                view = BackToSetupView(self.bot, self.guild_id, "ticket")
                await interaction.response.edit_message(embed=embed, view=view)
                return
            
            created_categories = []
            for cat in categories:
                category_name = f"{cat['label'].replace(' ', '-')}-Category"
                
                # Check if category already exists
                existing = discord.utils.get(interaction.guild.categories, name=category_name)
                if not existing:
                    try:
                        new_category = await interaction.guild.create_category(
                            name=category_name,
                            overwrites={
                                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False)
                            }
                        )
                        created_categories.append(category_name)
                        await interaction.client.db.set_ticket_category_channel(self.guild_id, cat['value'], new_category.id)
                    except Exception as e:
                        continue
            
            if created_categories:
                embed = discord.Embed(
                    title="✅ Category Channels Created",
                    description=f"Created {len(created_categories)} category channels:\n" + "\n".join([f"• {cat}" for cat in created_categories]),
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="ℹ️ No New Categories Created",
                    description="All category channels already exist.",
                    color=0x7289da
                )
            
            from cogs.boost import BackToSetupView
            view = BackToSetupView(self.bot, self.guild_id, "ticket")
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif setting == "send_panel":
            embed = discord.Embed(
                title="📨 Send Ticket Panel",
                description="Please select the channel where you want to send the ticket panel.",
                color=0x7289da
            )
            view = TicketChannelSelectView(self.bot, self.guild_id)
            await interaction.response.edit_message(embed=embed, view=view)

class TicketChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select channel for ticket panel...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        await interaction.response.defer()
        
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        config = await interaction.client.db.get_ticket_config(self.guild_id)
        
        print(f"DEBUG: Channel selected: {channel.name} ({channel.id})")
        print(f"DEBUG: Config retrieved: {config}")
        
        if not config:
            await interaction.followup.send("Please configure the ticket panel first. Use the setup options to add at least a title and category.", ephemeral=True)
            return
        
        # Create ticket panel
        title = config.get("title", "🎟️ Support Tickets")
        description = config.get("description", "Select a category below to create your ticket.")
        color = config.get("color", "#7289da")
        image = config.get("image")
        footer = config.get("footer")
        categories = config.get("categories", [])
        
        embed = discord.Embed(
            title=title,
            description=description,
            color=int(color[1:], 16) if color.startswith('#') else 0x7289da
        )
        
        if image:
            embed.set_image(url=image)
        
        if footer:
            embed.set_footer(text=footer)
        
        # Create ticket panel view
        panel_view = TicketPanelView(categories)
        
        print(f"DEBUG: About to send panel to {channel.name}")
        
        try:
            sent_message = await channel.send(embed=embed, view=panel_view)
            print(f"DEBUG: Panel sent successfully! Message ID: {sent_message.id}")
        except Exception as e:
            print(f"DEBUG: Failed to send panel: {str(e)}")
            await interaction.followup.send(f"Failed to send ticket panel: {str(e)}", ephemeral=True)
            return
        
        success_embed = discord.Embed(
            title="✅ Ticket Panel Sent",
            description=f"Ticket panel has been sent to {channel.mention}",
            color=0x00ff00
        )
        from cogs.boost import BackToSetupView
        back_view = BackToSetupView(self.bot, self.guild_id, "ticket")
        await interaction.edit_original_response(embed=success_embed, view=back_view)

class TicketPanelView(discord.ui.View):
    def __init__(self, categories):
        super().__init__(timeout=None)
        self.categories = categories
        
        if categories and len(categories) > 0:
            options = []
            for cat in categories[:25]:  # Discord limit
                options.append(discord.SelectOption(
                    label=cat["label"],
                    description=cat["description"],
                    value=cat["value"]
                ))
            
            if options:  # Only add select if we have valid options
                select = discord.ui.Select(
                    placeholder="Select a ticket category...",
                    options=options,
                    custom_id="ticket_category_select"
                )
                select.callback = self.category_callback
                self.add_item(select)
        else:
            # Add a button for general tickets if no categories
            button = discord.ui.Button(
                label="Create Ticket",
                style=discord.ButtonStyle.primary,
                emoji="🎟️",
                custom_id="create_general_ticket"
            )
            button.callback = self.create_general_ticket
            self.add_item(button)
    
    async def create_general_ticket(self, interaction: discord.Interaction):
        await self.create_ticket(interaction, "General")
    
    async def category_callback(self, interaction: discord.Interaction):
        category = interaction.data["values"][0]
        await self.create_ticket(interaction, category)
    
    async def create_ticket(self, interaction: discord.Interaction, category: str):
        # Check if user already has a ticket
        guild = interaction.guild
        existing_ticket = discord.utils.get(guild.channels, name=f"ticket-{interaction.user.name.lower()}")
        
        if existing_ticket:
            await interaction.response.send_message("You already have an open ticket!", ephemeral=True)
            return
        
        # Get category channel if exists
        config = await interaction.client.db.get_ticket_config(guild.id)
        category_channels = config.get("category_channels", {}) if config else {}
        category_id = category_channels.get(category)
        
        parent_category = None
        if category_id:
            parent_category = guild.get_channel(category_id)
        
        # Create ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Add staff roles if configured
        for member in guild.members:
            if member.guild_permissions.manage_channels:
                overwrites[member] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name.lower()}",
            overwrites=overwrites,
            category=parent_category,
            topic=f"Ticket created by {interaction.user} - Category: {category}"
        )
        
        # Send welcome message in ticket
        embed = discord.Embed(
            title="🎟️ Ticket Created",
            description=f"Hello {interaction.user.mention}!\n\nYour ticket has been created. Please describe your issue and our staff will help you shortly.\n\n**Category:** {category}",
            color=0x00ff00
        )
        
        view = TicketControlView()
        await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"Ticket created! {channel.mention}", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message("Only staff can close tickets.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {interaction.user.mention}",
            color=0xff0000
        )
        
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="ticket")
    async def ticket_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use ticket commands like `ticket setup`, `ticket config`, etc.")
    
    @ticket_group.command(name="setup")
    async def ticket_setup(self, ctx):
        """Configure ticket system"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🎟️ Ticket Setup",
            description="Create a fully customized ticket panel for your server.\n\n**Step 1:** Choose a setting from dropdown\n**Step 2:** Configure your ticket system\n**Step 3:** Send panel to a channel",
            color=0x7289da
        )
        
        view = TicketSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @ticket_group.command(name="config")
    async def ticket_config(self, ctx):
        """Display current ticket configuration"""
        config = await self.bot.db.get_ticket_config(ctx.guild.id)
        
        if not config:
            embed = discord.Embed(
                title="🎟️ Ticket Configuration",
                description="No ticket configuration found. Use `/ticket setup` to configure.",
                color=0x7289da
            )
        else:
            title = config.get("title", "Not set")
            description = config.get("description", "Not set")
            color = config.get("color", "#7289da")
            image = config.get("image", "Not set")
            footer = config.get("footer", "Not set")
            categories = config.get("categories", [])
            
            categories_text = "\n".join([f"• {cat['label']}" for cat in categories]) if categories else "None"
            
            embed = discord.Embed(
                title="🎟️ Ticket Configuration",
                description=f"**Title:** {title}\n**Description:** {description}\n**Color:** {color}\n**Image:** {image}\n**Footer:** {footer}\n**Categories:**\n{categories_text}",
                color=int(color[1:], 16) if color.startswith('#') else 0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @ticket_group.command(name="logs")
    async def ticket_logs(self, ctx, channel: discord.TextChannel = None):
        """Set ticket logs channel"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        if channel:
            await self.bot.db.set_ticket_logs_channel(ctx.guild.id, channel.id)
            embed = discord.Embed(
                title="✅ Ticket Logs Channel Set",
                description=f"Ticket logs will be sent to {channel.mention}",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="📋 Set Ticket Logs Channel",
                description="Usage: `/ticket logs #channel`\n\nThis channel will receive logs when tickets are created, closed, etc.",
                color=0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @ticket_group.command(name="add")
    async def ticket_add(self, ctx, user: discord.Member):
        """Add a user to the current ticket"""
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("Only staff can add users to tickets.")
            return
        
        # Add user to ticket channel
        overwrites = ctx.channel.overwrites
        overwrites[user] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
        
        await ctx.channel.edit(overwrites=overwrites)
        
        embed = discord.Embed(
            title="✅ User Added to Ticket",
            description=f"{user.mention} has been added to this ticket by {ctx.author.mention}",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)
    
    @ticket_group.command(name="close")
    async def ticket_close(self, ctx):
        """Close the current ticket"""
        if not ctx.channel.name.startswith("ticket-"):
            await ctx.send("This command can only be used in ticket channels.")
            return
        
        if not ctx.author.guild_permissions.manage_channels:
            await ctx.send("Only staff can close tickets.")
            return
        
        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=f"This ticket has been closed by {ctx.author.mention}",
            color=0xff0000
        )
        
        await ctx.send(embed=embed)
        await asyncio.sleep(5)
        await ctx.channel.delete()

async def setup(bot):
    await bot.add_cog(Ticket(bot))