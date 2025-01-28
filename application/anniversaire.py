import discord
from discord.ext import tasks, commands

import os
from dotenv import load_dotenv

import pymongo
from pymongo.mongo_client import MongoClient

from datetime import datetime

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
uri = os.getenv('URI')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

class Birthday(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loadDB()
        self.findChannel()
        self.check_birthday.start()

    def loadDB(self):
        client = MongoClient(uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        # Send a ping to confirm a successful connection
        try:
            client.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
            self.database = client["AppDB"]
            self.collection = self.database["MemberDB"]
        except Exception as e:
            print(e)

    def findChannel(self):
        self.channel = bot.get_channel(1332489269859844156)
        if self.channel:
            print("Channel trouvé.")

    def cog_unload(self):
        self.check_birthday.cancel()

    @tasks.loop(hours=24.0)
    async def check_birthday(self):
        today = datetime.now().strftime("%d/%m")
        print(today)
        if self.collection.count_documents({"birthday": today}) > 0:
            birthdays = self.collection.find({"birthday": today})
            for keys in birthdays:
                await self.channel.send(f"Joyeux anniversaire {keys['name']} ! 🎉")
        else:
            print("Aucun anniversaire trouvé aujourd'hui.")

    @commands.command()
    async def birthday(self, ctx, birth: str):
        try:
            birth = datetime.strptime(birth, "%d/%m/%Y")
            date = datetime.strftime(birth, "%d/%m")
            print(date)
            age = int(datetime.now().strftime("%Y")) - int(datetime.strftime(birth,"%Y"))
            print(age)
            print(ctx.author.name)
            existing_user = self.collection.find_one({"name": ctx.author.name})
            if existing_user:
                self.collection.update_one(
                    {"name": ctx.author.name},
                    {"$set": {"birth": birth,"birthday": date, "age": age}}
                )
            else:
                self.collection.insert_one({
                    "name": ctx.author.name,
                    "birth": birth,
                    "birthday": date,
                    "age": age,
                })
            await ctx.send(f"Merci {ctx.author.mention}, ton anniversaire a bien été enregistré à la date du {date} !")
        except ValueError:
            await ctx.send("Format de date incorrect. Veuillez entrer une date au format 'dd/mm/yyyy'.")


@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user.name}')
    await bot.add_cog(Birthday(bot))

bot.run(TOKEN)