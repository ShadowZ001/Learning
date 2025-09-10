import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class Interactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        """Handle button interactions"""
        if interaction.type == discord.InteractionType.component:
            if interaction.data.get('custom_id') == 'help_command':
                await self.handle_help_button(interaction)
    
    async def handle_help_button(self, interaction: discord.Interaction):
        """Handle help command button click"""
        embed = discord.Embed(
            title="🌟 Dravon Help Center",
            description="**Your all-in-one Discord server management solution**\n\nDravon offers comprehensive server management with advanced features including moderation, security, tickets, giveaways, premium perks, and much more!\n\n**📂 Command Categories:**\n🛡️ **Moderation** - Ban, kick, mute, warn users\n🔒 **Security** - AntiNuke protection system\n🎫 **Tickets** - Complete ticket management\n🎉 **Giveaways** - Falcon-style giveaway system\n⚙️ **Server Setup** - Welcome, leave, boost messages\n🤖 **AutoMod** - Automatic moderation\n📊 **Information** - Server and bot stats\n🎨 **Embed Builder** - Custom embed creation\n🎵 **Music Player** - Play music from multiple platforms\n🎮 **Fun Commands** - Interactive anime GIF commands\n💎 **Premium** - Exclusive premium features\n🔧 **Utility** - Prefix, purge, and more\n\n*Use `>help` or `/help` for detailed command information!*",
            color=0x7289da
        )
        
        embed.add_field(
            name="🚀 Quick Start Commands",
            value="`>help` - Full help menu\n`>serverinfo` - Server information\n`>botinfo` - Bot statistics\n`>premium` - Premium features",
            inline=True
        )
        
        embed.add_field(
            name="⚙️ Setup Commands",
            value="`>welcome setup` - Welcome messages\n`>antinuke setup` - Security system\n`>automod setup` - Auto moderation\n`>ticket setup` - Ticket system",
            inline=True
        )
        
        embed.set_thumbnail(url=interaction.client.user.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1369352923896741924/1413146132405817487/f41e57df-936d-428a-8aa8-a0b4ca2a1e64.jpg?ex=68bade64&is=68b98ce4&hm=b47dca3ee7abd906adf59b9a6974c047a2ee5079928e6b3ba37255ea7b9945f7&")
        embed = add_dravon_footer(embed)
        
        # Add support button
        view = discord.ui.View(timeout=None)
        support_button = discord.ui.Button(
            label="Support Server",
            style=discord.ButtonStyle.link,
            url="https://discord.gg/UKR78VcEtg",
            emoji="🛠️"
        )
        view.add_item(support_button)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Interactions(bot))