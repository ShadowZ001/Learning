import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_utils import add_dravon_footer
import asyncio
from datetime import datetime

class AdminHelpView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.select(
        placeholder="Select an admin category...",
        options=[
            discord.SelectOption(label="🔧 Bot Management", description="Bot control and system commands", value="bot_management"),
            discord.SelectOption(label="👑 Admin Management", description="Manage bot administrators", value="admin_management"),
            discord.SelectOption(label="💎 Premium System", description="Premium user and guild management", value="premium_system"),
            discord.SelectOption(label="📊 Statistics & Info", description="Bot statistics and information", value="statistics"),
            discord.SelectOption(label="🛠️ Maintenance", description="Bot maintenance and updates", value="maintenance"),
            discord.SelectOption(label="🔍 Debug & Testing", description="Debug tools and testing commands", value="debug"),
            discord.SelectOption(label="📝 Logs & Monitoring", description="System logs and monitoring", value="logs"),
            discord.SelectOption(label="⚙️ Configuration", description="Bot configuration and settings", value="configuration")
        ]
    )
    async def admin_help_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "bot_management":
            embed = discord.Embed(
                title="🔧 Bot Management Commands",
                description="Control and manage the bot system",
                color=0xff6b6b
            )
            embed.add_field(
                name="System Control",
                value="`/admin restart` - Restart the bot\n`/admin shutdown` - Shutdown the bot\n`/admin reload <cog>` - Reload a specific cog\n`/admin sync` - Sync slash commands\n`/admin status <status>` - Change bot status",
                inline=False
            )
            embed.add_field(
                name="Guild Management",
                value="`/admin guilds` - List all guilds\n`/admin leave <guild_id>` - Leave a guild\n`/admin guild_info <guild_id>` - Get guild information\n`/admin blacklist_guild <guild_id>` - Blacklist a guild",
                inline=False
            )
        
        elif category == "admin_management":
            embed = discord.Embed(
                title="👑 Admin Management Commands",
                description="Manage bot administrators and permissions",
                color=0xffd700
            )
            embed.add_field(
                name="Admin Control",
                value="`/admin add_admin <user_id>` - Add new bot admin\n`/admin remove_admin <user_id>` - Remove bot admin\n`/admin list_admins` - List all bot admins\n`/admin admin_info <user_id>` - Get admin information",
                inline=False
            )
            embed.add_field(
                name="Permissions",
                value="`/admin check_perms <user_id>` - Check user permissions\n`/admin grant_temp_admin <user_id>` - Grant temporary admin access",
                inline=False
            )
        
        elif category == "premium_system":
            embed = discord.Embed(
                title="💎 Premium System Commands",
                description="Manage premium users and guilds",
                color=0x9932cc
            )
            embed.add_field(
                name="Premium Users",
                value="`/admin premium_add <user_id> <duration>` - Add premium to user\n`/admin premium_remove <user_id>` - Remove premium from user\n`/admin premium_list` - List all premium users\n`/admin premium_check <user_id>` - Check premium status",
                inline=False
            )
            embed.add_field(
                name="Premium Guilds",
                value="`/admin premium_guild_add <guild_id>` - Add premium to guild\n`/admin premium_guild_remove <guild_id>` - Remove premium from guild\n`/admin premium_guild_list` - List premium guilds",
                inline=False
            )
        
        elif category == "statistics":
            embed = discord.Embed(
                title="📊 Statistics & Information Commands",
                description="Bot statistics and detailed information",
                color=0x3498db
            )
            embed.add_field(
                name="Bot Statistics",
                value="`/admin_stats` - Detailed bot statistics\n`/admin uptime` - Bot uptime information\n`/admin performance` - Performance metrics\n`/admin memory` - Memory usage statistics",
                inline=False
            )
            embed.add_field(
                name="User Statistics",
                value="`/admin user_stats <user_id>` - User statistics\n`/admin top_users` - Most active users\n`/admin user_guilds <user_id>` - User's mutual guilds",
                inline=False
            )
        
        elif category == "maintenance":
            embed = discord.Embed(
                title="🛠️ Maintenance Commands",
                description="Bot maintenance and system updates",
                color=0xe67e22
            )
            embed.add_field(
                name="System Maintenance",
                value="`/admin maintenance_mode` - Toggle maintenance mode\n`/admin update_bot` - Update bot to latest version\n`/admin backup_data` - Backup bot data\n`/admin restore_data` - Restore bot data",
                inline=False
            )
            embed.add_field(
                name="Database",
                value="`/admin db_stats` - Database statistics\n`/admin db_cleanup` - Clean up database\n`/admin db_backup` - Backup database",
                inline=False
            )
        
        elif category == "debug":
            embed = discord.Embed(
                title="🔍 Debug & Testing Commands",
                description="Debug tools and testing utilities",
                color=0x95a5a6
            )
            embed.add_field(
                name="Debug Tools",
                value="`/admin debug_user <user_id>` - Debug user information\n`/admin debug_guild <guild_id>` - Debug guild information\n`/admin test_command <command>` - Test a specific command\n`/admin simulate_event <event>` - Simulate bot events",
                inline=False
            )
            embed.add_field(
                name="Error Handling",
                value="`/admin error_logs` - View recent error logs\n`/admin clear_errors` - Clear error logs\n`/admin test_error` - Test error handling",
                inline=False
            )
        
        elif category == "logs":
            embed = discord.Embed(
                title="📝 Logs & Monitoring Commands",
                description="System logs and monitoring tools",
                color=0x1abc9c
            )
            embed.add_field(
                name="Log Management",
                value="`/admin logs` - View recent logs\n`/admin clear_logs` - Clear log files\n`/admin log_level <level>` - Set logging level\n`/admin export_logs` - Export logs to file",
                inline=False
            )
            embed.add_field(
                name="Monitoring",
                value="`/admin monitor_guilds` - Monitor guild activity\n`/admin monitor_users` - Monitor user activity\n`/admin alerts` - View system alerts",
                inline=False
            )
        
        elif category == "configuration":
            embed = discord.Embed(
                title="⚙️ Configuration Commands",
                description="Bot configuration and settings management",
                color=0x8e44ad
            )
            embed.add_field(
                name="Bot Settings",
                value="`/admin config_view` - View current configuration\n`/admin config_set <key> <value>` - Set configuration value\n`/admin config_reset` - Reset to default configuration\n`/admin config_backup` - Backup configuration",
                inline=False
            )
            embed.add_field(
                name="Feature Toggles",
                value="`/admin toggle_feature <feature>` - Toggle bot features\n`/admin feature_status` - View feature status\n`/admin emergency_disable` - Emergency disable all features",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        view = AdminHelpView(self.bot)
        await interaction.response.edit_message(embed=embed, view=view)

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.main_admin_id = 1037768611126841405
    
    def is_bot_admin(self, user_id: int) -> bool:
        """Check if user is a bot admin"""
        return user_id in self.bot.bot_admins
    
    def is_main_admin(self, user_id: int) -> bool:
        """Check if user is the main admin"""
        return user_id == self.main_admin_id
    
    @app_commands.command(name="admin", description="Bot admin help and commands")
    async def admin_help(self, interaction: discord.Interaction):
        """Admin help command with dropdown categories"""
        if not self.is_bot_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use admin commands.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="👑 Dravon Bot Admin Panel",
            description="**Welcome to the Admin Control Center**\n\nYou have access to advanced bot administration commands. Select a category below to view available commands.\n\n**Your Admin Level:** " + ("Main Administrator" if self.is_main_admin(interaction.user.id) else "Bot Administrator"),
            color=0xffd700
        )
        
        embed.add_field(
            name="📂 Available Categories",
            value="🔧 **Bot Management** - System control\n👑 **Admin Management** - Manage admins\n💎 **Premium System** - Premium features\n📊 **Statistics** - Bot analytics\n🛠️ **Maintenance** - System maintenance\n🔍 **Debug & Testing** - Debug tools\n📝 **Logs & Monitoring** - System logs\n⚙️ **Configuration** - Bot settings",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Quick Commands",
            value="`/admin_stats` - Bot statistics\n`/admin guilds` - List all guilds\n`/admin premium_list` - Premium users\n`/admin logs` - Recent logs",
            inline=False
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Admin Panel • {len(self.bot.bot_admins)} Admins • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        view = AdminHelpView(self.bot)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @app_commands.command(name="add_admin", description="Add a new bot administrator")
    @app_commands.describe(user_id="The user ID to add as admin")
    async def add_admin(self, interaction: discord.Interaction, user_id: str):
        """Add a new bot admin (Main admin only)"""
        if not self.is_main_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the main administrator can add new admins.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            user_id_int = int(user_id)
            
            if user_id_int in self.bot.bot_admins:
                embed = discord.Embed(
                    title="⚠️ Already Admin",
                    description=f"User <@{user_id_int}> is already a bot administrator.",
                    color=0xffd700
                )
                embed = add_dravon_footer(embed)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Add to bot admins
            self.bot.bot_admins.add(user_id_int)
            await self.bot.db.add_bot_admin(user_id_int)
            
            # Try to get user info
            try:
                user = await self.bot.fetch_user(user_id_int)
                user_mention = user.mention
                user_name = str(user)
            except:
                user_mention = f"<@{user_id_int}>"
                user_name = f"User ID: {user_id_int}"
            
            embed = discord.Embed(
                title="✅ Admin Added Successfully",
                description=f"**{user_name}** has been added as a bot administrator.\n\nThey now have access to all admin commands except adding/removing other admins.",
                color=0x00ff00
            )
            
            embed.add_field(
                name="👤 New Admin",
                value=f"**User:** {user_mention}\n**ID:** `{user_id_int}`\n**Added by:** {interaction.user.mention}\n**Date:** <t:{int(datetime.now().timestamp())}:F>",
                inline=False
            )
            
            embed.add_field(
                name="🔧 Admin Permissions",
                value="• Bot management commands\n• Premium system management\n• Statistics and monitoring\n• Debug and testing tools\n• Configuration management",
                inline=False
            )
            
            embed.set_footer(text=f"Total Admins: {len(self.bot.bot_admins)} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Try to send DM to new admin
            try:
                dm_embed = discord.Embed(
                    title="🎉 You've Been Made a Dravon Bot Admin!",
                    description=f"**Congratulations!**\n\nYou have been granted bot administrator privileges by {interaction.user.mention}.\n\n**What this means:**\n• You can now use `/admin` commands\n• Access to bot management features\n• Premium system control\n• Statistics and monitoring tools\n\n**Get Started:**\nUse `/admin` to see all available commands!",
                    color=0xffd700
                )
                dm_embed.set_footer(text="Welcome to the admin team! • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
                await user.send(embed=dm_embed)
            except:
                pass  # DM failed, but that's okay
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid user ID (numbers only).",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="remove_admin", description="Remove a bot administrator")
    @app_commands.describe(user_id="The user ID to remove from admins")
    async def remove_admin(self, interaction: discord.Interaction, user_id: str):
        """Remove a bot admin (Main admin only)"""
        if not self.is_main_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the main administrator can remove admins.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            user_id_int = int(user_id)
            
            if user_id_int == self.main_admin_id:
                embed = discord.Embed(
                    title="❌ Cannot Remove Main Admin",
                    description="The main administrator cannot be removed.",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            if user_id_int not in self.bot.bot_admins:
                embed = discord.Embed(
                    title="⚠️ Not an Admin",
                    description=f"User <@{user_id_int}> is not a bot administrator.",
                    color=0xffd700
                )
                embed = add_dravon_footer(embed)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Remove from bot admins
            self.bot.bot_admins.remove(user_id_int)
            await self.bot.db.remove_bot_admin(user_id_int)
            
            # Try to get user info
            try:
                user = await self.bot.fetch_user(user_id_int)
                user_mention = user.mention
                user_name = str(user)
            except:
                user_mention = f"<@{user_id_int}>"
                user_name = f"User ID: {user_id_int}"
            
            embed = discord.Embed(
                title="✅ Admin Removed Successfully",
                description=f"**{user_name}** has been removed from bot administrators.\n\nThey no longer have access to admin commands.",
                color=0x00ff00
            )
            
            embed.add_field(
                name="👤 Removed Admin",
                value=f"**User:** {user_mention}\n**ID:** `{user_id_int}`\n**Removed by:** {interaction.user.mention}\n**Date:** <t:{int(datetime.now().timestamp())}:F>",
                inline=False
            )
            
            embed.set_footer(text=f"Total Admins: {len(self.bot.bot_admins)} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid User ID",
                description="Please provide a valid user ID (numbers only).",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="list_admins", description="List all bot administrators")
    async def list_admins(self, interaction: discord.Interaction):
        """List all bot admins"""
        if not self.is_bot_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to view admin list.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="👑 Bot Administrators",
            description=f"**Total Administrators:** {len(self.bot.bot_admins)}",
            color=0xffd700
        )
        
        admin_list = []
        for admin_id in self.bot.bot_admins:
            try:
                user = await self.bot.fetch_user(admin_id)
                role = "Main Administrator" if admin_id == self.main_admin_id else "Bot Administrator"
                admin_list.append(f"👑 **{user}** - {role}\n└ ID: `{admin_id}`")
            except:
                role = "Main Administrator" if admin_id == self.main_admin_id else "Bot Administrator"
                admin_list.append(f"👑 **Unknown User** - {role}\n└ ID: `{admin_id}`")
        
        if admin_list:
            embed.add_field(
                name="📋 Administrator List",
                value="\n\n".join(admin_list),
                inline=False
            )
        else:
            embed.add_field(
                name="📋 Administrator List",
                value="No administrators found.",
                inline=False
            )
        
        embed.set_footer(text="Admin Management • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="admin_stats", description="View detailed bot statistics")
    async def admin_stats(self, interaction: discord.Interaction):
        """View bot statistics (Admin only)"""
        if not self.is_bot_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to view bot statistics.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Calculate statistics
        total_users = sum(guild.member_count for guild in self.bot.guilds)
        total_channels = sum(len(guild.channels) for guild in self.bot.guilds)
        
        embed = discord.Embed(
            title="📊 Detailed Bot Statistics",
            description="**Comprehensive bot analytics and metrics**",
            color=0x3498db
        )
        
        # Basic Stats
        embed.add_field(
            name="🏠 Server Statistics",
            value=f"**Guilds:** {len(self.bot.guilds):,}\n**Users:** {total_users:,}\n**Channels:** {total_channels:,}",
            inline=True
        )
        
        # Bot Info
        embed.add_field(
            name="🤖 Bot Information",
            value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n**Cogs Loaded:** {len(self.bot.cogs)}\n**Commands:** {len(self.bot.commands)}",
            inline=True
        )
        
        # Admin Info
        embed.add_field(
            name="👑 Administration",
            value=f"**Bot Admins:** {len(self.bot.bot_admins)}\n**Main Admin:** <@{self.main_admin_id}>\n**Your Level:** " + ("Main Admin" if self.is_main_admin(interaction.user.id) else "Bot Admin"),
            inline=True
        )
        
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text=f"Statistics generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="announce", description="Send announcement to all servers")
    async def announce(self, interaction: discord.Interaction):
        """Send announcement to all servers (Bot admin only)"""
        if not self.is_bot_admin(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You don't have permission to use announcement commands.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = discord.Embed(
            title="📢 Announcement System",
            description="**Create and send announcements to all servers**\n\nUse the dropdown below to configure your announcement message.",
            color=0x3498db
        )
        
        embed.add_field(
            name="📝 Configuration Options",
            value="• **Title** - Announcement title\n• **Description** - Main message content\n• **Color** - Embed color (hex code)\n• **Image** - Optional image URL",
            inline=False
        )
        
        embed.add_field(
            name="🚀 Actions",
            value="• **Save** - Save current configuration\n• **Send** - Send to all servers\n• **Preview** - Preview the announcement",
            inline=False
        )
        
        embed.set_footer(text=f"Announcement System • {len(self.bot.guilds)} servers • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        view = AnnouncementView(self.bot, interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class AnnouncementView(discord.ui.View):
    def __init__(self, bot, admin_id):
        super().__init__(timeout=600)
        self.bot = bot
        self.admin_id = admin_id
        self.announcement_data = {
            'title': '',
            'description': '',
            'color': '0x3498db',
            'image': ''
        }
    
    @discord.ui.select(
        placeholder="Configure announcement settings...",
        options=[
            discord.SelectOption(label="📝 Set Title", description="Set announcement title", value="title"),
            discord.SelectOption(label="📄 Set Description", description="Set main message content", value="description"),
            discord.SelectOption(label="🎨 Set Color", description="Set embed color (hex)", value="color"),
            discord.SelectOption(label="🖼️ Set Image", description="Set image URL", value="image"),
            discord.SelectOption(label="👁️ Preview", description="Preview announcement", value="preview"),
            discord.SelectOption(label="💾 Save", description="Save configuration", value="save"),
            discord.SelectOption(label="📢 Send", description="Send to all servers", value="send")
        ]
    )
    async def announcement_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if interaction.user.id != self.admin_id:
            await interaction.response.send_message("❌ Only the command author can use this.", ephemeral=True)
            return
        
        action = select.values[0]
        
        if action == "title":
            modal = AnnouncementModal(self, "title", "Set Announcement Title", "Enter the title for your announcement")
            await interaction.response.send_modal(modal)
        
        elif action == "description":
            modal = AnnouncementModal(self, "description", "Set Announcement Description", "Enter the main content of your announcement")
            await interaction.response.send_modal(modal)
        
        elif action == "color":
            modal = AnnouncementModal(self, "color", "Set Embed Color", "Enter hex color code (e.g., 0x3498db)")
            await interaction.response.send_modal(modal)
        
        elif action == "image":
            modal = AnnouncementModal(self, "image", "Set Image URL", "Enter image URL (optional)")
            await interaction.response.send_modal(modal)
        
        elif action == "preview":
            await self.show_preview(interaction)
        
        elif action == "save":
            await self.save_announcement(interaction)
        
        elif action == "send":
            await self.send_announcement(interaction)
    
    async def show_preview(self, interaction):
        """Show preview of announcement"""
        try:
            color = int(self.announcement_data['color'], 16) if self.announcement_data['color'] else 0x3498db
        except:
            color = 0x3498db
        
        embed = discord.Embed(
            title=self.announcement_data['title'] or "Announcement Title",
            description=self.announcement_data['description'] or "Announcement description goes here...",
            color=color
        )
        
        if self.announcement_data['image']:
            embed.set_image(url=self.announcement_data['image'])
        
        embed.set_footer(text="Preview • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.response.send_message("📋 **Announcement Preview:**", embed=embed, ephemeral=True)
    
    async def save_announcement(self, interaction):
        """Save announcement configuration"""
        embed = discord.Embed(
            title="💾 Configuration Saved",
            description="Your announcement configuration has been saved successfully!",
            color=0x00ff00
        )
        
        config_text = f"**Title:** {self.announcement_data['title'] or 'Not set'}\n"
        config_text += f"**Description:** {self.announcement_data['description'][:50] + '...' if len(self.announcement_data['description']) > 50 else self.announcement_data['description'] or 'Not set'}\n"
        config_text += f"**Color:** {self.announcement_data['color']}\n"
        config_text += f"**Image:** {'Set' if self.announcement_data['image'] else 'Not set'}"
        
        embed.add_field(name="📝 Current Configuration", value=config_text, inline=False)
        embed = add_dravon_footer(embed)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def send_announcement(self, interaction):
        """Send announcement to all servers"""
        if not self.announcement_data['title'] or not self.announcement_data['description']:
            embed = discord.Embed(
                title="❌ Incomplete Configuration",
                description="Please set both title and description before sending.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Confirmation embed
        confirm_embed = discord.Embed(
            title="⚠️ Confirm Announcement",
            description=f"**Are you sure you want to send this announcement to {len(self.bot.guilds)} servers?**\n\nThis action cannot be undone.",
            color=0xff8c00
        )
        
        view = ConfirmSendView(self.bot, self.announcement_data)
        await interaction.response.send_message(embed=confirm_embed, view=view, ephemeral=True)

class AnnouncementModal(discord.ui.Modal):
    def __init__(self, parent_view, field_type, title, placeholder):
        super().__init__(title=title)
        self.parent_view = parent_view
        self.field_type = field_type
        
        self.input = discord.ui.TextInput(
            label=title,
            placeholder=placeholder,
            style=discord.TextStyle.long if field_type == "description" else discord.TextStyle.short,
            max_length=4000 if field_type == "description" else 256,
            required=True
        )
        self.add_item(self.input)
    
    async def on_submit(self, interaction: discord.Interaction):
        self.parent_view.announcement_data[self.field_type] = self.input.value
        
        embed = discord.Embed(
            title="✅ Updated Successfully",
            description=f"**{self.field_type.title()}** has been updated!",
            color=0x00ff00
        )
        
        if self.field_type == "description":
            preview_text = self.input.value[:100] + "..." if len(self.input.value) > 100 else self.input.value
        else:
            preview_text = self.input.value
        
        embed.add_field(name="New Value", value=f"```{preview_text}```", inline=False)
        embed = add_dravon_footer(embed)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ConfirmSendView(discord.ui.View):
    def __init__(self, bot, announcement_data):
        super().__init__(timeout=60)
        self.bot = bot
        self.announcement_data = announcement_data
    
    @discord.ui.button(label="✅ Confirm Send", style=discord.ButtonStyle.danger)
    async def confirm_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Create announcement embed
        try:
            color = int(self.announcement_data['color'], 16)
        except:
            color = 0x3498db
        
        announcement_embed = discord.Embed(
            title=self.announcement_data['title'],
            description=self.announcement_data['description'],
            color=color
        )
        
        if self.announcement_data['image']:
            announcement_embed.set_image(url=self.announcement_data['image'])
        
        announcement_embed.set_footer(text="Official Announcement • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        # Send to all servers
        sent_count = 0
        failed_count = 0
        
        for guild in self.bot.guilds:
            try:
                # Find suitable channel
                channel = None
                for ch in guild.text_channels:
                    if ch.name.lower() in ['general', 'announcements', 'news', 'updates', 'main']:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break
                
                if not channel:
                    for ch in guild.text_channels:
                        if ch.permissions_for(guild.me).send_messages:
                            channel = ch
                            break
                
                if channel:
                    await channel.send(embed=announcement_embed)
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                failed_count += 1
                print(f"Failed to send announcement to {guild.name}: {e}")
        
        # Send completion report
        result_embed = discord.Embed(
            title="📢 Announcement Sent!",
            description=f"**Announcement has been sent successfully!**",
            color=0x00ff00
        )
        
        result_embed.add_field(
            name="📊 Delivery Report",
            value=f"✅ **Sent:** {sent_count} servers\n❌ **Failed:** {failed_count} servers\n📈 **Success Rate:** {(sent_count/(sent_count+failed_count)*100):.1f}%",
            inline=False
        )
        
        result_embed.set_footer(text="Announcement System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        await interaction.followup.send(embed=result_embed, ephemeral=True)
    
    @discord.ui.button(label="❌ Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_send(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="❌ Announcement Cancelled",
            description="The announcement has been cancelled and was not sent.",
            color=0x7289da
        )
        embed = add_dravon_footer(embed)
        await interaction.response.edit_message(embed=embed, view=None)

async def setup(bot):
    await bot.add_cog(Admin(bot))