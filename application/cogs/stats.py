# stat.py

# importation du fichier config.py
import config

# dépendances
import discord
from discord.ext import tasks, commands
import pymongo

from pymongo.mongo_client import MongoClient

from datetime import datetime, time, timezone, timedelta

# cog stat message
class Stats(commands.Cog):

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
            self.collection = self.database["MessagesDocument"]  # collection des stats de messages
        except Exception as e:
            print(f"{self.qualified_name} : Erreur de connexion MongoDB : {e}")
        
    def cog_unload(self):
        self.client.close()

    async def cog_before_invoke(self, ctx): # S'exécute avant chaque commande du cog
        print(f"{self.qualified_name} : Commande {ctx.command} exécutée par {ctx.author}")

    @commands.Cog.listener()
    async def on_message(self, message):
        """Incrémente le compteur de messages pour chaque utilisateur."""
        if message.author.bot: # ignore les messages des bots
            return

        if "!" in message.content: # ignore les commandes
            return
    
        user_id = str(message.author.id)
        username = message.author.name
        print(f"{self.qualified_name} : Message : {message.content} send by {username}")
    
        # mise à jour du compteur de messages de l'utilisateur
        self.collection.update_one(
            {"user_id": user_id},
            {"$set": {"username": username}, "$inc": {"message_count": 1}},
            upsert=True  # crée un l'utilisateur s'il est pas là
        )
    
        await self.bot.process_commands(message)

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
            print(f"{self.qualified_name} : Erreur MongoDB : {e}")

 # cog stat vocal
class VoiceTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()# Collection MongoDB
        self.user_voice_times = {}  # Dictionnaire temporaire pour suivre les entrées en vocal
        print(f"{self.qualified_name} chargé !")

    def loadDB(self):
        client = MongoClient(config.uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            client.admin.command('ping')
            print(f"{self.qualified_name} : Connecté à MongoDB!")
            self.database = client["AppDB"]
            self.collection = self.database["VoiceActivityDocument"]  # Collection de l'expérience
        except Exception as e:
            print(f"{self.qualified_name} : Erreur de connexion MongoDB : {e}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Détecte quand un utilisateur rejoint ou quitte un salon vocal"""
        user_id = str(member.id)

        # Si l'utilisateur rejoint un canal vocal
        if before.channel is None and after.channel is not None:
            self.user_voice_times[user_id] = datetime.utcnow()  # Enregistre l'heure d'entrée
            print(f"{self.qualified_name} : {member.name} a rejoint {after.channel.name} à {self.user_voice_times[user_id]}")

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

                print(f"{self.qualified_name} : {member.name} a quitté {before.channel.name} après {duration:.2f} secondes")

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


async def setup(bot):
    
    await bot.add_cog(Stats(bot))
    await bot.add_cog(VoiceTracker(bot))