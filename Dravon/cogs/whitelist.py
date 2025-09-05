import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class Whitelist(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.extra_owners = [1037768611126841405]  # Bot admin ID
    
    def is_owner_or_extra_owner(self, user_id: int, guild_id: int) -> bool:
        """Check if user is server owner or extra owner"""
        guild = self.bot.get_guild(guild_id)
        if not guild:
            return False
        
        # Check if user is server owner
        if guild.owner_id == user_id:
            return True
        
        # Check if user is extra owner (bot admin)
        if user_id in self.extra_owners:
            return True
        
        return False
    
    async def is_whitelisted(self, user_id: int, guild_id: int) -> bool:
        """Check if user is whitelisted"""
        # Server owner and extra owners are always whitelisted
        if self.is_owner_or_extra_owner(user_id, guild_id):
            return True
        
        # Check database whitelist
        whitelist_data = await self.bot.db.get_whitelist_user(guild_id, user_id)
        return whitelist_data is not None
    
    @commands.hybrid_group(name="whitelist")
    async def whitelist_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="⚪ Whitelist Commands",
                description="Manage users who can bypass AntiNuke and AutoMod systems.\n\n**Available Commands:**\n`>whitelist <user>` - Add user to whitelist\n`>whitelist list` - View all whitelisted users\n`>whitelist remove <user>` - Remove user from whitelist",
                color=0x7289da
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @whitelist_group.command(name="add")
    async def whitelist_add(self, ctx, user: discord.Member):
        """Add a user to the whitelist"""
        if not self.is_owner_or_extra_owner(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner and extra owners can manage the whitelist.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Check if user is already whitelisted
        if await self.is_whitelisted(user.id, ctx.guild.id):
            embed = discord.Embed(
                title="⚠️ Already Whitelisted",
                description=f"{user.mention} is already whitelisted or is a server owner/extra owner.",
                color=0xffaa00
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Add to whitelist
        await self.bot.db.add_whitelist_user(ctx.guild.id, user.id)
        
        embed = discord.Embed(
            title="✅ User Whitelisted",
            description=f"{user.mention} has been added to the whitelist.\n\nThey can now bypass:\n• AntiNuke protection\n• AutoMod filters\n• Other security measures",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @whitelist_group.command(name="list")
    async def whitelist_list(self, ctx):
        """List all whitelisted users"""
        if not self.is_owner_or_extra_owner(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner and extra owners can view the whitelist.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Get whitelist from database
        whitelist_users = await self.bot.db.get_whitelist_users(ctx.guild.id)
        
        embed = discord.Embed(
            title="⚪ Whitelist Users",
            description="Users who can bypass AntiNuke and AutoMod systems:",
            color=0x7289da
        )
        
        # Always include server owner and extra owners
        permanent_whitelist = []
        if ctx.guild.owner:
            permanent_whitelist.append(f"👑 {ctx.guild.owner.mention} (Server Owner)")
        
        for owner_id in self.extra_owners:
            user = ctx.guild.get_member(owner_id)
            if user:
                permanent_whitelist.append(f"⭐ {user.mention} (Extra Owner)")
        
        if permanent_whitelist:
            embed.add_field(
                name="🔒 Permanent Whitelist",
                value="\n".join(permanent_whitelist),
                inline=False
            )
        
        # Add database whitelist users
        if whitelist_users:
            user_list = []
            for user_data in whitelist_users:
                user_id = user_data.get("user_id")
                user = ctx.guild.get_member(user_id)
                if user:
                    user_list.append(f"⚪ {user.mention}")
                else:
                    user_list.append(f"⚪ <@{user_id}> (Left Server)")
            
            if user_list:
                embed.add_field(
                    name="📝 Added to Whitelist",
                    value="\n".join(user_list),
                    inline=False
                )
        else:
            embed.add_field(
                name="📝 Added to Whitelist",
                value="No additional users in whitelist",
                inline=False
            )
        
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @whitelist_group.command(name="remove")
    async def whitelist_remove(self, ctx, user: discord.Member):
        """Remove a user from the whitelist"""
        if not self.is_owner_or_extra_owner(ctx.author.id, ctx.guild.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner and extra owners can manage the whitelist.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Check if user is permanently whitelisted (owner/extra owner)
        if self.is_owner_or_extra_owner(user.id, ctx.guild.id):
            embed = discord.Embed(
                title="❌ Cannot Remove",
                description=f"{user.mention} is a server owner or extra owner and cannot be removed from the whitelist.",
                color=0xff0000
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Check if user is in whitelist
        whitelist_data = await self.bot.db.get_whitelist_user(ctx.guild.id, user.id)
        if not whitelist_data:
            embed = discord.Embed(
                title="⚠️ Not Whitelisted",
                description=f"{user.mention} is not in the whitelist.",
                color=0xffaa00
            )
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
            return
        
        # Remove from whitelist
        await self.bot.db.remove_whitelist_user(ctx.guild.id, user.id)
        
        embed = discord.Embed(
            title="✅ User Removed",
            description=f"{user.mention} has been removed from the whitelist.\n\nThey will now be subject to:\n• AntiNuke protection\n• AutoMod filters\n• Other security measures",
            color=0x00ff00
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    


async def setup(bot):
    await bot.add_cog(Whitelist(bot))