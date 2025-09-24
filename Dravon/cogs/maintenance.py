import discord
from discord.ext import commands
import json

class Maintenance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="maintenance")
    @commands.has_permissions(administrator=True)
    async def maintenance_group(self, ctx):
        """Maintenance system commands"""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `/maintenance on`, `/maintenance off`, `/maintenance status`, or `/maintenance restore`")
    
    @maintenance_group.command(name="on")
    async def maintenance_on(self, ctx):
        """Enable maintenance mode"""
        await ctx.defer()
        
        guild = ctx.guild
        everyone_role = guild.default_role
        
        # Store original channel permissions
        hidden_channels = []
        
        try:
            # Hide all channels from normal members
            for channel in guild.channels:
                if isinstance(channel, (discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel)):
                    # Store original permissions
                    perms = channel.overwrites_for(everyone_role)
                    if perms.view_channel is not False:
                        hidden_channels.append(channel.id)
                        # Hide channel
                        await channel.set_permissions(everyone_role, view_channel=False)
            
            # Create Maintenance category
            maintenance_category = await guild.create_category("🔧 Maintenance")
            
            # Set category permissions - only admins can see
            await maintenance_category.set_permissions(everyone_role, view_channel=False)
            for role in guild.roles:
                if role.permissions.administrator:
                    await maintenance_category.set_permissions(role, view_channel=True)
            
            # Create Maintenance Update channel (locked for normal users)
            update_channel = await guild.create_text_channel(
                "maintenance-updates",
                category=maintenance_category,
                topic="📢 Maintenance updates and announcements"
            )
            await update_channel.set_permissions(everyone_role, send_messages=False, view_channel=True)
            
            # Create Maintenance Chat channel
            chat_channel = await guild.create_text_channel(
                "maintenance-chat",
                category=maintenance_category,
                topic="💬 General chat during maintenance"
            )
            await chat_channel.set_permissions(everyone_role, view_channel=True)
            
            # Create Maintenance Media channel (only media, no text)
            media_channel = await guild.create_text_channel(
                "maintenance-media",
                category=maintenance_category,
                topic="📸 Share photos, videos, and GIFs only"
            )
            await media_channel.set_permissions(everyone_role, 
                                              send_messages=False,
                                              attach_files=True,
                                              embed_links=True,
                                              view_channel=True)
            
            # Create Maintenance Commands channel
            cmd_channel = await guild.create_text_channel(
                "maintenance-commands",
                category=maintenance_category,
                topic="🤖 Bot commands during maintenance"
            )
            await cmd_channel.set_permissions(everyone_role, view_channel=True)
            
            # Restrict media in all other channels
            for channel in guild.text_channels:
                if channel.category != maintenance_category:
                    await channel.set_permissions(everyone_role, 
                                                attach_files=False,
                                                embed_links=False)
                    # Allow admins to send media
                    for role in guild.roles:
                        if role.permissions.administrator:
                            await channel.set_permissions(role, 
                                                        attach_files=True,
                                                        embed_links=True)
            
            # Save maintenance data
            maintenance_data = {
                "active": True,
                "category_id": maintenance_category.id,
                "update_channel_id": update_channel.id,
                "chat_channel_id": chat_channel.id,
                "media_channel_id": media_channel.id,
                "cmd_channel_id": cmd_channel.id,
                "hidden_channels": hidden_channels
            }
            
            await self.bot.db.set_maintenance_data(guild.id, maintenance_data)
            
            embed = discord.Embed(
                title="✅ Maintenance Mode Setup Complete",
                description=f"**Maintenance category created with:**\n• {update_channel.mention} - Updates only\n• {chat_channel.mention} - General chat\n• {media_channel.mention} - Media only\n• {cmd_channel.mention} - Bot commands\n\n**All other channels hidden from normal members**\n**Media restrictions applied to all channels**",
                color=0x00ff00
            )
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Failed to enable maintenance mode: {str(e)}")
    
    @maintenance_group.command(name="off")
    async def maintenance_off(self, ctx):
        """Disable maintenance mode"""
        await ctx.defer()
        
        guild = ctx.guild
        everyone_role = guild.default_role
        
        try:
            # Get maintenance data
            maintenance_data = await self.bot.db.get_maintenance_data(guild.id)
            if not maintenance_data or not maintenance_data.get("active"):
                await ctx.followup.send("❌ Maintenance mode is not active!")
                return
            
            # Delete maintenance category and channels
            category = guild.get_channel(maintenance_data.get("category_id"))
            if category:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
            
            # Restore channel visibility
            hidden_channels = maintenance_data.get("hidden_channels", [])
            for channel_id in hidden_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    await channel.set_permissions(everyone_role, view_channel=None)
            
            # Restore media permissions in all channels
            for channel in guild.text_channels:
                await channel.set_permissions(everyone_role, 
                                            attach_files=None,
                                            embed_links=None)
                # Remove admin overrides
                for role in guild.roles:
                    if role.permissions.administrator and role != everyone_role:
                        perms = channel.overwrites_for(role)
                        if perms.attach_files is True:
                            await channel.set_permissions(role, 
                                                        attach_files=None,
                                                        embed_links=None)
            
            # Clear maintenance data
            await self.bot.db.clear_maintenance_data(guild.id)
            
            embed = discord.Embed(
                title="✅ Maintenance Mode Disabled Successfully",
                description="All channels and permissions have been restored to normal state.",
                color=0x00ff00
            )
            await ctx.followup.send(embed=embed)
            
        except Exception as e:
            await ctx.followup.send(f"❌ Failed to disable maintenance mode: {str(e)}")
    
    @maintenance_group.command(name="status")
    async def maintenance_status(self, ctx):
        """Check maintenance mode status"""
        
        try:
            maintenance_data = await self.bot.db.get_maintenance_data(ctx.guild.id)
            
            embed = discord.Embed(
                title="🔧 Maintenance Mode Status",
                color=0x7289da
            )
            
            if not maintenance_data or not maintenance_data.get("active"):
                embed.add_field(
                    name="Status",
                    value="🔴 Inactive",
                    inline=False
                )
            else:
                embed.add_field(
                    name="Status",
                    value="🟢 Active",
                    inline=False
                )
            
            embed.add_field(
                name="Settings",
                value="Auto-Create: Category: Maintenance",
                inline=False
            )
            
            embed.add_field(
                name="Guild ID",
                value=f"`{ctx.guild.id}`",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to check status: {str(e)}")
    
    @maintenance_group.command(name="restore")
    async def maintenance_restore(self, ctx):
        """Restore all channels and disable maintenance mode"""
        
        guild = ctx.guild
        everyone_role = guild.default_role
        
        try:
            # Get maintenance data
            maintenance_data = await self.bot.db.get_maintenance_data(guild.id)
            if not maintenance_data or not maintenance_data.get("active"):
                await ctx.followup.send("❌ Maintenance mode is not active!")
                return
            
            # Delete maintenance category and channels
            category = guild.get_channel(maintenance_data.get("category_id"))
            if category:
                for channel in category.channels:
                    await channel.delete()
                await category.delete()
            
            # Restore channel visibility
            hidden_channels = maintenance_data.get("hidden_channels", [])
            for channel_id in hidden_channels:
                channel = guild.get_channel(channel_id)
                if channel:
                    await channel.set_permissions(everyone_role, view_channel=None)
            
            # Restore media permissions in all channels
            for channel in guild.text_channels:
                await channel.set_permissions(everyone_role, 
                                            attach_files=None,
                                            embed_links=None)
                # Remove admin overrides
                for role in guild.roles:
                    if role.permissions.administrator and role != everyone_role:
                        perms = channel.overwrites_for(role)
                        if perms.attach_files is True:
                            await channel.set_permissions(role, 
                                                        attach_files=None,
                                                        embed_links=None)
            
            # Clear maintenance data
            await self.bot.db.clear_maintenance_data(guild.id)
            
            embed = discord.Embed(
                title="✅ Maintenance Mode Restored",
                description="All channels and permissions have been fully restored to normal state.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Failed to restore maintenance mode: {str(e)}")

    @commands.hybrid_command(name="lock")
    @commands.has_permissions(manage_channels=True)
    async def lock_channel(self, ctx, channel: discord.TextChannel = None):
        """Lock a channel for normal users"""
        channel = channel or ctx.channel
        everyone_role = ctx.guild.default_role
        
        try:
            await channel.set_permissions(everyone_role, send_messages=False)
            
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"{channel.mention} has been locked for normal users.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to lock channel: {str(e)}")
    
    @commands.hybrid_command(name="unlock")
    @commands.has_permissions(manage_channels=True)
    async def unlock_channel(self, ctx, channel: discord.TextChannel = None):
        """Unlock a channel for normal users"""
        channel = channel or ctx.channel
        everyone_role = ctx.guild.default_role
        
        try:
            await channel.set_permissions(everyone_role, send_messages=None)
            
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description=f"{channel.mention} has been unlocked for normal users.",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Failed to unlock channel: {str(e)}")

async def setup(bot):
    await bot.add_cog(Maintenance(bot))