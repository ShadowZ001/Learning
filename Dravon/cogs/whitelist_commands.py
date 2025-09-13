import discord
from discord.ext import commands

class WhitelistCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_users = {}  # guild_id: [user_ids]
        self.extra_owners = {}       # guild_id: [user_ids]
    
    @commands.hybrid_group(name="whitelist")
    async def whitelist_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🔐 Whitelist System",
                description="Manage whitelisted users for your server",
                color=0x2f3136
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
    
    @whitelist_group.command(name="list")
    async def whitelist_list(self, ctx):
        """List all whitelisted users"""
        embed = discord.Embed(
            title="📝 Whitelisted Users",
            color=0x2f3136
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        if ctx.guild.id in self.whitelisted_users and self.whitelisted_users[ctx.guild.id]:
            user_list = []
            for user_id in self.whitelisted_users[ctx.guild.id][:10]:
                user = self.bot.get_user(user_id)
                if user:
                    user_list.append(f"• {user.mention} (`{user.id}`)")
                else:
                    user_list.append(f"• Unknown User (`{user_id}`)")
            
            embed.add_field(
                name=f"👥 Whitelisted Users ({len(self.whitelisted_users[ctx.guild.id])})",
                value="\n".join(user_list) if user_list else "No users whitelisted",
                inline=False
            )
        else:
            embed.add_field(
                name="👥 Whitelisted Users",
                value="No users whitelisted",
                inline=False
            )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="extraowner")
    async def extraowner_group(self, ctx):
        if ctx.author.id != ctx.guild.owner_id:
            embed = discord.Embed(
                title="❌ | Access Denied",
                description="Only the Server Owner can manage extra owners!",
                color=0x2f3136
            )
            await ctx.send(embed=embed)
            return
        
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="👑 Extra Owner System",
                description="Manage extra owners for your server",
                color=0x2f3136
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)
    
    @extraowner_group.command(name="list")
    async def extraowner_list(self, ctx):
        """List all extra owners"""
        embed = discord.Embed(
            title="👑 Extra Owners",
            color=0x2f3136
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        
        # Always show main bot admin
        embed.add_field(
            name="🔧 Bot Administrator",
            value="• <@1037768611126841405> (`1037768611126841405`)",
            inline=False
        )
        
        if ctx.guild.id in self.extra_owners and self.extra_owners[ctx.guild.id]:
            user_list = []
            for user_id in self.extra_owners[ctx.guild.id][:10]:
                user = self.bot.get_user(user_id)
                if user:
                    user_list.append(f"• {user.mention} (`{user.id}`)")
                else:
                    user_list.append(f"• Unknown User (`{user_id}`)")
            
            embed.add_field(
                name=f"👑 Extra Owners ({len(self.extra_owners[ctx.guild.id])})",
                value="\n".join(user_list) if user_list else "No extra owners",
                inline=False
            )
        else:
            embed.add_field(
                name="👑 Extra Owners",
                value="No extra owners added",
                inline=False
            )
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(WhitelistCommands(bot))