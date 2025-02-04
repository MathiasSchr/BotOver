import discord
import pymongo
from discord.ext import commands
from discord.ui import View, Button
from pymongo.mongo_client import MongoClient
import config

class GameManagement(commands.Cog):
    """Gestion de la partie du jeu"""

    def __init__(self, bot):
        self.bot = bot
        self.loadDB()
        print(f"{self.qualified_name} chargé !")  # Collection pour stocker les parties

    def loadDB(self):
        self.client = MongoClient(config.uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            self.client.admin.command('ping')
            print(f"{self.qualified_name} : Connecté à MongoDB!")
            self.database = self.client["GameDB"]
            self.collection = self.database["GameStatement"]  # collection de l'expérience
        except Exception as e:
            print(f"{self.qualified_name} : Erreur de connexion MongoDB : {e}")

    async def get_game(self):
        """Récupère la partie en cours, s'il y en a une"""
        return self.collection.find_one({"status": "active"})

    @commands.command()
    async def startgame(self, ctx):
        """Démarre une partie et assigne le rôle Maître du Jeu"""
        existing_game = await self.get_game()
        if existing_game:
            await ctx.send("⚠️ Une partie est déjà en cours ! Utilise `!stopgame` pour l'arrêter.")
            return

        # Création du document pour la partie
        game_data = {
            "game_id": ctx.guild.id,
            "status": "active",
            "players": [ctx.author.id],
            "game_master": ctx.author.id
        }
        self.collection.insert_one(game_data)

        # Vérification et création du rôle Maître du Jeu s'il n'existe pas
        role_name = "Maître du Jeu"
        game_master_role = discord.utils.get(ctx.guild.roles, name=role_name)

        if not game_master_role:
            try:
                game_master_role = await ctx.guild.create_role(name=role_name, color=discord.Color.gold(), mentionable=True)
            except discord.Forbidden:
                await ctx.send("❌ Pas la permission de créé le rôle, il faut demander à Reda.")
                return

        # Attribuer le rôle au créateur du jeu
        await ctx.author.add_roles(game_master_role)

        await ctx.send(f"✅ {ctx.author.mention} a démarré une nouvelle partie ! Tu es maintenant **{role_name}**.")

    @commands.command()
    async def stopgame(self, ctx):
        """Arrête la partie et retire le rôle Maître du Jeu"""
        existing_game = await self.get_game()

        if not existing_game:
            await ctx.send("⚠️ Il n'y a aucune partie en cours !")
            return

        # Vérifier si l'utilisateur est l'administrateur ou le Maître du Jeu
        is_admin = ctx.author.guild_permissions.administrator
        is_game_master = existing_game["game_master"] == ctx.author.id

        if not is_admin and not is_game_master:
            await ctx.send("❌ Seul un administrateur ou le Maître du Jeu peut arrêter la partie.")
            return

        self.collection.delete_one({"game_id": ctx.guild.id})

        role_name = "Maître du Jeu"
        game_master_role = discord.utils.get(ctx.guild.roles, name=role_name) # Supprime la rôle game master

        if game_master_role:
            await ctx.author.remove_roles(game_master_role)

        await ctx.send(f"🛑 {ctx.author.mention} a stoppé la partie. Le rôle **{role_name}** a été retiré.")

    @commands.command()
    async def join(self, ctx):
        """Permet de rejoindre une partie en cours"""
        existing_game = await self.get_game()

        if not existing_game:
            await ctx.send("⚠️ Il n'y a aucune partie en cours ! Utilise `!startgame` pour en démarrer une.")
            return

        user_id = str(ctx.author.id)
        username = ctx.author.name

        if user_id in existing_game["players"]:
            await ctx.send(f"⚠️ {username}, tu es déjà dans la partie !")
            return

        # Ajouter le joueur à la liste des joueurs de la partie
        self.collection.update_one(
            {"game_id": existing_game["game_id"]},
            {"$push": {"players": user_id}}
        )

        # Envoyer le message interactif pour choisir la classe
        embed = discord.Embed(
            title="⚔️ Choisis ta classe !",
            description="Clique sur un bouton pour sélectionner ta classe de départ.",
            color=discord.Color.blue()
        )
        view = ClassSelectionView(user_id, existing_game["game_id"], self)
        await ctx.send(embed=embed, view=view)

class ClassSelectionView(View):
    """Vue interactive pour choisir une classe de joueur"""

    def __init__(self, user_id, game_id, cog):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.game_id = game_id
        self.loadDB()
        self.cog = cog  # Référence au Cog pour enregistrer la classe

    def loadDB(self):
        self.client = MongoClient(config.uri, server_api=pymongo.server_api.ServerApi(version="1", strict=True, deprecation_errors=True))
        try:
            self.client.admin.command('ping')
            self.database = self.client["GameDB"]
            self.collection = self.database["Players"]  # collection des joueurs
        except Exception as e:
            print(f"Erreur de connexion MongoDB : {e}")

    async def interaction_check(self, interaction: discord.Interaction):
        """Empêche les autres joueurs d'interagir avec le bouton"""
        return interaction.user.id == self.user_id

    async def select_class(self, interaction: discord.Interaction, player_class: str): #todo -> Fix la fonction ici car elle plante
        """Enregistre la classe choisie par le joueur"""
        user_id = str(interaction.user.id)
        username = interaction.user.name

        # Créer le profil du joueur dans la collection `Players`
        player_data = {
            "user_id": user_id,
            "username": username,
            "game_id": self.game_id,
            "class": player_class
        }
        self.collection.insert_one(player_data)

        await interaction.response.send_message(f"✅ {username}, tu es maintenant **{player_class}** !", ephemeral=False)

    @discord.ui.button(label="⚔️ Test1", style=discord.ButtonStyle.primary)
    async def warrior(self, interaction: discord.Interaction, button: Button):
        await self.select_class(interaction, "Test1")

    @discord.ui.button(label="🏹 Test2", style=discord.ButtonStyle.primary)
    async def archer(self, interaction: discord.Interaction, button: Button):
        await self.select_class(interaction, "Test2")

    @discord.ui.button(label="🧙 Test3", style=discord.ButtonStyle.primary)
    async def mage(self, interaction: discord.Interaction, button: Button):
        await self.select_class(interaction, "Test3")

async def setup(bot):
    await bot.add_cog(GameManagement(bot))
