# birthday.py

# importation du fichier config.py
import config

# dépendances
from discord.ext import tasks, commands
import pymongo

from pymongo.mongo_client import MongoClient

from datetime import datetime, time, timezone, timedelta

# variables de temps
frzone = timezone(timedelta(hours=1))
birthdaycheck = time(hour=9, tzinfo=frzone)

# cog
class Birthday(commands.Cog):

    # initialisation du cog
    def __init__(self, bot):

        self.bot = bot
        self.loadDB()
        self.findChannelAnniv()
        self.check_birthday.start()
        print(f"{self.qualified_name} chargé !")

    # connexion à la database
    def loadDB(self):

        self.client = MongoClient(config.uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try: # ping la database pour vérifier la connexion
            self.client.admin.command('ping')
            print(f"{self.qualified_name} : Connecté à MongoDB!")
            self.database = self.client["AppDB"]
            self.collection = self.database["MemberDB"]
        except Exception as e:
            print(f"{self.qualified_name} : Erreur de connexion MongoDB : {e}")

    # vérification de l'existence du channel anniversaire
    def findChannelAnniv(self):
        
        #self.channel = self.bot.get_channel(1297192718409400341)
        self.channel = self.bot.get_channel(1332489269859844156)
        if self.channel:
            print(f"{self.qualified_name} : Channel anniversaire trouvé.")

    def cog_unload(self):
        
        self.client.close()
        self.check_birthday.cancel()

    async def cog_before_invoke(self, ctx): # s'exécute avant chaque commande du cog
        
        print(f"{self.qualified_name} : Commande {ctx.command} exécutée par {ctx.author}")

    # tâche : souhaite l'anniversaire s'il y en a un à 9h
    @tasks.loop(time=birthdaycheck) #
    async def check_birthday(self):
        
        today = datetime.now().strftime("%d/%m")
        if self.collection.count_documents({"birthday": today}) > 0:
            birthdays = self.collection.find({"birthday": today})
            for keys in birthdays:
                await self.channel.send(f"Joyeux anniversaire {keys['name']} ! 🎉")
        else:
            print(f"{self.qualified_name} : Aucun anniversaire trouvé aujourd'hui.")

    # commande !birthday : ajoute un anniversaire
    @commands.command()
    async def birthday(self, ctx, birth: str):
        
        try:
            birth = datetime.strptime(birth, "%d/%m/%Y")
            birth_date = birth.date()
            if birth > datetime.now():
                await ctx.send(f"{ctx.author.mention}, tu ne peux pas être né dans le futur !")
            elif birth < datetime(1920, 1, 1,0,0,0):
                await ctx.send(f"{ctx.author.mention}, tu n'es pas Denver le dinosaure !")
            else:
                datestr = datetime.strftime(birth, "%d/%m")
                age = int(datetime.now().strftime("%Y")) - int(datetime.strftime(birth,"%Y"))
                if birth_date.month > birth_date.today().month or (birth_date.month == birth_date.today().month and birth_date.day > birth_date.today().day) :
                    age -= 1
                if self.collection.count_documents({"name": ctx.author.name})> 0 :
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
            await ctx.send(f"Format de date incorrect {ctx.author.mention}. Veuillez entrer une date au format 'dd/mm/yyyy'.")

async def setup(bot):
    
    await bot.add_cog(Birthday(bot))
