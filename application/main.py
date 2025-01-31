# Dépendances
import discord
from discord.ext import tasks, commands

import os
from dotenv import load_dotenv

import pymongo
from pymongo.mongo_client import MongoClient

from datetime import datetime, timezone, time, timedelta

# Récupération des variables d'environnement
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
uri = os.getenv('URI')

# Intentions
intents = discord.Intents.default()
intents.message_content = True

# Préfixe
bot = commands.Bot(command_prefix='!', intents=intents)

# Variable de temps
frzone = timezone(timedelta(hours=1))
time = time(hour=9, tzinfo=frzone)

# Classe du cog
class Birthday(commands.Cog):

    def __init__(self, bot): # Initialisation du cog
        self.bot = bot
        self.loadDB()
        self.findChannelAnniv()
        self.check_birthday.start()

    async def cog_before_invoke(self, ctx): # S'exécute avant chaque commande du cog
        print(f"Commande {ctx.command} exécutée par {ctx.author}")

    def loadDB(self): # Initialisation de la database
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try: # Ping la database pour vérifier la connexion
            client.admin.command('ping')
            print("Connexion avec la database établie !")
            self.database = client["AppDB"]
            self.collection = self.database["MemberDB"]
        except Exception as e:
            print(e)

    def findChannelAnniv(self): # Vérification de l'existence du channel anniversaire
        self.channel = bot.get_channel(1297192718409400341)
        if self.channel:
            print("Channel anniversaire trouvé.")

    def cog_unload(self):
        self.check_birthday.cancel()

    @tasks.loop(time=time) # Tâche : vérification des anniversaires à 9h
    async def check_birthday(self):
        today = datetime.now().strftime("%d/%m")
        if self.collection.count_documents({"birthday": today}) > 0:
            birthdays = self.collection.find({"birthday": today})
            for keys in birthdays:
                await self.channel.send(f"Joyeux anniversaire {keys['name']} ! 🎉")
        else:
            print("Aucun anniversaire trouvé aujourd'hui.")

    @commands.command() # Commande : ajout des anniversaires
    async def birthday(self, ctx, birth: str):
        try:
            birth = datetime.strptime(birth, "%d/%m/%Y")
            date = birth.date()
            datestr = datetime.strftime(birth, "%d/%m")
            age = int(datetime.now().strftime("%Y")) - int(datetime.strftime(birth,"%Y"))
            print(age)
            if date.month > date.today().month or (date.month == date.today().month and date.day > date.today().day) :
                age -= 1
                print(age)
            existing_user = self.collection.find_one({"name": ctx.author.name})
            if existing_user:
                self.collection.update_one(
                    {"name": ctx.author.name},
                    {"$set": {"birth": birth,"birthday": datestr, "age": age}}
                )
            else:
                self.collection.insert_one({
                    "name": ctx.author.name,
                    "birth": birth,
                    "birthday": datestr,
                    "age": age,
                })
            await ctx.send(f"Merci {ctx.author.mention}, ton anniversaire a bien été enregistré à la date du {datestr} !")
        except ValueError:
            await ctx.send("Format de date incorrect. Veuillez entrer une date au format 'dd/mm/yyyy'.")

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()

    def loadDB(self):
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            client.admin.command('ping')
            print("Connecté à MongoDB!")
            self.database = client["AppDB"]
            self.collection = self.database["MessagesDocument"]  # Collection des stats de messages
        except Exception as e:
            print(f"Erreur de connexion MongoDB : {e}")

    @commands.command()
    async def stats(self, ctx):
        """Affiche les 5 membres ayant envoyé le plus de messages."""
        try:
            top_users = list(self.collection.find({}, {"user_id": 1, "username": 1, "message_count": 1})
                             .sort("message_count", -1)
                             .limit(5))

            if not top_users:
                await ctx.send("Aucune donnée de messages trouvée.")
                return

            embed = discord.Embed(title="🏆 Classement des messages", color=discord.Color.blue())

            for i, user in enumerate(top_users, start=1):
                embed.add_field(
                    name=f"{i}. {user['username']}",
                    value=f"📩 {user['message_count']} messages",
                    inline=False
                )

            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send("Une erreur s'est produite lors de la récupération des statistiques.")
            print(f"Erreur MongoDB : {e}")


@bot.event
async def on_message(message):
    """Incrémente le compteur de messages pour chaque utilisateur."""
    if message.author.bot: # Ignore les messages des bots
        return

    client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
    database = client["AppDB"]
    collection = database["MessagesDocument"]

    user_id = str(message.author.id)
    username = message.author.name
    print(f'Message : {message.content} send by {username}')

    # Mise à jour du compteur de messages de l'utilisateur
    collection.update_one(
        {"user_id": user_id},
        {"$set": {"username": username}, "$inc": {"message_count": 1}},
        upsert=True  # Crée un l'utilisateur s'il est pas là
    )

    await bot.process_commands(message)



@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')
    await bot.add_cog(Birthday(bot)) # On charge le cog Birthday
    await bot.add_cog(Stats(bot))
    print("Cogs chargés :", bot.cogs.keys())  # Affiche les cogs chargés


bot.run(TOKEN) # On execute le bot