import discord
from discord.ext import commands

class PremiumListView(discord.ui.View):
    def __init__(self, bot, premium_users, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.premium_users = premium_users
        self.page = page
        self.per_page = 10
        self.max_pages = (len(premium_users) - 1) // self.per_page + 1 if premium_users else 1
    
    def create_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_users = self.premium_users[start:end]
        
        embed = discord.Embed(
            title="💎 Premium Users",
            description=f"**Total Premium Users:** {len(self.premium_users)}\n**Page:** {self.page + 1}/{self.max_pages}",
            color=0x7289da
        )
        
        if page_users:
            user_text = ""
            for user_id in page_users:
                try:
                    user = self.bot.get_user(user_id)
                    user_text += f"• {user.mention if user else f'Unknown User'} (`{user_id}`)\n"
                except:
                    user_text += f"• Unknown User (`{user_id}`)\n"
            
            embed.add_field(
                name="Premium Users",
                value=user_text,
                inline=False
            )
        else:
            embed.add_field(
                name="Premium Users",
                value="No premium users found.",
                inline=False
            )
        
        return embed
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="🏠", style=discord.ButtonStyle.primary)
    async def home_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page < self.max_pages - 1:
            self.page += 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = self.max_pages - 1
        embed = self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

class AdminPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=300)
        self.bot = bot
    
    @discord.ui.button(label="💎 Premium List", style=discord.ButtonStyle.primary)
    async def premium_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            # Get all premium users (mock data - would use actual database)
            premium_users = []  # Would get from database
            
            if not premium_users:
                embed = discord.Embed(
                    title="💎 Premium Users",
                    description="No premium users found.",
                    color=0x7289da
                )
                await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.bot))
                return
            
            view = PremiumListView(self.bot, premium_users)
            embed = view.create_embed()
            await interaction.response.edit_message(embed=embed, view=view)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)
    
    @discord.ui.button(label="➕ Add Bot Admin", style=discord.ButtonStyle.success)
    async def add_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = AddAdminModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="➖ Remove Bot Admin", style=discord.ButtonStyle.danger)
    async def remove_admin(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RemoveAdminModal(self.bot)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="📋 Admin List", style=discord.ButtonStyle.secondary)
    async def admin_list(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            admins = await self.bot.db.get_bot_admins()
            
            embed = discord.Embed(
                title="👑 Bot Administrators",
                color=0x7289da
            )
            
            if admins:
                admin_text = ""
                for admin_id in admins:
                    try:
                        user = self.bot.get_user(admin_id)
                        admin_text += f"• {user.mention if user else 'Unknown User'} (`{admin_id}`)\n"
                    except:
                        admin_text += f"• Unknown User (`{admin_id}`)\n"
                
                embed.add_field(
                    name="Current Bot Admins",
                    value=admin_text,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Current Bot Admins",
                    value="No additional bot admins found.",
                    inline=False
                )
            
            embed.set_footer(text=f"Total: {len(admins)} admins")
            await interaction.response.edit_message(embed=embed, view=AdminPanelView(self.bot))
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class AddAdminModal(discord.ui.Modal, title="Add Bot Administrator"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    user_id_input = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user ID to make bot admin...",
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = int(self.user_id_input.value.strip())
            
            # Check if user exists
            user = self.bot.get_user(user_id)
            if not user:
                await interaction.response.send_message("❌ User not found!", ephemeral=True)
                return
            
            # Add to database
            await self.bot.db.add_bot_admin(user_id)
            
            embed = discord.Embed(
                title="✅ Bot Admin Added",
                description=f"{user.mention} (`{user_id}`) has been added as a bot administrator.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID format!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class RemoveAdminModal(discord.ui.Modal, title="Remove Bot Administrator"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    user_id_input = discord.ui.TextInput(
        label="User ID",
        placeholder="Enter the user ID to remove from bot admins...",
        max_length=20
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_id = int(self.user_id_input.value.strip())
            
            # Cannot remove main bot owner
            if user_id == 1037768611126841405:
                await interaction.response.send_message("❌ Cannot remove the main bot owner!", ephemeral=True)
                return
            
            # Remove from database
            await self.bot.db.remove_bot_admin(user_id)
            
            user = self.bot.get_user(user_id)
            embed = discord.Embed(
                title="✅ Bot Admin Removed",
                description=f"{user.mention if user else 'User'} (`{user_id}`) has been removed from bot administrators.",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except ValueError:
            await interaction.response.send_message("❌ Invalid user ID format!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

class AdminPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    def is_bot_admin(self, user_id):
        """Check if user is bot admin"""
        return user_id == 1037768611126841405 or user_id in getattr(self.bot, 'bot_admins', set())
    
    @commands.hybrid_group(name="admin", hidden=True)
    async def admin_group(self, ctx):
        """Bot administration commands (Bot Admin Only)"""
        if not self.is_bot_admin(ctx.author.id):
            return  # Hidden command, no error message
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="👑 Bot Administration",
                description="**Available Commands:**\n• `/admin panel` - Open admin control panel",
                color=0x7289da
            )
            await ctx.send(embed=embed)
    
    @admin_group.command(name="panel")
    async def admin_panel(self, ctx):
        """Open the bot administration panel"""
        embed = discord.Embed(
            title="👑 Bot Administration Panel",
            description="**Welcome to the admin control panel.**\n\nUse the buttons below to manage bot administrators and view premium users.",
            color=0x7289da
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(text="Bot Admin Panel • Restricted Access", icon_url=self.bot.user.display_avatar.url)
        
        view = AdminPanelView(self.bot)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AdminPanel(bot))