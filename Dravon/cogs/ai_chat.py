import discord
from discord.ext import commands
import aiohttp
import json

class AISetupView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(
        placeholder="🤖 Select AI setup option...",
        options=[
            discord.SelectOption(label="📋 AI Info", description="Learn about AI chat features", value="info"),
            discord.SelectOption(label="📍 Select Channel", description="Choose AI chat channel", value="channel")
        ]
    )
    async def ai_setup_select(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "info":
            embed = discord.Embed(
                title="🤖 AI Chat Information",
                description="**Powered by Google Gemini AI**\n\nFeatures:\n• 🧠 Advanced AI conversations\n• 💬 Natural language processing\n• 🔄 Context-aware responses\n• ⚡ Real-time chat integration\n\n**Premium Feature**: Available for premium users and servers only.",
                color=0x7289da
            )
            embed.add_field(
                name="How it works",
                value="1. Select a channel for AI chat\n2. AI responds automatically to messages\n3. Enjoy intelligent conversations!",
                inline=False
            )
            await interaction.response.edit_message(embed=embed, view=self)
        
        elif select.values[0] == "channel":
            view = ChannelSelectView(self.bot, self.guild_id)
            embed = discord.Embed(
                title="📍 Select AI Chat Channel",
                description="Choose a channel where AI will respond automatically:",
                color=0x7289da
            )
            await interaction.response.edit_message(embed=embed, view=view)

class ChannelSelectView(discord.ui.View):
    def __init__(self, bot, guild_id):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
    
    @discord.ui.select(cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text])
    async def select_channel(self, interaction: discord.Interaction, select: discord.ui.ChannelSelect):
        channel = interaction.guild.get_channel(select.values[0].id)
        
        # Save AI channel to database
        await self.bot.db.set_ai_channel(self.guild_id, channel.id)
        
        embed = discord.Embed(
            title="✅ AI Chat Channel Set",
            description=f"AI chat has been configured for {channel.mention}\n\nThe AI will now respond automatically to messages in this channel.",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

class AIChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = "AIzaSyC0P_JuBhBUYChZs7oTFWyTLe6QnGOst-o"
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    
    async def is_premium_user_or_server(self, user_id, guild_id):
        """Check if user or server has premium"""
        premium_cog = self.bot.get_cog('Premium')
        if not premium_cog:
            return False
        
        user_premium = await premium_cog.is_premium(user_id)
        guild_premium = await premium_cog.is_premium_guild(guild_id)
        
        return user_premium or guild_premium
    
    async def generate_ai_response(self, message_content):
        """Generate AI response using Gemini API"""
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            
            data = {
                "contents": [{
                    "parts": [{
                        "text": message_content
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1024
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers=headers,
                    json=data
                ) as response:
                    response_text = await response.text()
                    print(f"API Response Status: {response.status}")
                    print(f"API Response: {response_text}")
                    
                    if response.status == 200:
                        result = await response.json()
                        if 'candidates' in result and len(result['candidates']) > 0:
                            candidate = result['candidates'][0]
                            if 'content' in candidate and 'parts' in candidate['content']:
                                return candidate['content']['parts'][0]['text']
                    
                    return f"API Error: Status {response.status} - {response_text[:200]}"
        except Exception as e:
            print(f"AI API Error: {e}")
            return f"Connection error: {str(e)}"
    
    @commands.hybrid_group(name="ai", invoke_without_command=True)
    async def ai_group(self, ctx):
        """AI Chat system commands"""
        # Check premium status
        if not await self.is_premium_user_or_server(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="💎 Premium Feature",
                description="AI Chat is a premium feature!\n\nUpgrade to premium to access:\n• 🤖 AI conversations\n• 🧠 Smart responses\n• ⚡ Real-time chat\n\nUse `/premium` to learn more!",
                color=0xff8c00
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🤖 AI Chat System",
            description="**Intelligent AI conversations powered by Google Gemini**\n\nAvailable commands:",
            color=0x7289da
        )
        embed.add_field(
            name="Setup Commands",
            value="`/ai setup` - Configure AI chat\n`/ai reset` - Reset AI configuration\n`/ai status` - Check current status",
            inline=False
        )
        embed.add_field(
            name="How it works",
            value="1. Use `/ai setup` to configure\n2. Select a channel for AI responses\n3. AI responds automatically to messages",
            inline=False
        )
        
        # Add setup button
        view = discord.ui.View(timeout=300)
        setup_btn = discord.ui.Button(
            label="🤖 AI Setup",
            style=discord.ButtonStyle.primary,
            custom_id="ai_setup"
        )
        
        async def setup_callback(interaction):
            setup_view = AISetupView(self.bot, ctx.guild.id)
            setup_embed = discord.Embed(
                title="🤖 AI Chat Setup",
                description="Configure your AI chat system:",
                color=0x7289da
            )
            await interaction.response.send_message(embed=setup_embed, view=setup_view, ephemeral=True)
        
        setup_btn.callback = setup_callback
        view.add_item(setup_btn)
        
        await ctx.send(embed=embed, view=view)
    
    @ai_group.command(name="setup")
    async def ai_setup(self, ctx):
        """Setup AI chat system"""
        # Check premium status
        if not await self.is_premium_user_or_server(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="💎 Premium Required",
                description="AI Chat requires premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        view = AISetupView(self.bot, ctx.guild.id)
        embed = discord.Embed(
            title="🤖 AI Chat Setup",
            description="Configure your AI chat system:",
            color=0x7289da
        )
        await ctx.send(embed=embed, view=view)
    
    @ai_group.command(name="reset")
    async def ai_reset(self, ctx):
        """Reset AI chat configuration"""
        # Check premium status
        if not await self.is_premium_user_or_server(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="💎 Premium Required",
                description="AI Chat requires premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        await self.bot.db.clear_ai_channel(ctx.guild.id)
        
        embed = discord.Embed(
            title="✅ AI Chat Reset",
            description="AI chat configuration has been reset.\n\nUse `/ai setup` to configure again.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @ai_group.command(name="status")
    async def ai_status(self, ctx):
        """Check AI chat status"""
        # Check premium status
        if not await self.is_premium_user_or_server(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="💎 Premium Required",
                description="AI Chat requires premium access!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        ai_channel_id = await self.bot.db.get_ai_channel(ctx.guild.id)
        
        embed = discord.Embed(
            title="🤖 AI Chat Status",
            color=0x7289da
        )
        
        if ai_channel_id:
            channel = ctx.guild.get_channel(ai_channel_id)
            if channel:
                embed.add_field(
                    name="Status",
                    value="🟢 Active",
                    inline=False
                )
                embed.add_field(
                    name="AI Channel",
                    value=channel.mention,
                    inline=False
                )
            else:
                embed.add_field(
                    name="Status",
                    value="🔴 Channel Not Found",
                    inline=False
                )
        else:
            embed.add_field(
                name="Status",
                value="🔴 Not Configured",
                inline=False
            )
        
        embed.add_field(
            name="API Status",
            value="🟢 Google Gemini Connected",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle AI responses in configured channels"""
        if message.author.bot:
            return
        
        if not message.guild:
            return
        
        # Check if message is in AI channel
        ai_channel_id = await self.bot.db.get_ai_channel(message.guild.id)
        if not ai_channel_id or message.channel.id != ai_channel_id:
            return
        
        # Check premium status
        if not await self.is_premium_user_or_server(message.author.id, message.guild.id):
            return
        
        # Don't respond to commands
        if message.content.startswith(('/', '>', '!', '?', '.')):
            return
        
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Generate AI response
                ai_response = await self.generate_ai_response(message.content)
                
                # Send response
                await message.reply(ai_response, mention_author=False)
        
        except Exception as e:
            print(f"AI Response Error: {e}")

async def setup(bot):
    await bot.add_cog(AIChat(bot))