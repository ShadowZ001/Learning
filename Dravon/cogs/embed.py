import discord
from discord.ext import commands
from discord import app_commands
import re
from datetime import datetime
from utils.embed_utils import add_dravon_footer

class EmbedSetupView(discord.ui.View):
    def __init__(self, bot, guild_id, embed_name=None):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.embed_name = embed_name
    
    @discord.ui.select(
        placeholder="Choose an embed setting to configure...",
        options=[
            discord.SelectOption(label="📝 Name of Embed", description="Set a unique identifier for the embed", value="name"),
            discord.SelectOption(label="🏷️ Title", description="Set the embed title", value="title"),
            discord.SelectOption(label="📄 Description", description="Set the embed description", value="description"),
            discord.SelectOption(label="🎨 Color", description="Pick a color (hex code)", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Add an image/banner URL", value="image"),
            discord.SelectOption(label="📑 Footer", description="Set footer text", value="footer"),
            discord.SelectOption(label="💾 Save Embed", description="Save the embed configuration", value="save"),
            discord.SelectOption(label="📤 Send Embed", description="Choose a channel and send the embed", value="send")
        ]
    )
    async def embed_setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        setting = select.values[0]
        
        if setting == "name":
            embed = discord.Embed(
                title="📝 Set Embed Name",
                description="Please type a unique name for this embed in chat.\n\n**Example:** `welcome_embed`\n\n**Note:** This name will be used to save and reference the embed.",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                self.embed_name = msg.content.strip().lower().replace(" ", "_")
                
                embed = discord.Embed(
                    title="✅ Embed Name Set",
                    description=f"Embed name has been set to: `{self.embed_name}`",
                    color=0x00ff00
                )
                embed = add_dravon_footer(embed)
                view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "title":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🏷️ Set Embed Title",
                description="Please type the title for the embed in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's name\n`{server}` - Server name\n`{member_count}` - Current member count\n`{date}` - Current date\n\n**Example:** `Welcome to {server}!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_embed_setting(self.guild_id, self.embed_name, "title", msg.content)
                
                embed = discord.Embed(
                    title="✅ Embed Title Set",
                    description=f"Embed title has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "description":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📄 Set Embed Description",
                description="Please type the description for the embed in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's name\n`{server}` - Server name\n`{member_count}` - Current member count\n`{date}` - Current date\n\n**Example:** `Hello {user}, we're glad you joined {server}!`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_embed_setting(self.guild_id, self.embed_name, "description", msg.content)
                
                embed = discord.Embed(
                    title="✅ Embed Description Set",
                    description=f"Embed description has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "color":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🎨 Set Embed Color",
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
                    await interaction.client.db.set_embed_setting(self.guild_id, self.embed_name, "color", color_input)
                    
                    embed = discord.Embed(
                        title="✅ Embed Color Set",
                        description=f"Embed color has been set to: `{color_input}`",
                        color=int(color_input[1:], 16)
                    )
                    view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                    await msg.reply(embed=embed, view=view)
                else:
                    await msg.reply("Invalid hex color format. Please use format like `#ff0000`")
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "image":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🖼️ Set Embed Image",
                description="Please provide an image URL in chat.\n\n**Example:**\n`https://example.com/banner.png`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_embed_setting(self.guild_id, self.embed_name, "image", msg.content)
                
                embed = discord.Embed(
                    title="✅ Embed Image Set",
                    description=f"Embed image has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "footer":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📑 Set Embed Footer",
                description="Please type the footer text in chat.\n\n**Variables:**\n`{user}` - Mentions the user\n`{username}` - User's name\n`{server}` - Server name\n`{member_count}` - Current member count\n`{date}` - Current date\n\n**Example:** `Made with ❤️ by {server}`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=60.0, check=check)
                await interaction.client.db.set_embed_setting(self.guild_id, self.embed_name, "footer", msg.content)
                
                embed = discord.Embed(
                    title="✅ Embed Footer Set",
                    description=f"Embed footer has been set to:\n`{msg.content}`",
                    color=0x00ff00
                )
                view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
                await msg.reply(embed=embed, view=view)
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif setting == "save":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            config = await interaction.client.db.get_embed_config(self.guild_id, self.embed_name)
            if not config or not config.get("title"):
                await interaction.response.send_message("Please set at least a title before saving!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="✅ Embed Saved",
                description=f"Embed `{self.embed_name}` has been saved successfully!\n\nYou can now use:\n• `/embed list` to see all saved embeds\n• `/embed edit {self.embed_name}` to edit this embed\n• Use 'Send Embed' option to send it to a channel",
                color=0x00ff00
            )
            view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif setting == "send":
            if not self.embed_name:
                await interaction.response.send_message("Please set an embed name first!", ephemeral=True)
                return
            
            config = await interaction.client.db.get_embed_config(self.guild_id, self.embed_name)
            if not config:
                await interaction.response.send_message("Please configure and save the embed first!", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📤 Send Embed",
                description="Please select the channel where you want to send the embed.",
                color=0x7289da
            )
            view = EmbedChannelSelectView(self.bot, self.guild_id, self.embed_name)
            await interaction.response.edit_message(embed=embed, view=view)

class EmbedChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id, embed_name):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.embed_name = embed_name
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select channel to send embed...")
    async def channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        await interaction.response.defer()
        
        selected_channel = select.values[0]
        channel = interaction.guild.get_channel(selected_channel.id)
        config = await interaction.client.db.get_embed_config(self.guild_id, self.embed_name)
        
        if not config:
            await interaction.followup.send("Embed configuration not found!", ephemeral=True)
            return
        
        # Create embed with variables replaced
        title = self.replace_variables(config.get("title", ""), interaction.user, interaction.guild)
        description = self.replace_variables(config.get("description", ""), interaction.user, interaction.guild)
        footer = self.replace_variables(config.get("footer", ""), interaction.user, interaction.guild)
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
        
        try:
            await channel.send(embed=embed)
            
            success_embed = discord.Embed(
                title="✅ Embed Sent",
                description=f"Embed `{self.embed_name}` has been sent to {channel.mention}",
                color=0x00ff00
            )
            view = EmbedSetupView(self.bot, self.guild_id, self.embed_name)
            await interaction.edit_original_response(embed=success_embed, view=view)
        except Exception as e:
            await interaction.followup.send(f"Failed to send embed: {str(e)}", ephemeral=True)
    
    def replace_variables(self, text: str, user: discord.Member, guild: discord.Guild) -> str:
        if not text:
            return text
        
        replacements = {
            "{user}": user.mention,
            "{username}": user.display_name,
            "{server}": guild.name,
            "{member_count}": str(guild.member_count),
            "{date}": datetime.now().strftime("%B %d, %Y")
        }
        
        for var, replacement in replacements.items():
            text = text.replace(var, replacement)
        
        return text

class EmbedDeleteView(discord.ui.View):
    def __init__(self, bot, guild_id, embeds):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.embeds = embeds
        
        # Create dropdown with embed options
        options = []
        for embed_name in list(embeds.keys())[:25]:  # Discord limit
            options.append(discord.SelectOption(
                label=embed_name,
                description=f"Delete {embed_name} embed",
                value=embed_name
            ))
        
        if options:
            self.add_item(EmbedDeleteSelect(options))
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📜 Embed Management",
            description="Use embed commands like `embed setup`, `embed list`, etc.",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)

class EmbedDeleteSelect(discord.ui.Select):
    def __init__(self, options):
        super().__init__(placeholder="Select an embed to delete...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        embed_name = self.values[0]
        
        # Confirmation view
        view = EmbedDeleteConfirmView(interaction.client, interaction.guild.id, embed_name)
        
        embed = discord.Embed(
            title="⚠️ Confirm Deletion",
            description=f"Are you sure you want to delete the embed `{embed_name}`?\n\nThis action cannot be undone.",
            color=0xff8c00
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class EmbedDeleteConfirmView(discord.ui.View):
    def __init__(self, bot, guild_id, embed_name):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.embed_name = embed_name
    
    @discord.ui.button(label="🗑️ Delete", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        success = await self.bot.db.delete_embed(self.guild_id, self.embed_name)
        
        if success:
            embed = discord.Embed(
                title="✅ Embed Deleted",
                description=f"Embed `{self.embed_name}` has been successfully deleted.",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Delete Failed",
                description=f"Failed to delete embed `{self.embed_name}`.",
                color=0xff0000
            )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    @discord.ui.button(label="🔙 Back", style=discord.ButtonStyle.secondary)
    async def back_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Go back to embed list
        embeds = await self.bot.db.get_all_embeds(self.guild_id)
        
        if not embeds:
            embed = discord.Embed(
                title="📜 No Embeds Found",
                description="No saved embeds found. Use `/embed setup` to create one.",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="🗑️ Delete Embed",
                description="Select an embed from the dropdown to delete it.",
                color=0xff6b6b
            )
            view = EmbedDeleteView(self.bot, self.guild_id, embeds)
            await interaction.response.edit_message(embed=embed, view=view)

class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def replace_variables(self, text: str, user: discord.Member, guild: discord.Guild) -> str:
        if not text:
            return text
        
        replacements = {
            "{user}": user.mention,
            "{username}": user.display_name,
            "{server}": guild.name,
            "{member_count}": str(guild.member_count),
            "{date}": datetime.now().strftime("%B %d, %Y")
        }
        
        for var, replacement in replacements.items():
            text = text.replace(var, replacement)
        
        return text
    
    @commands.hybrid_group(name="embed")
    async def embed_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use embed commands like `embed setup`, `embed list`, etc.")
    
    @embed_group.command(name="setup")
    async def embed_setup(self, ctx):
        """Create a custom embed with dropdown setup"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🛠️ Embed Builder",
            description="Customize and build your embed messages interactively.\nUse the dropdown options below to configure your embed.",
            color=0x7289da
        )
        
        view = EmbedSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @embed_group.command(name="list")
    async def embed_list(self, ctx):
        """Shows all saved embeds"""
        embeds = await self.bot.db.get_all_embeds(ctx.guild.id)
        
        if not embeds:
            embed = discord.Embed(
                title="📜 Saved Embeds",
                description="No saved embeds found. Use `/embed setup` to create one.",
                color=0x7289da
            )
        else:
            embed_list = "\n".join([f"• {name}" for name in embeds.keys()])
            embed = discord.Embed(
                title="📜 Saved Embeds",
                description=embed_list,
                color=0x7289da
            )
        
        await ctx.send(embed=embed)
    
    @embed_group.command(name="delete")
    async def embed_delete(self, ctx):
        """Delete saved embeds with dropdown selection"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embeds = await self.bot.db.get_all_embeds(ctx.guild.id)
        
        if not embeds:
            embed = discord.Embed(
                title="📜 No Embeds Found",
                description="No saved embeds found. Use `/embed setup` to create one.",
                color=0x7289da
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🗑️ Delete Embed",
            description="Select an embed from the dropdown to delete it.",
            color=0xff6b6b
        )
        
        view = EmbedDeleteView(self.bot, ctx.guild.id, embeds)
        await ctx.send(embed=embed, view=view)
    
    @embed_group.command(name="edit")
    async def embed_edit(self, ctx, name: str):
        """Loads a saved embed and reopens the setup dropdown flow for editing"""
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        config = await self.bot.db.get_embed_config(ctx.guild.id, name.lower())
        
        if not config:
            embed = discord.Embed(
                title="❌ Embed Not Found",
                description=f"No embed named `{name}` was found.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🛠️ Edit Embed",
            description=f"Editing embed: `{name}`\n\nUse the dropdown options below to modify your embed.",
            color=0x7289da
        )
        
        view = EmbedSetupView(self.bot, ctx.guild.id, name.lower())
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Embed(bot))