# main.py

# importation du fichier config.py
import config

# dépendances
import random

import discord
from discord.ext import tasks, commands
from discord.ui import View, Button

import pymongo
from pymongo.mongo_client import MongoClient

from datetime import datetime

# intentions
intents = discord.Intents.default()
intents.message_content = True

# préfixe
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():

    print(f'Connecté en tant que {bot.user.name}')
    await bot.load_extension("cogs.birthday")
    await bot.load_extension("cogs.stats")
    await bot.load_extension("cogs.experience")
    await bot.load_extension("cogs.dicegame")
    print("Cogs chargés :", bot.cogs.keys())  # Affiche les cogs chargés

bot.run(config.TOKEN) # On execute le bot
