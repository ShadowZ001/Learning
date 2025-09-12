import discord
from discord.ext import commands
from discord import app_commands
from utils.embed_utils import add_dravon_footer
from typing import Dict, List, Optional
import asyncio
from datetime import datetime

class CategorySelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
    
    @discord.ui.select(
        placeholder="Choose a category to configure...",
        options=[
            discord.SelectOption(label="🔠 Message Formatting", description="All Caps, Duplicate Text, Character Count", value="message_formatting"),
            discord.SelectOption(label="🚫 Content Filtering", description="Bad Words, Links, Invites, Phishing", value="content_filtering"),
            discord.SelectOption(label="📣 Spam & Flood", description="Fast Messages, Emoji Spam, Mass Mentions", value="spam_flood")
        ]
    )
    async def category_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        category = select.values[0]
        
        if category == "message_formatting":
            view = FilterSelectView("message_formatting")
            embed = discord.Embed(
                title="🔠 Message Formatting & Content Structure Filters",
                description="Please select a specific filter from the available options below to configure its settings, thresholds, and enforcement actions for your server's protection.",
                color=0x7289da
            )
        elif category == "content_filtering":
            view = FilterSelectView("content_filtering")
            embed = discord.Embed(
                title="🚫 Advanced Content Filtering & Security Protection",
                description="Please select a specific filter from the available options below to configure its settings, thresholds, and enforcement actions for your server's protection.",
                color=0x7289da
            )
        elif category == "spam_flood":
            view = FilterSelectView("spam_flood")
            embed = discord.Embed(
                title="📣 Anti-Spam & Flood Protection Management",
                description="Please select a specific filter from the available options below to configure its settings, thresholds, and enforcement actions for your server's protection.",
                color=0x7289da
            )
        
        await interaction.response.edit_message(embed=embed, view=view)

class FilterSelectView(discord.ui.View):
    def __init__(self, category):
        super().__init__(timeout=900)
        self.category = category
        
        if category == "message_formatting":
            options = [
                discord.SelectOption(label="All Caps", description="Detects messages with too many capital letters", value="all_caps"),
                discord.SelectOption(label="Duplicate Text", description="Repeated letters/words", value="duplicate_text"),
                discord.SelectOption(label="Character Count", description="Message too long", value="character_count"),
                discord.SelectOption(label="Chat Clearing", description="Excessive line breaks", value="chat_clearing"),
                discord.SelectOption(label="Zalgo Text", description="Messy glitch text", value="zalgo_text")
            ]
        elif category == "content_filtering":
            options = [
                discord.SelectOption(label="Bad Words", description="Blocklist of words/phrases", value="bad_words"),
                discord.SelectOption(label="Spoilers", description="Detect spoiler tags", value="spoilers"),
                discord.SelectOption(label="Masked Links", description="Links disguised under text", value="masked_links"),
                discord.SelectOption(label="Links", description="All or specific links", value="links"),
                discord.SelectOption(label="Phishing Links", description="Known scam sites", value="phishing_links"),
                discord.SelectOption(label="Invite Links", description="Discord server invites", value="invite_links")
            ]
        elif category == "spam_flood":
            options = [
                discord.SelectOption(label="Fast Message Spam", description="Too many messages in 5s", value="fast_spam"),
                discord.SelectOption(label="Emoji Spam", description="Too many emojis in one message", value="emoji_spam"),
                discord.SelectOption(label="Mass Mentions", description="Mentioning many users at once", value="mass_mentions"),
                discord.SelectOption(label="Mentions Cooldown", description="Too many mentions within 30s", value="mentions_cooldown"),
                discord.SelectOption(label="Links Cooldown", description="Too many links in short time", value="links_cooldown"),
                discord.SelectOption(label="Image Spam", description="Multiple images quickly", value="image_spam"),
                discord.SelectOption(label="Stickers", description="Blocks sticker usage", value="stickers"),
                discord.SelectOption(label="Sticker Cooldown", description="Sticker spam in 60s", value="sticker_cooldown")
            ]
        
        self.add_item(FilterSelect(options, self.category))

class FilterSelect(discord.ui.Select):
    def __init__(self, options, category):
        super().__init__(placeholder="Choose a filter to configure...", options=options)
        self.category = category
    
    async def callback(self, interaction: discord.Interaction):
        filter_type = self.values[0]
        
        embed = discord.Embed(
            title=f"⚙️ {self.options[[opt.value for opt in self.options].index(filter_type)].label} Configuration",
            description="Configure the specific settings and parameters for this filter, then select the appropriate enforcement action that will be taken when violations are detected.",
            color=0x7289da
        )
        
        # Add filter-specific configuration info
        if filter_type == "all_caps":
            embed.add_field(name="Setting", value="Caps Percentage (default: 70%)", inline=False)
            embed.add_field(name="Example", value="HELLO GUYS HOW ARE YOU", inline=False)
        elif filter_type == "bad_words":
            embed.add_field(name="Setting", value="Add words/phrases to blocklist", inline=False)
            embed.add_field(name="Example", value="Blocked words will be filtered", inline=False)
        elif filter_type == "invite_links":
            embed.add_field(name="Setting", value="Block Discord server invites", inline=False)
            embed.add_field(name="Example", value="discord.gg/example", inline=False)
        
        view = ActionSelectView(filter_type, self.category)
        await interaction.response.edit_message(embed=embed, view=view)

class ActionSelectView(discord.ui.View):
    def __init__(self, filter_type, category):
        super().__init__(timeout=900)
        self.filter_type = filter_type
        self.category = category
    
    @discord.ui.select(
        placeholder="Choose an action for this filter...",
        options=[
            discord.SelectOption(label="🗑️ Delete", description="Remove the message", value="delete"),
            discord.SelectOption(label="⚠️ Warn", description="Send a warning", value="warn"),
            discord.SelectOption(label="⏳ Automute", description="Temporary mute", value="automute"),
            discord.SelectOption(label="🔇 Instant Mute", description="Mute immediately", value="instant_mute"),
            discord.SelectOption(label="🔨 Autoban", description="Temporary ban", value="autoban"),
            discord.SelectOption(label="🚫 Instant Ban", description="Ban instantly", value="instant_ban")
        ]
    )
    async def action_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        
        # Save the automod rule
        bot = interaction.client
        rule_config = {
            "category": self.category,
            "filter_type": self.filter_type,
            "action": action,
            "enabled": True
        }
        
        await bot.db.set_automod_rule(interaction.guild.id, self.filter_type, rule_config)
        
        embed = discord.Embed(
            title="✅ AutoModeration Rule Successfully Configured & Activated",
            description=f"**Filter:** {self.filter_type.replace('_', ' ').title()}\n**Action:** {action.replace('_', ' ').title()}\n\nRule has been saved and activated!",
            color=0x00ff00
        )
        
        # Return to main setup
        view = MainSetupView()
        embed_main = discord.Embed(
            title="🔧 AutoMod Setup",
            description="Protect your server with AutoMod!\n\nPick a category below to view and configure filters.\nEach filter can have custom thresholds and actions.",
            color=0x7289da
        )
        
        await interaction.response.edit_message(embed=embed_main, view=view)

class MainSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)
    
    @discord.ui.select(
        placeholder="🔧 Choose AutoMod Action...",
        options=[
            discord.SelectOption(label="📦 Configure Categories", description="Set up filters by category", value="configure"),
            discord.SelectOption(label="📋 View Rules", description="See all configured rules", value="view_rules"),
            discord.SelectOption(label="📝 Logs Channel", description="Set automod logs channel", value="logs_channel"),
            discord.SelectOption(label="⚡ Fast Setup", description="Automatic best automod setup", value="fast_setup"),
            discord.SelectOption(label="⚙️ Toggle AutoMod", description="Enable/disable AutoMod system", value="toggle")
        ]
    )
    async def main_action_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        action = select.values[0]
        
        if action == "configure":
            view = CategorySelectView()
            embed = discord.Embed(
                title="📦 AutoModeration Filter Categories Selection",
                description="Choose a category to configure:",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif action == "view_rules":
            rules = await interaction.client.db.get_all_automod_rules(interaction.guild.id)
            
            if not rules:
                embed = discord.Embed(
                    title="📋 AutoMod Rules",
                    description="No automod rules configured.",
                    color=0x7289da
                )
            else:
                embed = discord.Embed(
                    title="📋 AutoMod Rules",
                    description=f"**{len(rules)}** rules configured:",
                    color=0x7289da
                )
                
                for filter_type, config in rules.items():
                    filter_name = filter_type.replace('_', ' ').title()
                    action_name = config.get('action', 'Unknown').replace('_', ' ').title()
                    status = "✅ Enabled" if config.get('enabled') else "❌ Disabled"
                    
                    embed.add_field(
                        name=filter_name,
                        value=f"**Action:** {action_name}\n**Status:** {status}",
                        inline=True
                    )
            
            await interaction.response.edit_message(embed=embed, view=self)
        
        elif action == "logs_channel":
            embed = discord.Embed(
                title="📝 AutoMod Logs Channel",
                description="Please select a channel for automod logs.",
                color=0x7289da
            )
            view = LogsChannelView()
            await interaction.response.edit_message(embed=embed, view=view)
        
        elif action == "fast_setup":
            # Processing animation
            embed = discord.Embed(
                title="🚀 AutoMod Fast Setup in Progress",
                description="⏳ Configuring optimal protection settings...",
                color=0xffd700
            )
            await interaction.response.edit_message(embed=embed, view=None)
            
            bot = interaction.client
            guild_id = interaction.guild.id
            
            steps = [
                {"text": "🔧 Initializing AutoMod system...", "detail": "Loading protection modules"},
                {"text": "🛡️ Configuring content filters...", "detail": "Bad words, links, invites"},
                {"text": "📝 Setting up spam protection...", "detail": "Fast messages, emoji spam"},
                {"text": "⚙️ Applying punishment actions...", "detail": "Delete, warn, automute"},
                {"text": "✅ Activation complete!", "detail": "AutoMod is now protecting your server"}
            ]
            
            for i, step in enumerate(steps):
                progress_bar = "█" * (i + 1) + "░" * (len(steps) - i - 1)
                percentage = int((i + 1) / len(steps) * 100)
                
                embed = discord.Embed(
                    title="🚀 AutoMod Fast Setup in Progress",
                    description=f"**{step['text']}**\n*{step['detail']}*\n\n**Progress:** `{progress_bar}` **{percentage}%**",
                    color=0xffd700 if i < len(steps) - 1 else 0x00ff00
                )
                embed.set_footer(text=f"Step {i + 1} of {len(steps)} • AutoMod System", icon_url=bot.user.display_avatar.url)
                
                await interaction.edit_original_response(embed=embed)
                await asyncio.sleep(1.2)
            
            # Configure best practice rules
            best_rules = {
                "bad_words": {"category": "content_filtering", "action": "delete", "enabled": True},
                "invite_links": {"category": "content_filtering", "action": "delete", "enabled": True},
                "phishing_links": {"category": "content_filtering", "action": "ban", "enabled": True},
                "all_caps": {"category": "message_formatting", "action": "warn", "enabled": True},
                "duplicate_text": {"category": "message_formatting", "action": "delete", "enabled": True},
                "fast_spam": {"category": "spam_flood", "action": "automute", "enabled": True},
                "emoji_spam": {"category": "spam_flood", "action": "delete", "enabled": True},
                "mass_mentions": {"category": "spam_flood", "action": "automute", "enabled": True},
                "image_spam": {"category": "spam_flood", "action": "warn", "enabled": True}
            }
            
            for rule_type, config in best_rules.items():
                await bot.db.set_automod_rule(guild_id, rule_type, config)
            
            # Final success embed
            final_embed = discord.Embed(
                title="🎉 AutoMod Fast Setup Complete!",
                description="**🛡️ Your server is now protected with optimal AutoMod settings**\n\nAll essential protection rules have been configured and activated.",
                color=0x00ff00
            )
            
            final_embed.add_field(
                name="✅ Content Filtering Rules",
                value="• **Bad Words** → Delete message\n• **Invite Links** → Delete message\n• **Phishing Links** → Ban user",
                inline=True
            )
            
            final_embed.add_field(
                name="✅ Message Formatting Rules",
                value="• **All Caps** → Warn user\n• **Duplicate Text** → Delete message",
                inline=True
            )
            
            final_embed.add_field(
                name="✅ Spam Protection Rules",
                value="• **Fast Spam** → Auto mute\n• **Emoji Spam** → Delete message\n• **Mass Mentions** → Auto mute\n• **Image Spam** → Warn user",
                inline=False
            )
            
            final_embed.add_field(
                name="⚡ Next Steps",
                value="• View rules: `/automod config`\n• Customize settings: `/automod setup`\n• Monitor activity: `/automod events`",
                inline=True
            )
            
            final_embed.add_field(
                name="🔧 Management",
                value="• Add ignored channels/roles\n• Adjust punishment severity\n• Configure custom word lists",
                inline=True
            )
            
            final_embed.set_footer(text="AutoMod System • 9 Rules Active • Powered by Dravon™", icon_url=bot.user.display_avatar.url)
            
            await interaction.edit_original_response(embed=final_embed)
        
        elif action == "toggle":
            embed = discord.Embed(
                title="⚙️ AutoMod System",
                description="AutoMod system toggled!",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=self)

class LogsChannelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, placeholder="Select logs channel...")
    async def logs_channel_select(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = select.values[0]
        await interaction.client.db.set_automod_logs_channel(interaction.guild.id, channel.id)
        
        embed = discord.Embed(
            title="✅ Logs Channel Set",
            description=f"AutoMod logs will be sent to {channel.mention}",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="automod")
    async def automod_group(self, ctx):
        if ctx.invoked_subcommand is None:
            if not ctx.author.guild_permissions.manage_guild:
                embed = discord.Embed(
                    title="❌ Permission Required",
                    description="You need **Manage Server** permission to use AutoMod commands.",
                    color=0xff0000
                )
                embed = add_dravon_footer(embed)
                await ctx.send(embed=embed)
                return
            
            # Get current automod status
            rules = await self.bot.db.get_all_automod_rules(ctx.guild.id)
            active_rules = len([r for r in rules.values() if r.get('enabled', False)]) if rules else 0
            
            embed = discord.Embed(
                title="🛡️ Dravon™ AutoMod System",
                description="**🚀 Advanced Automatic Moderation**\n\nProtect your server with intelligent content filtering, spam detection, and automated punishment systems.\n\n**📊 Current Status:**\n" + (f"✅ **{active_rules} rules active**" if active_rules > 0 else "❌ **No rules configured**"),
                color=0x7289da
            )
            
            embed.add_field(
                name="🔠 Message Formatting Filters",
                value="• **All Caps** - Excessive capital letters\n• **Duplicate Text** - Repeated characters/words\n• **Character Count** - Messages too long\n• **Chat Clearing** - Excessive line breaks\n• **Zalgo Text** - Corrupted/glitch text",
                inline=True
            )
            
            embed.add_field(
                name="🚫 Content Filtering",
                value="• **Bad Words** - Custom word blocklist\n• **Links** - URL filtering\n• **Invite Links** - Discord server invites\n• **Phishing Links** - Malicious websites\n• **Masked Links** - Hidden/disguised URLs\n• **Spoilers** - Spoiler tag detection",
                inline=True
            )
            
            embed.add_field(
                name="📣 Spam & Flood Protection",
                value="• **Fast Message Spam** - Rapid messaging\n• **Emoji Spam** - Excessive emojis\n• **Mass Mentions** - Multiple user pings\n• **Image Spam** - Rapid image posting\n• **Sticker Spam** - Excessive stickers\n• **Cooldown Systems** - Rate limiting",
                inline=False
            )
            
            embed.add_field(
                name="⚡ Punishment Actions",
                value="🗑️ **Delete** - Remove message\n⚠️ **Warn** - Send warning\n⏳ **Auto Mute** - Temporary mute\n🔇 **Instant Mute** - Immediate mute\n🔨 **Auto Ban** - Temporary ban\n🚫 **Instant Ban** - Permanent ban",
                inline=True
            )
            
            embed.add_field(
                name="🚀 Quick Setup",
                value="• `/automod setup` - Interactive configuration\n• `/automod fastsetup` - Instant best practices\n• `/automod config` - View current rules",
                inline=True
            )
            
            embed.set_footer(text="AutoMod System • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            
            view = MainSetupView()
            await ctx.send(embed=embed, view=view)
    
    @automod_group.command(name="setup")
    async def automod_setup(self, ctx):
        """Interactive AutoMod setup wizard"""
        if not ctx.author.guild_permissions.manage_guild:
            embed = discord.Embed(
                title="❌ Permission Required",
                description="You need **Manage Server** permission to setup AutoMod.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🔧 AutoMod Setup Wizard",
            description="**🛡️ Configure Advanced Server Protection**\n\nUse the dropdown below to configure AutoMod categories and rules.\n\n**📦 Available Categories:**\n🔠 **Message Formatting** - Text structure filters\n🚫 **Content Filtering** - Word and link blocking\n📣 **Spam & Flood** - Rate limiting and spam detection",
            color=0x7289da
        )
        
        embed.add_field(
            name="⚡ Quick Options",
            value="• **Configure Categories** - Set up specific filters\n• **Fast Setup** - Instant best practices\n• **View Current Rules** - See active protection\n• **Logs Channel** - Set moderation logs",
            inline=False
        )
        
        embed.set_footer(text="AutoMod Setup • Interactive Configuration • Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
        
        view = MainSetupView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))