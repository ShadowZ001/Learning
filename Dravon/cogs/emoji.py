import discord
from discord.ext import commands

class EmojiView(discord.ui.View):
    def __init__(self, bot, guild, emojis, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild = guild
        self.emojis = emojis
        self.page = page
        self.per_page = 10
        self.max_pages = (len(emojis) - 1) // self.per_page + 1
    
    def create_embed(self):
        start = self.page * self.per_page
        end = start + self.per_page
        page_emojis = self.emojis[start:end]
        
        embed = discord.Embed(
            title=f"😀 {self.guild.name} Emojis",
            description=f"**Total Emojis:** {len(self.emojis)}\n**Page:** {self.page + 1}/{self.max_pages}",
            color=0x7289da
        )
        
        if page_emojis:
            emoji_text = ""
            for emoji in page_emojis:
                emoji_text += f"{emoji} `:{emoji.name}:` - {emoji.id}\n"
            
            embed.add_field(
                name="Emojis",
                value=emoji_text,
                inline=False
            )
        else:
            embed.add_field(
                name="No Emojis",
                value="This server has no custom emojis.",
                inline=False
            )
        
        embed.set_footer(text=f"Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
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

class Emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="emoji")
    async def emoji_command(self, ctx):
        """Show all server emojis with navigation"""
        emojis = ctx.guild.emojis
        
        if not emojis:
            embed = discord.Embed(
                title="😀 Server Emojis",
                description="This server has no custom emojis.",
                color=0x7289da
            )
            embed.set_footer(text="Powered by Dravon™", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
            return
        
        view = EmojiView(self.bot, ctx.guild, emojis)
        embed = view.create_embed()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Emoji(bot))