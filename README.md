# BotOver
<p align="center"><strong>
Bienvenue sur le github du bot collaboratif du serveur OVER !
</strong>
</p>
<p align="center">
  <img src="https://files.oaiusercontent.com/file-4jQm2RpeRmvjZsEcr2Z31k?se=2025-01-28T21%3A33%3A47Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3Dcf8d81c1-9a40-49fa-84b6-95fc843001bf.webp&sig=UmM1K%2B45pS68Qn3f1/l/tgaIwJV1BRQfpqRSJu0d1PA%3D" width=500> 
</p>

## Architecture du bot

### Code

Le code de l'application est dev en **Python** et utilse la librairie discord.py. Il est disponible dans la dossier "environnement applicatif".

La doc de la librairie discord.py : https://discordpy.readthedocs.io/en/stable/

Concernant les autres dépendances du code :
- python-dotenv : pour assurer la sécurité du token du bot et la lien de la connexion de la database (pour qu'ils ne soient pas codé en clair)
- pymongo : pour établir un lien avec la database et faire des requêtes

### Hebergement

L'hébergement du bot est assuré par la platforme **Sparked Host**. Grâce à son panel de contrôle, on peut facilement modifier les paramètres du bot et faire pleins de choses. Voici le lien pour y accéder, il faut juste avant que je vous ai invité avant et que vous vous inscriviez avec le mail que vous m'avez envoyez) : control.sparkedhost.us

### Database

Pour la database je suis partie sur MongoDB, une database NoSQL. Je sais qu'il y a une data base SQL intégré au panel de hosting, mais je trouvais ca marrant d'utiliser autre chose. Pareil pour se connecter au panel de control de la database il faut que je vous invite avant et que vous vous créez un compte avec la meme adresse mail. Voici le lien : https://cloud.mongodb.com/

Pour bien utiliser mongoDB je vous conseil de télécharger MongoDB Compass : https://www.mongodb.com/try/download/compass

## Comment rejoindre le développement du bot ?

Envoyer moi votre mail sur discord en mp et je vous rajoute sur tous les outils collaboratifs nécessaires (Sparked Host et MongoDB Atlas) avec le bot !
