import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_utils import add_dravon_footer
import asyncio
from datetime import datetime

class WhitelistView(discord.ui.View):
    def __init__(self, bot, guild):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
    
    @discord.ui.select(
        placeholder="🔒 Manage Whitelist Permissions...",
        options=[
            discord.SelectOption(label="👥 Add User", description="Add user to whitelist", value="add_user"),
            discord.SelectOption(label="🗑️ Remove User", description="Remove user from whitelist", value="remove_user"),
            discord.SelectOption(label="📋 View Whitelist", description="View all whitelisted users", value="view_list"),
            discord.SelectOption(label="🛡️ Grant AntiNuke Access", description="Give AntiNuke setup permissions", value="grant_antinuke"),
            discord.SelectOption(label="❌ Revoke AntiNuke Access", description="Remove AntiNuke permissions", value="revoke_antinuke"),
            discord.SelectOption(label="📊 View Permissions", description="View user permissions", value="view_perms")
        ]
    )
    async def whitelist_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner can manage the whitelist system.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        value = select.values[0]
        
        if value == "add_user":
            modal = AddUserModal(self.bot, self.guild)
            await interaction.response.send_modal(modal)
        
        elif value == "remove_user":
            modal = RemoveUserModal(self.bot, self.guild)
            await interaction.response.send_modal(modal)
        
        elif value == "view_list":
            await self.show_whitelist(interaction)
        
        elif value == "grant_antinuke":
            modal = GrantAntiNukeModal(self.bot, self.guild)
            await interaction.response.send_modal(modal)
        
        elif value == "revoke_antinuke":
            modal = RevokeAntiNukeModal(self.bot, self.guild)
            await interaction.response.send_modal(modal)
        
        elif value == "view_perms":
            modal = ViewPermissionsModal(self.bot, self.guild)
            await interaction.response.send_modal(modal)
    
    async def show_whitelist(self, interaction):
        """Show all whitelisted users with animation"""
        # Loading animation
        loading_embed = discord.Embed(
            title="🔄 Loading Whitelist...",
            description="⏳ Fetching whitelisted users...",
            color=0xffd700
        )
        await interaction.response.edit_message(embed=loading_embed, view=None)
        await asyncio.sleep(1)
        
        # Get whitelist data
        whitelist_data = await self.bot.db.get_whitelist_users(self.guild.id)
        antinuke_users = await self.bot.db.get_antinuke_whitelist(self.guild.id)
        
        embed = discord.Embed(
            title="📋 Server Whitelist System",
            description=f"**🔒 Trusted Users in {self.guild.name}**\n\nWhitelisted users have special permissions and access to restricted commands.",
            color=0x7289da
        )
        
        # Always whitelisted
        embed.add_field(
            name="👑 Automatically Whitelisted",
            value=f"• **Server Owner:** <@{self.guild.owner_id}>\n• **Bot Admin:** <@1037768611126841405>",
            inline=False
        )
        
        # Manual whitelist
        if whitelist_data:
            user_list = []
            for user_id in whitelist_data[:10]:  # Show first 10
                user = self.bot.get_user(user_id)
                if user:
                    user_list.append(f"• **{user.display_name}** - {user.mention}")
                else:
                    user_list.append(f"• **Unknown User** - `{user_id}`")
            
            embed.add_field(
                name=f"✅ Manual Whitelist ({len(whitelist_data)} total)",
                value="\n".join(user_list) + (f"\n... and {len(whitelist_data) - 10} more" if len(whitelist_data) > 10 else ""),
                inline=False
            )
        else:
            embed.add_field(
                name="📝 Manual Whitelist",
                value="No manually whitelisted users.",
                inline=False
            )
        
        # AntiNuke permissions
        if antinuke_users:
            antinuke_list = []
            for user_id in antinuke_users[:5]:  # Show first 5
                user = self.bot.get_user(user_id)
                if user:
                    antinuke_list.append(f"• **{user.display_name}** - {user.mention}")
                else:
                    antinuke_list.append(f"• **Unknown User** - `{user_id}`")
            
            embed.add_field(
                name=f"🛡️ AntiNuke Access ({len(antinuke_users)} total)",
                value="\n".join(antinuke_list) + (f"\n... and {len(antinuke_users) - 5} more" if len(antinuke_users) > 5 else ""),
                inline=False
            )
        else:
            embed.add_field(
                name="🛡️ AntiNuke Access",
                value="No users have AntiNuke setup permissions.",
                inline=False
            )
        
        embed.set_footer(text=f"Total Protected Users: {len(whitelist_data or []) + len(antinuke_users or []) + 2} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        view = WhitelistView(self.bot, self.guild)
        await interaction.edit_original_response(embed=embed, view=view)

class AddUserModal(discord.ui.Modal):
    def __init__(self, bot, guild):
        super().__init__(title="Add User to Whitelist")
        self.bot = bot
        self.guild = guild
        
        self.user_input = discord.ui.TextInput(
            label="User ID or Mention",
            placeholder="Enter user ID or mention the user",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse user input
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
            else:
                user_id = int(user_input)
            
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            
            if user.bot:
                embed = discord.Embed(
                    title="❌ Cannot Whitelist Bot",
                    description="Bots cannot be added to the whitelist for security reasons.",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Add to whitelist
            await self.bot.db.add_whitelist_user(self.guild.id, user_id)
            
            embed = discord.Embed(
                title="✅ User Added to Whitelist",
                description=f"**{user.display_name}** has been successfully added to the whitelist!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="👤 User Information",
                value=f"**User:** {user.mention}\n**ID:** `{user_id}`\n**Added by:** {interaction.user.mention}",
                inline=True
            )
            
            embed.add_field(
                name="🔓 Permissions Granted",
                value="• Access to restricted commands\n• Bypass certain limitations\n• Special user status",
                inline=True
            )
            
            embed.set_thumbnail(url=user.display_avatar.url)
            embed = add_dravon_footer(embed)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid user ID or mention.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoveUserModal(discord.ui.Modal):
    def __init__(self, bot, guild):
        super().__init__(title="Remove User from Whitelist")
        self.bot = bot
        self.guild = guild
        
        self.user_input = discord.ui.TextInput(
            label="User ID or Mention",
            placeholder="Enter user ID or mention the user",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse user input
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
            else:
                user_id = int(user_input)
            
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            
            # Remove from whitelist
            success = await self.bot.db.remove_whitelist_user(self.guild.id, user_id)
            
            if success:
                embed = discord.Embed(
                    title="✅ User Removed from Whitelist",
                    description=f"**{user.display_name if user else 'Unknown User'}** has been removed from the whitelist.",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="👤 User Information",
                    value=f"**User:** {user.mention if user else f'`{user_id}`'}\n**ID:** `{user_id}`\n**Removed by:** {interaction.user.mention}",
                    inline=True
                )
                
                embed.add_field(
                    name="🔒 Permissions Revoked",
                    value="• Lost access to restricted commands\n• Subject to normal limitations\n• Regular user status",
                    inline=True
                )
            else:
                embed = discord.Embed(
                    title="⚠️ User Not Found",
                    description="The specified user is not in the whitelist.",
                    color=0xffd700
                )
            
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid user ID or mention.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class GrantAntiNukeModal(discord.ui.Modal):
    def __init__(self, bot, guild):
        super().__init__(title="Grant AntiNuke Access")
        self.bot = bot
        self.guild = guild
        
        self.user_input = discord.ui.TextInput(
            label="User ID or Mention",
            placeholder="Enter user ID or mention the user",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse user input
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
            else:
                user_id = int(user_input)
            
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            
            # Add to AntiNuke whitelist
            await self.bot.db.add_antinuke_whitelist(self.guild.id, user_id)
            
            embed = discord.Embed(
                title="🛡️ AntiNuke Access Granted",
                description=f"**{user.display_name if user else 'Unknown User'}** now has access to AntiNuke setup commands!",
                color=0x00ff00
            )
            
            embed.add_field(
                name="👤 User Information",
                value=f"**User:** {user.mention if user else f'`{user_id}`'}\n**ID:** `{user_id}`\n**Granted by:** {interaction.user.mention}",
                inline=True
            )
            
            embed.add_field(
                name="🔓 AntiNuke Permissions",
                value="• Can use `/antinuke setup`\n• Can modify AntiNuke settings\n• Can manage security features",
                inline=True
            )
            
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid user ID or mention.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class RevokeAntiNukeModal(discord.ui.Modal):
    def __init__(self, bot, guild):
        super().__init__(title="Revoke AntiNuke Access")
        self.bot = bot
        self.guild = guild
        
        self.user_input = discord.ui.TextInput(
            label="User ID or Mention",
            placeholder="Enter user ID or mention the user",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse user input
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
            else:
                user_id = int(user_input)
            
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            
            # Remove from AntiNuke whitelist
            success = await self.bot.db.remove_antinuke_whitelist(self.guild.id, user_id)
            
            if success:
                embed = discord.Embed(
                    title="🛡️ AntiNuke Access Revoked",
                    description=f"**{user.display_name if user else 'Unknown User'}** no longer has AntiNuke setup access.",
                    color=0x00ff00
                )
                
                embed.add_field(
                    name="👤 User Information",
                    value=f"**User:** {user.mention if user else f'`{user_id}`'}\n**ID:** `{user_id}`\n**Revoked by:** {interaction.user.mention}",
                    inline=True
                )
                
                embed.add_field(
                    name="🔒 Permissions Removed",
                    value="• Lost AntiNuke setup access\n• Cannot modify security settings\n• Regular user permissions only",
                    inline=True
                )
            else:
                embed = discord.Embed(
                    title="⚠️ User Not Found",
                    description="The specified user doesn't have AntiNuke access.",
                    color=0xffd700
                )
            
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid user ID or mention.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class ViewPermissionsModal(discord.ui.Modal):
    def __init__(self, bot, guild):
        super().__init__(title="View User Permissions")
        self.bot = bot
        self.guild = guild
        
        self.user_input = discord.ui.TextInput(
            label="User ID or Mention",
            placeholder="Enter user ID or mention the user",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.user_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            # Parse user input
            user_input = self.user_input.value.strip()
            if user_input.startswith('<@') and user_input.endswith('>'):
                user_id = int(user_input[2:-1].replace('!', ''))
            else:
                user_id = int(user_input)
            
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
            
            # Check permissions
            is_whitelisted = await self.bot.db.is_whitelisted(self.guild.id, user_id)
            has_antinuke = await self.bot.db.has_antinuke_access(self.guild.id, user_id)
            is_owner = user_id == self.guild.owner_id
            is_bot_admin = user_id == 1037768611126841405
            
            embed = discord.Embed(
                title="🔍 User Permissions",
                description=f"**Permission status for {user.display_name if user else 'Unknown User'}**",
                color=0x7289da
            )
            
            embed.add_field(
                name="👤 User Information",
                value=f"**User:** {user.mention if user else f'`{user_id}`'}\n**ID:** `{user_id}`\n**Status:** {'Online' if user and user.status != discord.Status.offline else 'Offline'}",
                inline=True
            )
            
            permissions = []
            if is_owner:
                permissions.append("👑 **Server Owner** - Full access")
            if is_bot_admin:
                permissions.append("🤖 **Bot Administrator** - Global access")
            if is_whitelisted:
                permissions.append("✅ **Whitelisted User** - Special access")
            if has_antinuke:
                permissions.append("🛡️ **AntiNuke Access** - Security setup")
            
            if not permissions:
                permissions.append("👤 **Regular User** - Standard access")
            
            embed.add_field(
                name="🔓 Current Permissions",
                value="\n".join(permissions),
                inline=False
            )
            
            embed.set_thumbnail(url=user.display_avatar.url if user else self.bot.user.display_avatar.url)
            embed = add_dravon_footer(embed)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid user ID or mention.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)

class WhitelistSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="whitelistmgr")
    async def whitelist_command(self, ctx):
        """Manage server whitelist system (Owner only)"""
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="**🔒 Owner Only Command**\n\nOnly the server owner can manage the whitelist system for security reasons.",
                color=0xff0000
            )
            embed.set_footer(text="Whitelist System • Security Restriction • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        
        # Loading animation
        loading_embed = discord.Embed(
            title="🔄 Loading Whitelist System...",
            description="⏳ Initializing whitelist management interface...",
            color=0xffd700
        )
        loading_embed.set_footer(text="Please wait...", icon_url=self.bot.user.display_avatar.url)
        
        message = await ctx.send(embed=loading_embed)
        await asyncio.sleep(2)
        
        embed = discord.Embed(
            title="🔒 Server Whitelist Management",
            description=f"**Welcome to the Whitelist Control Panel**\n\nManage trusted users and their permissions in **{ctx.guild.name}**.\n\n**🛡️ What is Whitelist?**\nWhitelisted users have special access to restricted commands and bypass certain limitations.",
            color=0x7289da
        )
        
        embed.add_field(
            name="⚙️ Available Actions",
            value="👥 **Add User** - Add user to whitelist\n🗑️ **Remove User** - Remove user from whitelist\n📋 **View Whitelist** - See all whitelisted users\n🛡️ **Grant AntiNuke** - Give AntiNuke setup access\n❌ **Revoke AntiNuke** - Remove AntiNuke permissions\n📊 **View Permissions** - Check user permissions\n\n**Usage:** `/whitelistmgr` or `>whitelistmgr`",
            inline=False
        )
        
        embed.add_field(
            name="🔐 Security Features",
            value="• **Owner Only Access** - Only you can manage whitelist\n• **AntiNuke Integration** - Control security setup access\n• **Permission Tracking** - Monitor user permissions\n• **Audit Logging** - Track all whitelist changes",
            inline=False
        )
        
        embed.set_thumbnail(url=ctx.guild.icon.url if ctx.guild.icon else self.bot.user.display_avatar.url)
        embed.set_footer(text="Whitelist System • Owner Control Panel • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        view = WhitelistView(self.bot, ctx.guild)
        await message.edit(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(WhitelistSystem(bot))