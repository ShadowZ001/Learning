import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Synced {len(synced)} command(s)')
    except Exception as e:
        print(f'Failed to sync commands: {e}')

@bot.event
async def on_guild_join(guild):
    embed = discord.Embed(
        title="BloodyMc Arrived!",
        description="Thanks for adding me to your server! Use `/help` to see all available commands.",
        color=0x0099ff
    )
    embed.set_thumbnail(url=bot.user.avatar.url)
    
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(embed=embed)
            break

@bot.command(name='hello')
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}! I am BloodyMc!')

@bot.tree.command(name='hello', description='Say hello to BloodyMc')
async def hello_slash(interaction: discord.Interaction):
    await interaction.response.send_message(f'Hello {interaction.user.mention}! I am BloodyMc!')

@bot.tree.command(name='help', description='Show all available commands')
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="BloodyMc Commands",
        description="Here are all available commands:",
        color=0x0099ff
    )
    embed.add_field(name="/hello", value="Say hello to BloodyMc", inline=False)
    embed.add_field(name="!hello", value="Say hello to BloodyMc (prefix version)", inline=False)
    embed.add_field(name="/help", value="Show this help message", inline=False)
    
    await interaction.response.send_message(embed=embed)

if __name__ == '__main__':
    bot.run(os.getenv('DISCORD_TOKEN'))