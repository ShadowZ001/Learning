import discord
from discord.ext import commands

class RPSView(discord.ui.View):
    def __init__(self, challenger, opponent):
        super().__init__(timeout=60)
        self.challenger = challenger
        self.opponent = opponent
        self.challenger_choice = None
        self.opponent_choice = None
        self.choices = {"🪨": "Rock", "📄": "Paper", "✂️": "Scissors"}
    
    def get_winner(self, choice1, choice2):
        if choice1 == choice2:
            return "tie"
        elif (choice1 == "🪨" and choice2 == "✂️") or \
             (choice1 == "📄" and choice2 == "🪨") or \
             (choice1 == "✂️" and choice2 == "📄"):
            return "challenger"
        else:
            return "opponent"
    
    @discord.ui.button(emoji="🪨", style=discord.ButtonStyle.secondary)
    async def rock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "🪨")
    
    @discord.ui.button(emoji="📄", style=discord.ButtonStyle.secondary)
    async def paper_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "📄")
    
    @discord.ui.button(emoji="✂️", style=discord.ButtonStyle.secondary)
    async def scissors_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_choice(interaction, "✂️")
    
    async def handle_choice(self, interaction: discord.Interaction, choice):
        if interaction.user.id == self.challenger.id:
            if self.challenger_choice is None:
                self.challenger_choice = choice
                embed = discord.Embed(
                    title="Rock Paper Scissors",
                    description=f"{self.challenger.mention} has chosen! {self.opponent.mention} waiting for you to choose",
                    color=0x7289da
                )
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("You already made your choice!", ephemeral=True)
        
        elif interaction.user.id == self.opponent.id:
            if self.opponent_choice is None:
                self.opponent_choice = choice
                
                # Determine winner
                winner = self.get_winner(self.challenger_choice, self.opponent_choice)
                
                if winner == "tie":
                    result = f"It's a tie! Both chose {self.choices[choice]}"
                elif winner == "challenger":
                    result = f"{self.challenger.mention} wins gg! {self.opponent.mention} loose!!"
                else:
                    result = f"{self.opponent.mention} wins gg! {self.challenger.mention} loose!!"
                
                embed = discord.Embed(
                    title="Rock Paper Scissors - Results",
                    description=f"{self.challenger.mention}: {self.choices[self.challenger_choice]}\n{self.opponent.mention}: {self.choices[self.opponent_choice]}\n\n{result}",
                    color=0x00ff00
                )
                
                # Disable all buttons
                for item in self.children:
                    item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message("You already made your choice!", ephemeral=True)
        
        else:
            await interaction.response.send_message("This game is not for you!", ephemeral=True)

class RPS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="rps")
    async def rps_command(self, ctx, user: discord.Member):
        """Play Rock Paper Scissors with another user"""
        if user.bot:
            await ctx.send("❌ You cannot play with bots!")
            return
        
        if user.id == ctx.author.id:
            await ctx.send("❌ You cannot play with yourself!")
            return
        
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description="Select a button to play!",
            color=0x7289da
        )
        
        view = RPSView(ctx.author, user)
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(RPS(bot))