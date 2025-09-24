import discord
from discord.ext import commands

class ExtraOwner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def is_extra_owner(self, guild_id, user_id):
        """Check if user is extra owner for this guild"""
        extra_owners = await self.bot.db.get_extra_owners(guild_id)
        return user_id in extra_owners
    
    @commands.hybrid_group(name="extraowner")
    async def extraowner_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("Use: `/extraowner set <user>`, `/extraowner remove <user>`, `/extraowner list`")
    
    @extraowner_group.command(name="set")
    async def extraowner_set(self, ctx, user: discord.Member):
        """Add extra owner (Server owner only)"""
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner can manage extra owners.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if await self.is_extra_owner(ctx.guild.id, user.id):
            embed = discord.Embed(
                title="⚠️ Already Extra Owner",
                description=f"{user.mention} is already an extra owner.",
                color=0xff8c00
            )
            await ctx.send(embed=embed)
            return
        
        await self.bot.db.add_extra_owner(ctx.guild.id, user.id)
        
        embed = discord.Embed(
            title="✅ Extra Owner Added",
            description=f"{user.mention} has been added as an extra owner.\n\nThey can now bypass antinuke and automod restrictions.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @extraowner_group.command(name="remove")
    async def extraowner_remove(self, ctx, user: discord.Member):
        """Remove extra owner (Server owner only)"""
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ Access Denied",
                description="Only the server owner can manage extra owners.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if not await self.is_extra_owner(ctx.guild.id, user.id):
            embed = discord.Embed(
                title="⚠️ Not Extra Owner",
                description=f"{user.mention} is not an extra owner.",
                color=0xff8c00
            )
            await ctx.send(embed=embed)
            return
        
        await self.bot.db.remove_extra_owner(ctx.guild.id, user.id)
        
        embed = discord.Embed(
            title="✅ Extra Owner Removed",
            description=f"{user.mention} has been removed from extra owners.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)
    
    @extraowner_group.command(name="list")
    async def extraowner_list(self, ctx):
        """List all extra owners"""
        extra_owners = await self.bot.db.get_extra_owners(ctx.guild.id)
        
        embed = discord.Embed(
            title="👑 Extra Owners",
            description=f"**Total:** {len(extra_owners)}",
            color=0x7289da
        )
        
        if extra_owners:
            owner_list = []
            for owner_id in extra_owners:
                try:
                    user_obj = await self.bot.fetch_user(owner_id)
                    owner_list.append(f"• {user_obj.mention} (`{owner_id}`)")
                except:
                    owner_list.append(f"• Unknown User (`{owner_id}`)")
            
            embed.add_field(
                name="Extra Owners",
                value="\n".join(owner_list),
                inline=False
            )
        else:
            embed.add_field(
                name="Extra Owners",
                value="No extra owners set",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtraOwner(bot))