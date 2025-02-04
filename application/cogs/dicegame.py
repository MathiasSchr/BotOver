# dicegame.py

# importation du fichier config.py

# dépendances
import random

import discord
from discord.ext import commands
from discord.ui import View, Button


# cog
class DiceGameView(View):
    """Vue interactive contenant les boutons pour lancer les dés"""

    def __init__(self, user_id):
        super().__init__(timeout=60)  # Le message interactif dure 60s
        self.user_id = user_id  # Stocke l'ID du joueur qui a initié le jeu
        print(f"{self.qualified_name} chargé !")

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user.id == self.user_id

    async def roll_dice(self, interaction: discord.Interaction, sides: int):
        result = random.randint(1, sides)  # Lancer du dé
        await interaction.response.send_message(
            f"🎲 **{interaction.user.name}** a lancé un **D{sides}** et a obtenu **{result}**!", ephemeral=False
        )

    @discord.ui.button(label="🎲 D6", style=discord.ButtonStyle.primary)
    async def d6(self, interaction: discord.Interaction, button: Button):
        await self.roll_dice(interaction, 6)

    @discord.ui.button(label="🎲 D10", style=discord.ButtonStyle.primary)
    async def d10(self, interaction: discord.Interaction, button: Button):
        await self.roll_dice(interaction, 10)

    @discord.ui.button(label="🎲 D20", style=discord.ButtonStyle.primary)
    async def d20(self, interaction: discord.Interaction, button: Button):
        await self.roll_dice(interaction, 20)

    @discord.ui.button(label="🎲 D50", style=discord.ButtonStyle.primary)
    async def d50(self, interaction: discord.Interaction, button: Button):
        await self.roll_dice(interaction, 50)

    @discord.ui.button(label="🎲 D100", style=discord.ButtonStyle.primary)
    async def d100(self, interaction: discord.Interaction, button: Button):
        await self.roll_dice(interaction, 100)


class DiceGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dice(self, ctx):
        """Affiche le message interactif pour lancer un dé"""
        embed = discord.Embed(
            title="🎲 Lancer de dés",
            description="Clique sur un bouton pour lancer un dé !",
            color=discord.Color.blue()
        )
        view = DiceGameView(user_id=ctx.author.id)  # Création de la vue interactive
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    
    await bot.add_cog(DiceGame(bot))