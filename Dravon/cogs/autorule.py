import discord
from discord.ext import commands
from discord import app_commands

class CapsModal(discord.ui.Modal, title="All Caps Configuration"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    percentage = discord.ui.TextInput(
        label="Caps Percentage (%)",
        placeholder="Enter percentage (e.g., 80)",
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            caps_percent = int(self.percentage.value)
            if caps_percent < 1 or caps_percent > 100:
                await interaction.response.send_message("Percentage must be between 1-100!", ephemeral=True)
                return
            
            self.view.config["caps_percentage"] = caps_percent
            view = ActionSelectView("all_caps", self.view.config)
            
            embed = discord.Embed(
                title="⚙️ All Caps Configuration",
                description=f"**Setting:** {caps_percent}% caps threshold\n**Action:** Choose action below\n\n**Example:** If a message has {caps_percent}% or more caps, then perform selected action.",
                color=0x7289da
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number!", ephemeral=True)

class BadWordsModal(discord.ui.Modal, title="Bad Words Configuration"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    words = discord.ui.TextInput(
        label="Banned Words/Phrases",
        placeholder="Enter words separated by - (e.g., fuck-bitch-idiot)",
        style=discord.TextStyle.paragraph,
        max_length=1000
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        banned_words = [word.strip() for word in self.words.value.split("-") if word.strip()]
        if not banned_words:
            await interaction.response.send_message("Please enter at least one word!", ephemeral=True)
            return
        
        self.view.config["banned_words"] = banned_words
        view = ActionSelectView("bad_words", self.view.config)
        
        embed = discord.Embed(
            title="⚙️ Bad Words Configuration",
            description=f"**Setting:** {len(banned_words)} banned words\n**Words:** {', '.join(banned_words[:5])}{'...' if len(banned_words) > 5 else ''}\n**Action:** Choose action below",
            color=0x7289da
        )
        
        await interaction.response.edit_message(embed=embed, view=view)

class EmojiSpamModal(discord.ui.Modal, title="Emoji Spam Configuration"):
    def __init__(self, view):
        super().__init__()
        self.view = view
    
    max_emojis = discord.ui.TextInput(
        label="Max Emojis per Message",
        placeholder="Enter number (e.g., 10)",
        max_length=3
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        try:
            emoji_limit = int(self.max_emojis.value)
            if emoji_limit < 1:
                await interaction.response.send_message("Number must be greater than 0!", ephemeral=True)
                return
            
            self.view.config["max_emojis"] = emoji_limit
            view = ActionSelectView("emoji_spam", self.view.config)
            
            embed = discord.Embed(
                title="⚙️ Emoji Spam Configuration",
                description=f"**Setting:** Max {emoji_limit} emojis per message\n**Action:** Choose action below",
                color=0x7289da
            )
            
            await interaction.response.edit_message(embed=embed, view=view)
        except ValueError:
            await interaction.response.send_message("Please enter a valid number!", ephemeral=True)

class RuleConfigView(discord.ui.View):
    def __init__(self, rule_type):
        super().__init__(timeout=900)
        self.rule_type = rule_type
        self.config = {"rule_type": rule_type}

class RuleTypeSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
    
    @discord.ui.select(
        placeholder="Choose a rule type to configure...",
        options=[
            discord.SelectOption(label="All Caps", description="Detect messages with excessive capital letters", value="all_caps"),
            discord.SelectOption(label="Bad Words", description="Filter inappropriate language", value="bad_words"),
            discord.SelectOption(label="Emoji Spam", description="Limit emoji usage per message", value="emoji_spam"),
            discord.SelectOption(label="Image Spam", description="Control image posting frequency", value="image_spam"),
            discord.SelectOption(label="Invite Links", description="Block Discord invite links", value="invite_links"),
            discord.SelectOption(label="Mass Mentions", description="Limit mentions per message", value="mass_mentions"),
            discord.SelectOption(label="Stickers", description="Control sticker usage", value="stickers"),
            discord.SelectOption(label="Fast Message Spam", description="Prevent rapid message sending", value="fast_spam"),
            discord.SelectOption(label="Duplicate Text", description="Block repeated characters/words", value="duplicate_text"),
            discord.SelectOption(label="Links", description="Control external link posting", value="links")
        ]
    )
    async def rule_type_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        rule_type = select.values[0]
        
        config_view = RuleConfigView(rule_type)
        
        if rule_type == "all_caps":
            modal = CapsModal(config_view)
            await interaction.response.send_modal(modal)
        elif rule_type == "bad_words":
            modal = BadWordsModal(config_view)
            await interaction.response.send_modal(modal)
        elif rule_type == "emoji_spam":
            modal = EmojiSpamModal(config_view)
            await interaction.response.send_modal(modal)
        else:
            # For other rule types, go directly to action selection
            view = ActionSelectView(rule_type, {"rule_type": rule_type})
            embed = discord.Embed(
                title=f"⚙️ {select.options[[opt.value for opt in select.options].index(rule_type)].label} Configuration",
                description="Choose an action for this rule type.",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=view)

class ActionSelectView(discord.ui.View):
    def __init__(self, rule_type, config):
        super().__init__(timeout=900)
        self.rule_type = rule_type
        self.config = config
    
    @discord.ui.select(
        placeholder="Choose an action for this rule...",
        options=[
            discord.SelectOption(label="Warn", description="Send a warning to the user", value="warn"),
            discord.SelectOption(label="Delete", description="Delete the offending message", value="delete"),
            discord.SelectOption(label="Automute", description="Temporarily mute the user", value="automute"),
            discord.SelectOption(label="Autoban", description="Temporarily ban the user", value="autoban"),
            discord.SelectOption(label="Instant Mute", description="Permanently mute the user", value="instant_mute"),
            discord.SelectOption(label="Instant Ban", description="Permanently ban the user", value="instant_ban")
        ]
    )
    async def action_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        
        # Save the rule configuration
        bot = interaction.client
        rule_config = self.config.copy()
        rule_config.update({
            "action": action,
            "enabled": True
        })
        await bot.db.set_autorule_config(interaction.guild.id, self.rule_type, rule_config)
        
        # Return to main setup with success message
        embed = discord.Embed(
            title="🛡️ Auto Rule Setup",
            description=f"**Configure automatic moderation rules for your server.**\n\n✅ **{self.rule_type.replace('_', ' ').title()}** rule saved with **{action.replace('_', ' ').title()}** action!\n\n📋 **Available Rule Types:**\n\n• **All Caps** → Detect excessive capital letters\n• **Bad Words** → Filter inappropriate language\n• **Emoji Spam** → Limit emoji usage\n• **Image Spam** → Control image frequency\n• **Invite Links** → Block Discord invites\n• **Mass Mentions** → Limit mentions per message\n• **Stickers** → Control sticker usage\n• **Fast Message Spam** → Prevent rapid messaging\n• **Duplicate Text** → Block repeated text\n• **Links** → Control external links\n\n⚡ **Settings**\nEach rule type has customizable thresholds and actions.\n\n⏱️ **Timeout**\nThis selection expires in **15 minutes**",
            color=0x7289da
        )
        
        view = RuleTypeSelectView()
        await interaction.response.edit_message(embed=embed, view=view)

class AutoRule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="autorule")
    async def autorule_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `autorule setup`, `autorule config` or `autorule logs channel set <channel>` commands.")
    
    @autorule_group.command(name="setup")
    async def autorule_setup(self, ctx):
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        embed = discord.Embed(
            title="🛡️ Auto Rule Setup",
            description="**Configure automatic moderation rules for your server.**\n\n📋 **Available Rule Types:**\n\n• **All Caps** → Detect excessive capital letters\n• **Bad Words** → Filter inappropriate language\n• **Emoji Spam** → Limit emoji usage\n• **Image Spam** → Control image frequency\n• **Invite Links** → Block Discord invites\n• **Mass Mentions** → Limit mentions per message\n• **Stickers** → Control sticker usage\n• **Fast Message Spam** → Prevent rapid messaging\n• **Duplicate Text** → Block repeated text\n• **Links** → Control external links\n\n⚡ **Settings**\nEach rule type has customizable thresholds and actions.\n\n⏱️ **Timeout**\nThis selection expires in **15 minutes**",
            color=0x7289da
        )
        
        view = RuleTypeSelectView()
        await ctx.send(embed=embed, view=view)
    
    @autorule_group.command(name="config")
    async def autorule_config(self, ctx):
        configs = await self.bot.db.get_all_autorule_configs(ctx.guild.id)
        
        if not configs:
            embed = discord.Embed(
                title="📋 Auto Rule Configuration",
                description="No auto rules configured for this server.",
                color=0x7289da
            )
        else:
            embed = discord.Embed(
                title="📋 Auto Rule Configuration",
                description=f"**{len(configs)}** auto rules configured:",
                color=0x7289da
            )
            
            for rule_type, config in configs.items():
                rule_name = rule_type.replace('_', ' ').title()
                action = config.get('action', 'Unknown').replace('_', ' ').title()
                status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
                
                settings = ""
                if 'caps_percentage' in config:
                    settings = f" ({config['caps_percentage']}%)"
                elif 'banned_words' in config:
                    settings = f" ({len(config['banned_words'])} words)"
                elif 'max_emojis' in config:
                    settings = f" (max {config['max_emojis']})"
                
                embed.add_field(
                    name=f"{rule_name}{settings}",
                    value=f"**Action:** {action}\n**Status:** {status}",
                    inline=True
                )
        
        await ctx.send(embed=embed)
    
    @autorule_group.group(name="logs")
    async def logs_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use `autorule logs channel set <channel>` to setup logging.")
    
    @logs_group.command(name="channel")
    @app_commands.describe(action="Use 'set' to configure", channel="The channel for autorule logs")
    async def logs_channel(self, ctx, action: str, channel: discord.TextChannel = None):
        if action.lower() != "set":
            await ctx.send("Use `autorule logs channel set <channel>` to setup logging.")
            return
        
        if not channel:
            await ctx.send("Please specify a channel: `autorule logs channel set <channel>`")
            return
        
        if not ctx.author.guild_permissions.manage_guild:
            await ctx.send("You need 'Manage Server' permission to use this command.")
            return
        
        # Save logs channel to database
        await self.bot.db.set_autorule_logs_channel(ctx.guild.id, channel.id)
        
        await ctx.send(f"✅ Auto rule logs will be sent to {channel.mention}")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        # Skip if user has administrator permission
        if message.author.guild_permissions.administrator:
            return
        
        configs = await self.bot.db.get_all_autorule_configs(message.guild.id)
        
        for rule_type, config in configs.items():
            if not config.get('enabled', False):
                continue
            
            action = config.get('action')
            should_punish = False
            
            # Check All Caps
            if rule_type == 'all_caps' and 'caps_percentage' in config:
                caps_count = sum(1 for c in message.content if c.isupper())
                total_letters = sum(1 for c in message.content if c.isalpha())
                if total_letters > 0:
                    caps_percent = (caps_count / total_letters) * 100
                    if caps_percent >= config['caps_percentage']:
                        should_punish = True
            
            # Check Bad Words
            elif rule_type == 'bad_words' and 'banned_words' in config:
                content_lower = message.content.lower()
                for word in config['banned_words']:
                    if word.lower() in content_lower:
                        should_punish = True
                        break
            
            # Check Emoji Spam
            elif rule_type == 'emoji_spam' and 'max_emojis' in config:
                import re
                emoji_count = len(re.findall(r'<:[^:]+:[0-9]+>|[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]+', message.content))
                if emoji_count > config['max_emojis']:
                    should_punish = True
            
            if should_punish:
                await self.execute_action(message, action, rule_type)
                break
    
    async def execute_action(self, message, action, rule_type):
        try:
            if action == 'delete':
                await message.delete()
            
            elif action == 'warn':
                await message.delete()
                await message.channel.send(f"{message.author.mention} Warning: Message violated {rule_type.replace('_', ' ')} rule.", delete_after=5)
            
            elif action in ['automute', 'instant_mute']:
                await message.delete()
                try:
                    import datetime
                    duration = datetime.timedelta(minutes=10) if action == 'automute' else datetime.timedelta(days=28)
                    await message.author.timeout(duration, reason=f"Auto rule violation: {rule_type}")
                    await message.channel.send(f"{message.author.mention} has been muted for violating {rule_type.replace('_', ' ')} rule.", delete_after=5)
                except:
                    await message.channel.send(f"Could not mute {message.author.mention} - missing permissions.", delete_after=5)
            
            elif action in ['autoban', 'instant_ban']:
                await message.delete()
                try:
                    reason = f"Auto rule violation: {rule_type.replace('_', ' ')}"
                    await message.author.ban(reason=reason)
                    await message.channel.send(f"{message.author.mention} has been banned for violating {rule_type.replace('_', ' ')} rule.", delete_after=5)
                except:
                    await message.channel.send(f"Could not ban {message.author.mention} - missing permissions.", delete_after=5)
        
        except Exception as e:
            pass

async def setup(bot):
    await bot.add_cog(AutoRule(bot))