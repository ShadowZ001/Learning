import discord
from discord.ext import commands
from datetime import datetime, timedelta

class MessageLeaderboardView(discord.ui.View):
    def __init__(self, bot, guild_id, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.current_page = page
    
    async def get_leaderboard_data(self, page):
        try:
            leaderboard = await self.bot.db.get_message_leaderboard(self.guild_id, page)
            return leaderboard
        except:
            return []
    
    async def create_embed(self, page):
        leaderboard = await self.get_leaderboard_data(page)
        
        embed = discord.Embed(
            title="📊 Message Leaderboard",
            description=f"Top message senders in this server",
            color=0x7289da
        )
        
        if not leaderboard:
            embed.description = "No message data available."
            return embed
        
        guild = self.bot.get_guild(self.guild_id)
        for i, user_data in enumerate(leaderboard, start=page*10+1):
            user = guild.get_member(user_data['user_id'])
            user_name = user.display_name if user else f"Unknown User"
            
            embed.add_field(
                name=f"#{i} {user_name}",
                value=f"📝 {user_data['message_count']} messages",
                inline=True
            )
        
        embed.set_footer(text=f"Page {page + 1} • Use buttons to navigate")
        return embed
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        embed = await self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        embed = await self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        embed = await self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            total_users = await self.bot.db.get_total_message_users(self.guild_id)
            max_page = (total_users - 1) // 10
            self.current_page = max_page
        except:
            self.current_page = 0
        embed = await self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await self.create_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self)

class Messages(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_premium(self, user_id, guild_id):
        """Check if user or guild has premium"""
        try:
            premium_cog = self.bot.get_cog('Premium')
            if premium_cog:
                user_premium = await premium_cog.is_premium(user_id)
                guild_premium = await premium_cog.is_premium_guild(guild_id)
                return user_premium or guild_premium
        except:
            pass
        return False
    
    @commands.hybrid_command(name="message")
    async def message_slash(self, ctx, user: discord.Member = None):
        """Check user message count (slash command)"""
        if user is None:
            user = ctx.author
        
        try:
            all_time = await self.bot.db.get_user_messages(ctx.guild.id, user.id)
            today = await self.bot.db.get_user_messages_today(ctx.guild.id, user.id)
        except:
            all_time = 0
            today = 0
        
        embed = discord.Embed(
            title=f"📊 {user.display_name} Messages",
            color=0x7289da
        )
        
        embed.add_field(
            name="**All time**",
            value=f"• **{all_time:,}** messages in this server!",
            inline=False
        )
        
        embed.add_field(
            name="**Today**",
            value=f"• **{today:,}** messages in this server",
            inline=False
        )
        
        embed.add_field(
            name="📈 Want to see top users?",
            value=f"{user.mention} You want to know users that have top messages? Use `/leaderboard message`",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Message tracking powered by Dravon™")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="leaderboard", fallback="help")
    async def leaderboard_slash_group(self, ctx):
        """Leaderboard commands (slash)"""
        embed = discord.Embed(
            title="🏆 Leaderboard Commands",
            description="**Available leaderboards:**\n• `/leaderboard message` - Message leaderboard",
            color=0x7289da
        )
        await ctx.send(embed=embed)
    
    @leaderboard_slash_group.command(name="message")
    async def message_leaderboard_slash(self, ctx):
        """Show message leaderboard (slash command)"""
        view = MessageLeaderboardView(self.bot, ctx.guild.id)
        embed = await view.create_embed(0)
        await ctx.send(embed=embed, view=view)
    
    @commands.group(name="lb", invoke_without_command=True)
    async def lb_group(self, ctx):
        """Leaderboard commands (prefix only)"""
        embed = discord.Embed(
            title="🏆 Leaderboard Commands",
            description="**Available leaderboards:**\n• `>lb message` - Message leaderboard\n• `>lb m` - Message leaderboard (short)",
            color=0x7289da
        )
        await ctx.send(embed=embed)
    
    @lb_group.command(name="message", aliases=["m", "messages", "msg"])
    async def lb_message_leaderboard(self, ctx):
        """Show message leaderboard (prefix)"""
        view = MessageLeaderboardView(self.bot, ctx.guild.id)
        embed = await view.create_embed(0)
        await ctx.send(embed=embed, view=view)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Track user messages"""
        if message.author.bot or not message.guild:
            return
        
        try:
            await self.bot.db.increment_user_messages(message.guild.id, message.author.id)
        except:
            pass
    
    @commands.command(name="messages", aliases=["m"])
    async def messages_command(self, ctx, user: discord.Member = None):
        """Check user message count"""
        if user is None:
            user = ctx.author
        
        try:
            all_time = await self.bot.db.get_user_messages(ctx.guild.id, user.id)
            today = await self.bot.db.get_user_messages_today(ctx.guild.id, user.id)
        except:
            all_time = 0
            today = 0
        
        embed = discord.Embed(
            title=f"📊 {user.display_name} Messages",
            color=0x7289da
        )
        
        embed.add_field(
            name="**All time**",
            value=f"• **{all_time:,}** messages in this server!",
            inline=False
        )
        
        embed.add_field(
            name="**Today**",
            value=f"• **{today:,}** messages in this server",
            inline=False
        )
        
        embed.add_field(
            name="📈 Want to see top users?",
            value=f"{user.mention} You want to know users that have top messages? Use `>leaderboard message`",
            inline=False
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.set_footer(text="Message tracking powered by Dravon™")
        
        await ctx.send(embed=embed)
    

    


async def setup(bot):
    await bot.add_cog(Messages(bot))