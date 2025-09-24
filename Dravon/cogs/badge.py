import discord
from discord.ext import commands

class Badge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # Available badges
        self.available_badges = {
            "👑": "Crown - Bot Owner",
            "💎": "Premium - Premium User", 
            "📜": "Member - Default Member",
            "🌟": "Star - Special User",
            "🔥": "Fire - Active User",
            "⚡": "Lightning - Fast User",
            "🎯": "Target - Accurate User",
            "🏆": "Trophy - Winner",
            "🎨": "Artist - Creative User",
            "🛡️": "Shield - Protector"
        }
    
    def is_bot_admin(self, user_id):
        """Check if user is bot admin"""
        return user_id == 1037768611126841405 or user_id in getattr(self.bot, 'bot_admins', set())
    
    @commands.hybrid_group(name="badge", hidden=True)
    async def badge_group(self, ctx):
        """Badge management commands (Bot Admin Only)"""
        if not self.is_bot_admin(ctx.author.id):
            return  # Hidden command, no error message
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🏅 Badge Management",
                description="**Available Commands:**\n• `/badge add <user> <badge>` - Add badge to user\n• `/badge remove <user> <badge>` - Remove badge from user\n• `/badge list [user]` - List user badges\n• `/badge available` - Show available badges",
                color=0x7289da
            )
            await ctx.send(embed=embed)
    
    @badge_group.command(name="add")
    async def badge_add(self, ctx, user: discord.Member, badge: str):
        """Add a badge to a user"""
        if badge not in self.available_badges:
            embed = discord.Embed(
                title="❌ Invalid Badge",
                description=f"Badge `{badge}` not found. Use `/badge available` to see available badges.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        try:
            await self.bot.db.add_user_badge(user.id, badge)
            embed = discord.Embed(
                title="✅ Badge Added",
                description=f"Added badge {badge} to {user.mention}",
                color=0x00ff00
            )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @badge_group.command(name="remove")
    async def badge_remove(self, ctx, user: discord.Member, badge: str):
        """Remove a badge from a user"""
        try:
            success = await self.bot.db.remove_user_badge(user.id, badge)
            if success:
                embed = discord.Embed(
                    title="✅ Badge Removed",
                    description=f"Removed badge {badge} from {user.mention}",
                    color=0x00ff00
                )
            else:
                embed = discord.Embed(
                    title="❌ Badge Not Found",
                    description=f"{user.mention} doesn't have badge {badge}",
                    color=0xff0000
                )
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @badge_group.command(name="list")
    async def badge_list(self, ctx, user: discord.Member = None):
        """List badges for a user"""
        if user is None:
            user = ctx.author
        
        try:
            badges = await self.bot.db.get_user_badges(user.id)
            
            embed = discord.Embed(
                title=f"🏅 {user.display_name}'s Badges",
                color=0x7289da
            )
            
            if badges:
                badge_text = ""
                for badge in badges:
                    badge_name = self.available_badges.get(badge, "Unknown Badge")
                    badge_text += f"{badge} {badge_name}\n"
                embed.add_field(name="Badges", value=badge_text, inline=False)
            else:
                embed.add_field(name="Badges", value="No custom badges", inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ Error: {str(e)}")
    
    @badge_group.command(name="available")
    async def badge_available(self, ctx):
        """Show all available badges"""
        embed = discord.Embed(
            title="🏅 Available Badges",
            description="**All available badges:**",
            color=0x7289da
        )
        
        badge_text = ""
        for emoji, description in self.available_badges.items():
            badge_text += f"{emoji} {description}\n"
        
        embed.add_field(name="Badges", value=badge_text, inline=False)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Badge(bot))