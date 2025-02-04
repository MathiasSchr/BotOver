# experience.py

# dépendances
import random

# importation du fichier config.py
import config
import discord
import pymongo
from discord.ext import commands
from pymongo.mongo_client import MongoClient


# cog
class Experience(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()
        print(f"{self.qualified_name} chargé !")

    def loadDB(self):
        self.client = MongoClient(config.uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            self.client.admin.command('ping')
            print(f"{self.qualified_name} : Connecté à MongoDB!")
            self.database = self.client["AppDB"]
            self.collection = self.database["ExperienceDocument"]  # collection de l'expérience
        except Exception as e:
            print(f"{self.qualified_name} : Erreur de connexion MongoDB : {e}")

    def cog_unload(self):
        self.client.close()

    async def cog_before_invoke(self, ctx): # s'exécute avant chaque commande du cog
        print(f"{self.qualified_name} : Commande {ctx.command} exécutée par {ctx.author}")

    def calculate_level(self, xp):
        """Calcule le niveau en fonction de l'XP selon la formule donnée."""
        level = 1
        required_xp = 30  # xp pour le lvl 1

        while xp >= required_xp:
            level += 1
            required_xp = required_xp + required_xp * 1.05  # taux d'augmentation à 1.16 pour commencer (maybe to high)

        return level, required_xp

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ajoute de l'XP lorsqu'un message est envoyé."""
        if message.author.bot:
            return

        if "!" in message.content: # ignore les messages des bots
            return

        user_id = str(message.author.id)
        username = message.author.name
        xp_gained = random.randint(1, 5)  # gain d'XP entre 1 et 5
        print(f"{self.qualified_name} : {username} gained : {xp_gained} xp")

        user_data = self.collection.find_one({"user_id": user_id})

        if self.collection.count_documents({"user_id": user_id})> 0 :
            new_xp = user_data["xp"]+ xp_gained
        else:
            new_xp = xp_gained  # si c'est son premier message

        new_level, next_level_xp = self.calculate_level(new_xp)

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "xp": new_xp, "level": new_level}},
            upsert=True
        )

        # check du levelup
        if user_data and (new_level > user_data["level"]) :
            await message.channel.send(f"🎉 {username} est maintenant **niveau {new_level}** ! 🎉")

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Affiche le niveau et l'XP d'un utilisateur."""
        member = member or ctx.author  # si aucun utilisateur n'est mentionné, on prend celui qui tape la commande
        user_id = str(member.id)
        user_data = self.collection.find_one({"user_id": user_id})

        if not user_data:
            await ctx.send(f"{member.mention} n'a pas encore gagné d'XP.")
            return

        level = user_data["level"]
        xp = user_data["xp"]
        _, next_xp = self.calculate_level(xp)

        embed = discord.Embed(title=f"🏅 Niveau de {member.name}", color=discord.Color.gold())
        embed.add_field(name="Niveau", value=f"{level}", inline=True)
        embed.add_field(name="XP", value=f"{xp}/{int(next_xp)}", inline=True)

        await ctx.send(embed=embed)

async def setup(bot):
    
    await bot.add_cog(Experience(bot))