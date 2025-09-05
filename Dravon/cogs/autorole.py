import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class AutoRoleSetupView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=900)
        self.bot = bot
        self.config = {
            "member_role": None,
            "bot_role": None,
            "extra_roles": [],
            "delay": 0,
            "enabled": False
        }
    
    @discord.ui.button(label="👥 Set Member Role", style=discord.ButtonStyle.primary)
    async def set_member_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RoleSelectView(self, "member_role", "Select a role for new members:")
        await interaction.response.edit_message(view=view)
    
    @discord.ui.button(label="🤖 Set Bot Role", style=discord.ButtonStyle.primary)
    async def set_bot_role(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RoleSelectView(self, "bot_role", "Select a role for new bots:")
        await interaction.response.edit_message(view=view)
    
    @discord.ui.button(label="➕ Extra Roles", style=discord.ButtonStyle.secondary)
    async def set_extra_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = RoleSelectView(self, "extra_roles", "Select additional roles:")
        await interaction.response.edit_message(view=view)
    
    @discord.ui.button(label="⏳ Set Delay", style=discord.ButtonStyle.secondary)
    async def set_delay(self, interaction: discord.Interaction, button: discord.ui.Button):
        view = DelaySelectView(self)
        await interaction.response.edit_message(view=view)
    
    @discord.ui.button(label="⚙️ Toggle System", style=discord.ButtonStyle.secondary)
    async def toggle_system(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.config["enabled"] = not self.config["enabled"]
        status = "✅ Enabled" if self.config["enabled"] else "❌ Disabled"
        button.label = f"⚙️ {status}"
        
        embed = self.create_setup_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💾 Save", style=discord.ButtonStyle.success, row=1)
    async def save_config(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.bot.db.set_autorole_config(interaction.guild.id, self.config)
        
        embed = discord.Embed(
            title="✅ AutoRole System Saved",
            description="AutoRole system has been saved and activated!",
            color=0x00ff00
        )
        
        await interaction.response.edit_message(embed=embed, view=None)
    
    def create_setup_embed(self):
        embed = discord.Embed(
            title="🎭 AutoRole Setup",
            description="Welcome to the AutoRole setup!\n\nHere you can configure which roles will be automatically given when new members or bots join.\n\nUse the buttons below to set everything – no extra commands required!",
            color=0x7289da
        )
        
        # Show current config
        member_role = f"<@&{self.config['member_role']}>" if self.config['member_role'] else "Not set"
        bot_role = f"<@&{self.config['bot_role']}>" if self.config['bot_role'] else "Not set"
        extra_roles = ", ".join([f"<@&{role_id}>" for role_id in self.config['extra_roles']]) if self.config['extra_roles'] else "None"
        
        delay_text = "No Delay"
        if self.config['delay'] > 0:
            if self.config['delay'] < 60:
                delay_text = f"{self.config['delay']}s"
            else:
                delay_text = f"{self.config['delay']//60}m"
        
        status = "✅ Enabled" if self.config['enabled'] else "❌ Disabled"
        
        embed.add_field(name="👥 Member Role", value=member_role, inline=True)
        embed.add_field(name="🤖 Bot Role", value=bot_role, inline=True)
        embed.add_field(name="➕ Extra Roles", value=extra_roles, inline=True)
        embed.add_field(name="⏳ Delay", value=delay_text, inline=True)
        embed.add_field(name="⚙️ Status", value=status, inline=True)
        
        return embed

class RoleSelectView(discord.ui.View):
    def __init__(self, setup_view, config_key, placeholder):
        super().__init__(timeout=300)
        self.setup_view = setup_view
        self.config_key = config_key
        self.placeholder = placeholder
    
    @discord.ui.select(cls=discord.ui.RoleSelect, placeholder="Choose a role...")
    async def role_select(self, interaction: discord.Interaction, select: discord.ui.RoleSelect):
        selected_role = select.values[0]
        
        if self.config_key == "extra_roles":
            if selected_role.id not in self.setup_view.config["extra_roles"]:
                self.setup_view.config["extra_roles"].append(selected_role.id)
        else:
            self.setup_view.config[self.config_key] = selected_role.id
        
        embed = self.setup_view.create_setup_embed()
        await interaction.response.edit_message(embed=embed, view=self.setup_view)

class DelaySelectView(discord.ui.View):
    def __init__(self, setup_view):
        super().__init__(timeout=300)
        self.setup_view = setup_view
    
    @discord.ui.select(
        placeholder="Choose delay time...",
        options=[
            discord.SelectOption(label="No Delay", value="0"),
            discord.SelectOption(label="10 seconds", value="10"),
            discord.SelectOption(label="30 seconds", value="30"),
            discord.SelectOption(label="1 minute", value="60"),
            discord.SelectOption(label="5 minutes", value="300")
        ]
    )
    async def delay_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.setup_view.config["delay"] = int(select.values[0])
        
        embed = self.setup_view.create_setup_embed()
        await interaction.response.edit_message(embed=embed, view=self.setup_view)

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="autorole")
    async def autorole(self, ctx):
        if not ctx.author.guild_permissions.manage_roles:
            await ctx.send("You need 'Manage Roles' permission to use this command.")
            return
        
        view = AutoRoleSetupView(self.bot)
        embed = view.create_setup_embed()
        
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        config = await self.bot.db.get_autorole_config(member.guild.id)
        
        if not config or not config.get("enabled"):
            return
        
        # Wait for delay if configured
        delay = config.get("delay", 0)
        if delay > 0:
            await asyncio.sleep(delay)
        
        roles_to_add = []
        
        # Add member or bot role
        if member.bot and config.get("bot_role"):
            role = member.guild.get_role(config["bot_role"])
            if role:
                roles_to_add.append(role)
        elif not member.bot and config.get("member_role"):
            role = member.guild.get_role(config["member_role"])
            if role:
                roles_to_add.append(role)
        
        # Add extra roles
        for role_id in config.get("extra_roles", []):
            role = member.guild.get_role(role_id)
            if role:
                roles_to_add.append(role)
        
        # Apply roles
        if roles_to_add:
            try:
                await member.add_roles(*roles_to_add, reason="AutoRole system")
            except discord.Forbidden:
                pass
            except discord.HTTPException:
                pass

async def setup(bot):
    await bot.add_cog(AutoRole(bot))