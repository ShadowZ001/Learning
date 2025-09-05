import discord
from discord.ext import commands
from discord import app_commands
import math

class InviteLeaderboardView(discord.ui.View):
    def __init__(self, bot, guild_id, user_id, page=0):
        super().__init__(timeout=300)
        self.bot = bot
        self.guild_id = guild_id
        self.user_id = user_id
        self.page = page
    
    async def get_leaderboard_data(self):
        """Get invite data for the guild"""
        invites = await self.bot.db.get_guild_invites(self.guild_id)
        # Sort by total invites (valid + fake + left)
        sorted_invites = sorted(invites.items(), key=lambda x: x[1].get('total', 0), reverse=True)
        return sorted_invites
    
    async def create_embed(self):
        """Create leaderboard embed"""
        data = await self.get_leaderboard_data()
        total_pages = max(1, math.ceil(len(data) / 10))
        
        # Ensure page is within bounds
        self.page = max(0, min(self.page, total_pages - 1))
        
        embed = discord.Embed(
            title="🦅 Invite Leaderboard",
            description="Track who's inviting the most members!\nUse the emoji buttons below to navigate.\n🏅 Rewards for top inviters!",
            color=0x7289da
        )
        
        if not data:
            embed.add_field(name="No Data", value="No invite data available yet.", inline=False)
        else:
            start_idx = self.page * 10
            end_idx = min(start_idx + 10, len(data))
            
            leaderboard_text = ""
            for i in range(start_idx, end_idx):
                user_id, invite_data = data[i]
                rank = i + 1
                
                # Get user
                guild = self.bot.get_guild(self.guild_id)
                user = guild.get_member(int(user_id))
                username = user.display_name if user else f"Unknown User ({user_id})"
                
                total = invite_data.get('total', 0)
                valid = invite_data.get('valid', 0)
                fake = invite_data.get('fake', 0)
                left = invite_data.get('left', 0)
                
                # Highlight current user
                if int(user_id) == self.user_id:
                    leaderboard_text += f"**#{rank} {username}** ⭐\n"
                else:
                    leaderboard_text += f"#{rank} {username}\n"
                
                leaderboard_text += f"📊 Total: {total} | ✅ Valid: {valid} | ❌ Fake: {fake} | 👋 Left: {left}\n\n"
            
            embed.add_field(name="Rankings", value=leaderboard_text or "No data", inline=False)
        
        embed.set_footer(text=f"Page {self.page + 1}/{total_pages} • Requested by {self.bot.get_user(self.user_id).display_name}")
        return embed
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.page = 0
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.page > 0:
            self.page -= 1
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await self.get_leaderboard_data()
        total_pages = max(1, math.ceil(len(data) / 10))
        if self.page < total_pages - 1:
            self.page += 1
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = await self.get_leaderboard_data()
        total_pages = max(1, math.ceil(len(data) / 10))
        self.page = total_pages - 1
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(emoji="🔄", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = await self.create_embed()
        await interaction.response.edit_message(embed=embed, view=self)

class InviteLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    


async def setup(bot):
    await bot.add_cog(InviteLeaderboard(bot))