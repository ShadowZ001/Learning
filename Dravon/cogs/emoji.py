import discord
from discord.ext import commands

class EmojiCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='emoji', aliases=['emojis'])
    async def emoji_list(self, ctx):
        """Show available emoji placeholders"""
        embed = discord.Embed(
            title="🎭 Available Emoji Placeholders",
            description="Use these placeholders in your messages and they'll be converted to emojis!",
            color=0x58a6ff
        )
        
        # Basic emojis
        basic = ":smile: :grin: :joy: :heart: :fire: :star: :thumbsup: :thumbsdown: :clap: :wave:"
        embed.add_field(name="😊 Basic Emojis", value=basic, inline=False)
        
        # Utility emojis
        utility = ":check: :x: :warning: :info: :question: :exclamation:"
        embed.add_field(name="⚠️ Utility", value=utility, inline=False)
        
        # Numbers
        numbers = ":one: :two: :three: :four: :five: :six: :seven: :eight: :nine: :ten:"
        embed.add_field(name="🔢 Numbers", value=numbers, inline=False)
        
        # Music
        music = ":musical_note: :notes: :microphone: :headphones: :speaker: :mute:"
        embed.add_field(name="🎵 Music", value=music, inline=False)
        
        # Status
        status = ":online: :idle: :dnd: :offline: :streaming:"
        embed.add_field(name="🟢 Status", value=status, inline=False)
        
        embed.set_footer(text="Example: Type ':fire: This is lit!' and it becomes '🔥 This is lit!'")
        
        await ctx.send(embed=embed)
    
    @commands.command(name='addemoji', hidden=True)
    @commands.has_permissions(administrator=True)
    async def add_emoji(self, ctx, placeholder: str, emoji: str):
        """Add custom emoji placeholder (Admin only)"""
        if not placeholder.startswith(':') or not placeholder.endswith(':'):
            await ctx.send("❌ Placeholder must be in format `:name:`")
            return
        
        self.bot.emoji_handler.add_emoji(placeholder, emoji)
        await ctx.send(f"✅ Added emoji placeholder: {placeholder} → {emoji}")

async def setup(bot):
    await bot.add_cog(EmojiCommands(bot))