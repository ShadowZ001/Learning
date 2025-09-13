import discord
from discord.ext import commands
from utils.embed_utils import add_dravon_footer

class AutoModConfig(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="automod")
    async def automod_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"AutoMod — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="📝 Configuration Commands",
                value="`>automod setup` - Interactive setup wizard\n`>automod config` - View current settings\n`>automod logs <channel>` - Set logs channel\n`>automod reset` - Reset all settings",
                inline=False
            )
            
            embed.add_field(
                name="🛡️ Filter Commands",
                value="`>automod spam enable/disable` - Spam protection\n`>automod links enable/disable` - Link filtering\n`>automod caps enable/disable` - Caps filtering\n`>automod profanity enable/disable` - Bad word filter",
                inline=False
            )
            
            embed.add_field(
                name="📱 Media Commands",
                value="`>media` - Media filter settings\n`>media channel add <channel>` - Add media channel\n`>media channel remove <channel>` - Remove media channel\n`>media channel list` - List media channels\n`>media channel reset` - Reset media channels",
                inline=False
            )
            
            embed.add_field(
                name="🔓 Bypass Commands",
                value="`>media bypass add <role>` - Add bypass role\n`>media bypass remove <role>` - Remove bypass role\n`>media bypass list` - List bypass roles\n`>media bypass reset` - Reset bypass roles",
                inline=False
            )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @automod_group.command(name="setup")
    @commands.has_permissions(manage_guild=True)
    async def automod_setup(self, ctx):
        """Interactive AutoMod setup wizard"""
        embed = discord.Embed(
            title="🤖 AutoMod Setup Wizard",
            description="Configure automatic moderation for your server",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @commands.hybrid_group(name="media")
    async def media_group(self, ctx):
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title=f"Media Filter — Commands for {ctx.guild.name}",
                color=0x808080
            )
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
            
            embed.add_field(
                name="📱 Media Channel Management",
                value="`>media channel add <channel>` - Add media-only channel\n`>media channel remove <channel>` - Remove media channel\n`>media channel list` - View all media channels\n`>media channel reset` - Clear all media channels",
                inline=False
            )
            
            embed.add_field(
                name="🔓 Bypass Role Management",
                value="`>media bypass add <role>` - Add bypass role\n`>media bypass remove <role>` - Remove bypass role\n`>media bypass list` - View all bypass roles\n`>media bypass reset` - Clear all bypass roles",
                inline=False
            )
            
            embed = add_dravon_footer(embed)
            await ctx.send(embed=embed)
    
    @media_group.group(name="channel")
    async def media_channel(self, ctx):
        pass
    
    @media_channel.command(name="add")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_add(self, ctx, channel: discord.TextChannel):
        """Add a media-only channel"""
        embed = discord.Embed(
            title="✅ Media Channel Added",
            description=f"{channel.mention} has been added as a media-only channel.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="remove")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_remove(self, ctx, channel: discord.TextChannel):
        """Remove a media-only channel"""
        embed = discord.Embed(
            title="✅ Media Channel Removed",
            description=f"{channel.mention} is no longer a media-only channel.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="list")
    async def media_channel_list(self, ctx):
        """List all media-only channels"""
        embed = discord.Embed(
            title="📱 Media-Only Channels",
            description="No media channels configured.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_channel.command(name="reset")
    @commands.has_permissions(manage_channels=True)
    async def media_channel_reset(self, ctx):
        """Reset all media-only channels"""
        embed = discord.Embed(
            title="✅ Media Channels Reset",
            description="All media-only channels have been cleared.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_group.group(name="bypass")
    async def media_bypass(self, ctx):
        pass
    
    @media_bypass.command(name="add")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_add(self, ctx, role: discord.Role):
        """Add a bypass role for media channels"""
        embed = discord.Embed(
            title="✅ Bypass Role Added",
            description=f"{role.mention} can now bypass media-only restrictions.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="remove")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_remove(self, ctx, role: discord.Role):
        """Remove a bypass role for media channels"""
        embed = discord.Embed(
            title="✅ Bypass Role Removed",
            description=f"{role.mention} can no longer bypass media-only restrictions.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="list")
    async def media_bypass_list(self, ctx):
        """List all bypass roles"""
        embed = discord.Embed(
            title="🔓 Media Bypass Roles",
            description="No bypass roles configured.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)
    
    @media_bypass.command(name="reset")
    @commands.has_permissions(manage_roles=True)
    async def media_bypass_reset(self, ctx):
        """Reset all bypass roles"""
        embed = discord.Embed(
            title="✅ Bypass Roles Reset",
            description="All bypass roles have been cleared.",
            color=0x808080
        )
        embed = add_dravon_footer(embed)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AutoModConfig(bot))