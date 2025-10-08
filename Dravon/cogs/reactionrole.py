import discord
from discord.ext import commands
import re

class ReactionRoleSetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=1200)  # 20 minutes
        self.bot = bot
        self.guild_id = guild_id
        self.config = {"reaction_roles": []}
    
    @discord.ui.select(
        placeholder="Configure reaction role embed...",
        options=[
            discord.SelectOption(label="📝 Title", description="Set embed title", value="title"),
            discord.SelectOption(label="📄 Description", description="Set embed description", value="description"),
            discord.SelectOption(label="🎨 Hex Color", description="Set embed color (optional)", value="color"),
            discord.SelectOption(label="🖼️ Image", description="Set embed image (optional)", value="image"),
            discord.SelectOption(label="📑 Footer", description="Set embed footer (optional)", value="footer"),
            discord.SelectOption(label="⚡ Reaction Roles", description="Add emoji-role pairs", value="reactions"),
            discord.SelectOption(label="📤 Save & Send", description="Save and send to channel", value="send")
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
        elif value == "footer":
            modal = FooterModal(self)
            await interaction.response.send_modal(modal)
        elif value == "reactions":
            embed = discord.Embed(
                title="⚡ Add Reaction Role",
                description="Please type an emoji in chat, then mention the role for that emoji.\n\n**Format:** `😀 @Role Name`\n**Example:** `🎮 @Gamer`",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            def check(message):
                return message.author == interaction.user and message.channel == interaction.channel
            
            try:
                msg = await interaction.client.wait_for('message', timeout=300.0, check=check)
                parts = msg.content.split(None, 1)
                
                if len(parts) < 2:
                    await msg.reply("Invalid format! Use: `emoji @role`")
                    return
                
                emoji = parts[0]
                role_mention = parts[1]
                
                # Extract role from mention
                role_id = re.search(r'<@&(\d+)>', role_mention)
                if role_id:
                    role = interaction.guild.get_role(int(role_id.group(1)))
                else:
                    role = discord.utils.get(interaction.guild.roles, name=role_mention.strip('@'))
                
                if not role:
                    await msg.reply("Role not found!")
                    return
                
                self.config["reaction_roles"].append({"emoji": emoji, "role_id": role.id})
                
                view = ReactionRoleAddMoreView(self, emoji, role)
                embed = discord.Embed(
                    title="✅ Reaction Role Added",
                    description=f"Added: {emoji} → {role.mention}",
                    color=0x00ff00
                )
                await msg.reply(embed=embed, view=view)
                
            except:
                await interaction.followup.send("Setup timed out. Please try again.")
        
        elif value == "send":
            if not self.config.get("title") or not self.config.get("reaction_roles"):
                await interaction.response.send_message("Please set title and add reaction roles first!", ephemeral=True)
                return
            
            view = ChannelSelectView(self.bot, self.guild_id, self.config)
            embed = discord.Embed(
                title="📤 Select Channel",
                description="Choose where to send the reaction role embed.",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=view)

class ReactionRoleAddMoreView(discord.ui.View):
    def __init__(self, setup_view, emoji, role):
        super().__init__(timeout=1200)  # 20 minutes
        self.setup_view = setup_view
        self.emoji = emoji
        self.role = role
    
    @discord.ui.button(label="➕ Add More", style=discord.ButtonStyle.primary)
    async def add_more(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="⚡ Add Another Reaction Role",
            description="Please type an emoji in chat, then mention the role for that emoji.\n\n**Format:** `😀 @Role Name`\n**Example:** `🎮 @Gamer`",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=None)
        
        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel
        
        try:
            msg = await interaction.client.wait_for('message', timeout=300.0, check=check)
            parts = msg.content.split(None, 1)
            
            if len(parts) < 2:
                await msg.reply("Invalid format! Use: `emoji @role`")
                return
            
            emoji = parts[0]
            role_mention = parts[1]
            
            # Extract role from mention
            role_id = re.search(r'<@&(\d+)>', role_mention)
            if role_id:
                role = interaction.guild.get_role(int(role_id.group(1)))
            else:
                role = discord.utils.get(interaction.guild.roles, name=role_mention.strip('@'))
            
            if not role:
                await msg.reply("Role not found!")
                return
            
            self.setup_view.config["reaction_roles"].append({"emoji": emoji, "role_id": role.id})
            
            view = ReactionRoleAddMoreView(self.setup_view, emoji, role)
            embed = discord.Embed(
                title="✅ Reaction Role Added",
                description=f"Added: {emoji} → {role.mention}",
                color=0x00ff00
            )
            await msg.reply(embed=embed, view=view)
            
        except:
            await interaction.followup.send("Setup timed out. Please try again.")
    
    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.success)
    async def save(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛠️ Reaction Role Setup",
            description="Continue configuring your reaction role embed.",
            color=0x7289da
        )
        await interaction.response.edit_message(embed=embed, view=self.setup_view)

class TitleModal(discord.ui.Modal, title="Set Reaction Role Title"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    title_input = discord.ui.TextInput(
        label="Embed Title",
        placeholder="Enter reaction role embed title...",
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

class DescriptionModal(discord.ui.Modal, title="Set Reaction Role Description"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    desc_input = discord.ui.TextInput(
        label="Embed Description",
        placeholder="Enter reaction role embed description...",
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
        placeholder="Enter hex color (e.g., #7289da) or leave empty...",
        required=False,
        max_length=7
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        if self.color_input.value:
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
            else:
                await interaction.response.send_message("Invalid hex color format!", ephemeral=True)
                return
        else:
            self.view.config["color"] = None
            embed = discord.Embed(
                title="✅ Color Cleared",
                description="Color set to default",
                color=0x00ff00
            )
        
        await interaction.response.edit_message(embed=embed, view=self.view)

class ImageModal(discord.ui.Modal, title="Set Embed Image"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    image_input = discord.ui.TextInput(
        label="Image URL",
        placeholder="Enter image URL or leave empty...",
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

class FooterModal(discord.ui.Modal, title="Set Embed Footer"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    footer_input = discord.ui.TextInput(
        label="Footer Text",
        placeholder="Enter footer text or leave empty...",
        required=False,
        max_length=2048
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        self.view.config["footer"] = self.footer_input.value or None
        embed = discord.Embed(
            title="✅ Footer Set",
            description=f"Footer: `{self.footer_input.value or 'None'}`",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=self.view)

class ChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id, config):
        super().__init__(timeout=1200)  # 20 minutes
        self.bot = bot
        self.guild_id = guild_id
        self.config = config
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)
        
        # Create reaction role embed
        embed = discord.Embed(
            title=self.config["title"],
            description=self.config.get("description", ""),
            color=int(self.config.get("color", "#7289da")[1:], 16) if self.config.get("color") else 0x7289da
        )
        
        if self.config.get("image"):
            embed.set_image(url=self.config["image"])
        
        if self.config.get("footer"):
            embed.set_footer(text=self.config["footer"])
        
        # Don't add extra text to description
        
        try:
            message = await channel.send(embed=embed)
            
            # Add reactions
            for rr in self.config["reaction_roles"]:
                try:
                    await message.add_reaction(rr["emoji"])
                except:
                    pass
            
            # Save to database
            self.config["message_id"] = message.id
            self.config["channel_id"] = channel.id
            await self.bot.db.add_reaction_role(self.guild_id, self.config)
            
            success_embed = discord.Embed(
                title="✅ Reaction Role Setup Complete",
                description=f"Reaction role embed sent to {channel.mention}",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=success_embed, view=None)
        except Exception as e:
            await interaction.response.send_message(f"Failed to send embed: {str(e)}", ephemeral=True)

class ReactionRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Skip bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        try:
            # Get guild and member
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            member = guild.get_member(payload.user_id)
            if not member:
                return
            
            # Get all reaction role configs for this guild
            reaction_roles = await self.bot.db.get_reaction_roles(payload.guild_id)
            if not reaction_roles:
                return
            
            # Check each config
            for config in reaction_roles:
                # Match message and channel
                if (config.get("message_id") == payload.message_id and 
                    config.get("channel_id") == payload.channel_id):
                    
                    # Check each reaction role in this config
                    for rr in config.get("reaction_roles", []):
                        # Format emoji for comparison
                        if payload.emoji.id:
                            # Custom emoji: <:name:id>
                            emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
                        else:
                            # Unicode emoji
                            emoji_str = str(payload.emoji)
                        
                        # Check if emoji matches
                        if emoji_str == rr.get("emoji"):
                            # Get the role
                            role = guild.get_role(rr.get("role_id"))
                            if not role:
                                continue
                            
                            # Add role if user doesn't have it
                            if role not in member.roles:
                                try:
                                    await member.add_roles(role, reason="Reaction Role")
                                    print(f"Added role {role.name} to {member.display_name}")
                                except Exception as e:
                                    print(f"Failed to add role {role.name}: {e}")
                            return
        
        except Exception as e:
            print(f"Reaction role error: {e}")
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Skip bot reactions
        if payload.user_id == self.bot.user.id:
            return
        
        try:
            # Get guild and member
            guild = self.bot.get_guild(payload.guild_id)
            if not guild:
                return
            
            member = guild.get_member(payload.user_id)
            if not member:
                return
            
            # Get all reaction role configs for this guild
            reaction_roles = await self.bot.db.get_reaction_roles(payload.guild_id)
            if not reaction_roles:
                return
            
            # Check each config
            for config in reaction_roles:
                # Match message and channel
                if (config.get("message_id") == payload.message_id and 
                    config.get("channel_id") == payload.channel_id):
                    
                    # Check each reaction role in this config
                    for rr in config.get("reaction_roles", []):
                        # Format emoji for comparison
                        if payload.emoji.id:
                            # Custom emoji: <:name:id>
                            emoji_str = f"<:{payload.emoji.name}:{payload.emoji.id}>"
                        else:
                            # Unicode emoji
                            emoji_str = str(payload.emoji)
                        
                        # Check if emoji matches
                        if emoji_str == rr.get("emoji"):
                            # Get the role
                            role = guild.get_role(rr.get("role_id"))
                            if not role:
                                continue
                            
                            # Remove role if user has it
                            if role in member.roles:
                                try:
                                    await member.remove_roles(role, reason="Reaction Role Removed")
                                    print(f"Removed role {role.name} from {member.display_name}")
                                except Exception as e:
                                    print(f"Failed to remove role {role.name}: {e}")
                            return
        
        except Exception as e:
            print(f"Reaction role remove error: {e}")
    
    @commands.hybrid_group(name="reaction")
    async def reaction_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `/reaction role setup`, `/reaction role list`, or `/reaction role reset`")
    
    @reaction_group.group(name="role")
    async def reaction_role_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `/reaction role setup`, `/reaction role list`, or `/reaction role reset`")
    
    @reaction_role_group.command(name="setup")
    async def reaction_role_setup(self, ctx):
        """Setup reaction roles"""
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="⚡ Reaction Role Setup",
            description="Configure your reaction role system using the dropdown below.",
            color=0x7289da
        )
        
        view = ReactionRoleSetupView(self.bot, ctx.guild.id)
        await ctx.send(embed=embed, view=view)
    
    @reaction_role_group.command(name="list")
    async def reaction_role_list(self, ctx):
        """List all reaction role setups"""
        reaction_roles = await self.bot.db.get_reaction_roles(ctx.guild.id)
        
        if not reaction_roles:
            embed = discord.Embed(
                title="📝 Reaction Roles",
                description="No reaction role setups found.",
                color=0x7289da
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="📝 Reaction Role Setups",
            description=f"Found {len(reaction_roles)} reaction role setup(s)",
            color=0x7289da
        )
        
        for i, rr_config in enumerate(reaction_roles[:5], 1):  # Show first 5
            channel = ctx.guild.get_channel(rr_config["channel_id"])
            roles_text = []
            for rr in rr_config["reaction_roles"]:
                role = ctx.guild.get_role(rr["role_id"])
                if role:
                    roles_text.append(f"{rr['emoji']} {role.mention}")
            
            embed.add_field(
                name=f"Setup {i}: {rr_config['title']}",
                value=f"**Channel:** {channel.mention if channel else 'Unknown'}\n**Roles:** {', '.join(roles_text[:3])}{'...' if len(roles_text) > 3 else ''}",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @reaction_role_group.command(name="reset")
    async def reaction_role_reset(self, ctx):
        """Reset all reaction role configurations"""
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        await self.bot.db.reset_reaction_roles(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ Reaction Roles Reset",
            description="All reaction role configurations have been reset.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @reaction_role_group.command(name="debug")
    async def reaction_role_debug(self, ctx):
        """Debug reaction role permissions"""
        bot_member = ctx.guild.get_member(self.bot.user.id)
        
        embed = discord.Embed(
            title="🔍 Reaction Role Debug",
            color=0x7289da
        )
        
        embed.add_field(
            name="Bot Permissions",
            value=f"Manage Roles: {bot_member.guild_permissions.manage_roles}\nAdministrator: {bot_member.guild_permissions.administrator}",
            inline=False
        )
        
        embed.add_field(
            name="Bot Role Position",
            value=f"Highest Role: {bot_member.top_role.name} (Position: {bot_member.top_role.position})",
            inline=False
        )
        
        # Show first 10 roles for comparison
        roles_info = []
        for role in sorted(ctx.guild.roles, key=lambda r: r.position, reverse=True)[:10]:
            roles_info.append(f"{role.name}: {role.position}")
        
        embed.add_field(
            name="Server Roles (Top 10)",
            value="\n".join(roles_info),
            inline=False
        )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ReactionRole(bot))