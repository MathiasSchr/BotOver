# Dépendances
import discord
from discord.ext import tasks, commands

import os
from dotenv import load_dotenv

import pymongo
from pymongo.mongo_client import MongoClient

from datetime import datetime

# Variables d'environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')  # Récupère le token du bot Discord depuis le fichier .env
uri = os.getenv('URI')  # URI de connexion à la base de données MongoDB

# Configuration des intents du bot
intents = discord.Intents.default()
intents.message_content = True  # Active l'intent pour accéder au contenu des messages

bot = commands.Bot(command_prefix='!', intents=intents)  # Initialise le bot avec le préfixe '!' et les intents

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()  # Initialise la connexion à la base de données
        self.findChannel()  # Localise le canal Discord pour les messages
        self.check_birthday.start()  # Démarre la tâche planifiée pour vérifier les anniversaires

    def loadDB(self):
        # Initialise la connexion à MongoDB
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            client.admin.command('ping')  # Vérifie la connexion à MongoDB
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.database = client["AppDB"]  # Sélectionne la base de données "AppDB"
            self.collection = self.database["MemberDB"]  # Sélectionne la collection "MemberDB"
        except Exception as e:
            print(e)  # Affiche les erreurs de connexion

    def findChannel(self):
        # Trouve le canal Discord où envoyer les messages d'anniversaire
        self.channel = bot.get_channel(1332489269859844156)  # Remplace l'ID par celui de votre canal
        if self.channel:
            print("Channel trouvé.")

    def cog_unload(self):
        # Annule la tâche planifiée lorsque le cog est déchargé
        self.check_birthday.cancel()

    @tasks.loop(hours=24.0)
    async def check_birthday(self):
        # Vérifie les anniversaires tous les jours
        today = datetime.now().strftime("%d/%m")  # Format de la date du jour
        print(today)
        if self.collection.count_documents({"birthday": today}) > 0:  # Recherche des documents correspondant à la date
            birthdays = self.collection.find({"birthday": today})
            for keys in birthdays:
                await self.channel.send(f"Joyeux anniversaire {keys['name']} ! 🎉")  # Envoie un message pour chaque anniversaire
        else:
            print("Aucun anniversaire trouvé aujourd'hui.")

    @commands.command()
    async def birthday(self, ctx, birth: str):
        # Commande pour enregistrer l'anniversaire d'un utilisateur
        try:
            birth = datetime.strptime(birth, "%d/%m/%Y")  # Convertit la chaîne de date en objet datetime
            date = datetime.strftime(birth, "%d/%m")  # Extrait le jour et le mois
            print(date)
            age = int(datetime.now().strftime("%Y")) - int(datetime.strftime(birth,"%Y"))  # Calcule l'âge
            print(age)
            print(ctx.author.name)
            existing_user = self.collection.find_one({"name": ctx.author.name})  # Vérifie si l'utilisateur existe déjà
            if existing_user:
                self.collection.update_one(
                    {"name": ctx.author.name},
                    {"$set": {"birth": birth,"birthday": date, "age": age}}  # Met à jour les informations existantes
                )
            else:
                self.collection.insert_one({
                    "name": ctx.author.name,  # Ajoute un nouvel utilisateur avec ses informations
                    "birth": birth,
                    "birthday": date,
                    "age": age,
                })
            await ctx.send(f"Merci {ctx.author.mention}, ton anniversaire a bien été enregistré à la date du {date} !")
        except ValueError:
            # Gestion des erreurs de format de date
            await ctx.send("Format de date incorrect. Veuillez entrer une date au format 'dd/mm/yyyy'.")


@bot.event
async def on_ready():
    # Événement déclenché lorsque le bot est prêt
    print(f'Connecté en tant que {bot.user.name}')
    await bot.add_cog(Birthday(bot))  # Ajoute le cog Birthday au bot

bot.run(TOKEN)  # Lance le bot avec le token
