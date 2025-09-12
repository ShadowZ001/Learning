import discord
from discord.ext import commands
import json
import os

class BotAdmin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_admins = [1037768611126841405]  # Initial bot admin
        self.blacklisted_users = set()
        self.premium_logs_channel = None
        self.load_data()
    
    def load_data(self):
        try:
            if os.path.exists('data/botadmin.json'):
                with open('data/botadmin.json', 'r') as f:
                    data = json.load(f)
                    self.bot_admins = data.get('bot_admins', [1037768611126841405])
                    self.blacklisted_users = set(data.get('blacklisted_users', []))
                    self.premium_logs_channel = data.get('premium_logs_channel')
        except:
            pass
    
    def save_data(self):
        os.makedirs('data', exist_ok=True)
        with open('data/botadmin.json', 'w') as f:
            json.dump({
                'bot_admins': self.bot_admins,
                'blacklisted_users': list(self.blacklisted_users),
                'premium_logs_channel': self.premium_logs_channel
            }, f)
    
    def is_bot_admin(self, user_id):
        return user_id in self.bot_admins
    
    async def cog_check(self, ctx):
        """Only allow bot admins to use these commands"""
        return self.is_bot_admin(ctx.author.id)
    
    @commands.command(name='global', hidden=True)
    async def global_announce(self, ctx, *, message=None):
        
        if not message:
            await ctx.send("Please provide a message to announce globally.")
            return
        
        embed = discord.Embed(
            title="📢 Global Announcement",
            description=message,
            color=0xff6b35
        )
        embed.set_footer(text="Dravon Bot Team")
        
        sent = 0
        for guild in self.bot.guilds:
            try:
                channel = guild.system_channel or guild.text_channels[0]
                await channel.send(embed=embed)
                sent += 1
            except:
                continue
        
        await ctx.send(f"Global announcement sent to {sent} servers.")
    
    @commands.group(name='announce', hidden=True, invoke_without_command=True)
    async def announce(self, ctx):
        await ctx.send("Use: `announce title <title>`, `announce description <desc>`, `announce color <hex>`, `announce image <url>`, `announce send`")
    
    @announce.command(name='title')
    async def announce_title(self, ctx, *, title):
        if not hasattr(self, 'announce_data'):
            self.announce_data = {}
        self.announce_data['title'] = title
        await ctx.send(f"Title set: {title}")
    
    @announce.command(name='description')
    async def announce_description(self, ctx, *, description):
        if not hasattr(self, 'announce_data'):
            self.announce_data = {}
        self.announce_data['description'] = description
        await ctx.send(f"Description set: {description[:50]}...")
    
    @announce.command(name='color')
    async def announce_color(self, ctx, color):
        if not hasattr(self, 'announce_data'):
            self.announce_data = {}
        try:
            color_int = int(color.replace('#', ''), 16)
            self.announce_data['color'] = color_int
            await ctx.send(f"Color set: {color}")
        except:
            await ctx.send("Invalid color format. Use hex format like #ff6b35")
    
    @announce.command(name='image')
    async def announce_image(self, ctx, url):
        if not hasattr(self, 'announce_data'):
            self.announce_data = {}
        self.announce_data['image'] = url
        await ctx.send(f"Image set: {url}")
    
    @announce.command(name='send')
    async def announce_send(self, ctx):
        if not hasattr(self, 'announce_data'):
            await ctx.send("No announcement data set.")
            return
        
        embed = discord.Embed(
            title=self.announce_data.get('title', 'Announcement'),
            description=self.announce_data.get('description', ''),
            color=self.announce_data.get('color', 0xff6b35)
        )
        
        if 'image' in self.announce_data:
            embed.set_image(url=self.announce_data['image'])
        
        embed.set_footer(text="Dravon Bot Team")
        
        sent = 0
        for guild in self.bot.guilds:
            try:
                channel = guild.system_channel or guild.text_channels[0]
                await channel.send(embed=embed)
                sent += 1
            except:
                continue
        
        await ctx.send(f"Custom announcement sent to {sent} servers.")
        self.announce_data = {}
    
    @commands.group(name='premiumlogs', hidden=True, invoke_without_command=True)
    async def premiumlogs_group(self, ctx):
        await ctx.send("Use: `premiumlogs set <channel>`")
    
    @premiumlogs_group.command(name='set')
    async def set_premium_logs_channel(self, ctx, channel: discord.TextChannel):
        self.premium_logs_channel = channel.id
        self.save_data()
        await ctx.send(f"Premium logs channel set to {channel.mention}")
    
    @commands.group(name='blacklist', hidden=True, invoke_without_command=True)
    async def blacklist(self, ctx):
        await ctx.send("Use: `blacklist user <user_id>`")
    
    @blacklist.command(name='user')
    async def blacklist_user(self, ctx, user_id: int):
        self.blacklisted_users.add(user_id)
        self.save_data()
        await ctx.send(f"User {user_id} has been blacklisted.")
    
    @commands.group(name='botadmin', hidden=True, invoke_without_command=True)
    async def botadmin_group(self, ctx):
        await ctx.send("Use: `botadmin add <user_id>`")
    
    @botadmin_group.command(name='add')
    async def add_bot_admin(self, ctx, user_id: int):
        if user_id not in self.bot_admins:
            self.bot_admins.append(user_id)
            self.save_data()
            await ctx.send(f"User {user_id} has been added as bot admin.")
        else:
            await ctx.send("User is already a bot admin.")
    
    @botadmin_group.command(name='list')
    async def list_bot_admins(self, ctx):
        embed = discord.Embed(
            title="🔐 Bot Admins",
            color=0x58a6ff
        )
        admin_list = "\n".join([f"<@{admin_id}> ({admin_id})" for admin_id in self.bot_admins])
        embed.add_field(name="Current Bot Admins:", value=admin_list or "None", inline=False)
        embed.set_footer(text=f"Total: {len(self.bot_admins)} admins")
        await ctx.send(embed=embed)
    
    def is_blacklisted(self, user_id):
        return user_id in self.blacklisted_users

async def setup(bot):
    await bot.add_cog(BotAdmin(bot))
    print("BotAdmin cog loaded successfully")