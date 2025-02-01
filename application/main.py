# Dépendances
import random

import discord
from discord.ext import tasks, commands
from discord.ui import View, Button

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
    async def stats(self, ctx, limit: int = 5):
        """Affiche les membres ayant envoyé le plus de messages, avec une limite définie par l'utilisateur."""
        try:
            if limit <= 0:
                await ctx.send("La limite doit être un nombre positif.")
                return

            top_users = list(self.collection.find({}, {"user_id": 1, "username": 1, "message_count": 1})
                             .sort("message_count", -1)
                             .limit(limit))

            if not top_users:
                await ctx.send("Aucune donnée de messages trouvée.")
                return

            embed = discord.Embed(title=f"🏆 Classement des {limit} meilleurs posteurs", color=discord.Color.blue())

            for i, user in enumerate(top_users, start=1):
                embed.add_field(
                    name=f"{i}. {user['username']}",
                    value=f"📩 {user['message_count']} messages",
                    inline=False
                )

            await ctx.send(embed=embed)
        except ValueError:
            await ctx.send("Veuillez entrer un nombre valide pour la limite.")
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

class Experience(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()

    def loadDB(self):
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            client.admin.command('ping')
            print("Connecté à MongoDB!")
            self.database = client["AppDB"]
            self.collection = self.database["ExperienceDocument"]  # Collection de l'expérience
        except Exception as e:
            print(f"Erreur de connexion MongoDB : {e}")

    def calculate_level(self, xp):
        """Calcule le niveau en fonction de l'XP selon la formule donnée."""
        level = 1
        required_xp = 30  # Xp pour le lvl 1

        while xp >= required_xp:
            level += 1
            required_xp = required_xp + required_xp * 1.05  # Taux d'augmentation à 1.16 pour commencer (maybe to high)

        return level, required_xp

    @commands.Cog.listener()
    async def on_message(self, message):
        """Ajoute de l'XP lorsqu'un message est envoyé."""
        if message.author.bot:
            return

        user_id = str(message.author.id)
        username = message.author.name
        xp_gained = random.randint(1, 5)  # Gain d'XP entre 1 et 5
        print(f"{username} gained : {xp_gained} xp")

        user_data = self.collection.find_one({"user_id": user_id})

        if user_data:
            new_xp = user_data["xp"] + xp_gained
        else:
            new_xp = xp_gained  # Si c'est son premier message

        new_level, next_level_xp = self.calculate_level(new_xp)

        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username, "xp": new_xp, "level": new_level}},
            upsert=True
        )

        # Check du levelup
        if user_data and (new_level > user_data["level"]) :
            await message.channel.send(f"🎉 {username} est maintenant **niveau {new_level}** ! 🎉")

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        """Affiche le niveau et l'XP d'un utilisateur."""
        member = member or ctx.author  # Si aucun utilisateur n'est mentionné, on prend celui qui tape la commande
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

class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()# Collection MongoDB
        self.user_voice_times = {}  # Dictionnaire temporaire pour suivre les entrées en vocal

    def loadDB(self):
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            client.admin.command('ping')
            print("Connecté à MongoDB!")
            self.database = client["AppDB"]
            self.collection = self.database["ExperienceDocument"]  # Collection de l'expérience
        except Exception as e:
            print(f"Erreur de connexion MongoDB : {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Détecte quand un utilisateur rejoint ou quitte un salon vocal"""
        user_id = str(member.id)

        # Si l'utilisateur rejoint un canal vocal
        if before.channel is None and after.channel is not None:
            self.user_voice_times[user_id] = datetime.utcnow()  # Enregistre l'heure d'entrée
            print(f"{member.name} a rejoint {after.channel.name} à {self.user_voice_times[user_id]}")

        # Si l'utilisateur quitte un canal vocal
        elif before.channel is not None and after.channel is None:
            if user_id in self.user_voice_times:
                join_time = self.user_voice_times.pop(user_id)
                duration = (datetime.utcnow() - join_time).total_seconds()  # Temps passé en secondes

                # Mise à jour du temps total en vocal
                user_data = self.collection.find_one({"user_id": user_id})

                if user_data:
                    total_time = user_data["total_time"] + duration
                else:
                    total_time = duration  # Premier enregistrement

                self.collection.update_one(
                    {"user_id": user_id},
                    {"$set": {"username": member.name, "total_time": total_time}},
                    upsert=True
                )

                print(f"{member.name} a quitté {before.channel.name} après {duration:.2f} secondes")

    @commands.command()
    async def voicetime(self, ctx, member: discord.Member = None):
        """Affiche le temps total passé en vocal"""
        member = member or ctx.author
        user_id = str(member.id)
        user_data = self.collection.find_one({"user_id": user_id})

        if not user_data:
            await ctx.send(f"{member.mention} n'a pas encore été en vocal.")
            return

        total_seconds = int(user_data["total_time"])
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        embed = discord.Embed(title=f"🎙 Temps vocal de {member.name}", color=discord.Color.green())
        embed.add_field(name="Total", value=f"{hours}h {minutes}m {seconds}s", inline=False)

        await ctx.send(embed=embed)


class DiceGameView(View):
    """Vue interactive contenant les boutons pour lancer les dés"""

    def __init__(self, user_id):
        super().__init__(timeout=60)  # Le message interactif dure 60s
        self.user_id = user_id  # Stocke l'ID du joueur qui a initié le jeu

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



@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')
    await bot.add_cog(Birthday(bot)) # On charge le cog Birthday
    await bot.add_cog(Stats(bot))
    await bot.add_cog(Experience(bot))
    await bot.add_cog(VoiceTracker(bot))
    await bot.add_cog(DiceGame(bot))
    print("Cogs chargés :", bot.cogs.keys())  # Affiche les cogs chargés


bot.run(TOKEN) # On execute le bot
