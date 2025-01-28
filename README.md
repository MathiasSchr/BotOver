# BotOver

<p align="center">
  <img src="https://files.oaiusercontent.com/file-4jQm2RpeRmvjZsEcr2Z31k?se=2025-01-28T21%3A33%3A47Z&sp=r&sv=2024-08-04&sr=b&rscc=max-age%3D604800%2C%20immutable%2C%20private&rscd=attachment%3B%20filename%3Dcf8d81c1-9a40-49fa-84b6-95fc843001bf.webp&sig=UmM1K%2B45pS68Qn3f1/l/tgaIwJV1BRQfpqRSJu0d1PA%3D" width=500 alt="Logo du projet BotOver">
</p>

## Description

BotOver est un bot Discord collaboratif développé par les membres du serveur **OVER**. Viens rejoindre ce projet pour créer pleins de trucs marrants et débiles sur le serveur.

---

## Architecture du Bot

### Code
Le code de l'application est développé en **Python** et utilise la bibliothèque [discord.py](https://discordpy.readthedocs.io/en/stable/). Tous les fichiers sources se trouvent dans le dossier **/environnement applicatif**.

#### Principales dépendances :
- **discord.py**
- **python-dotenv** : Assure la sécurité des informations sensibles, comme le token du bot et les identifiants de connexion à la base de données, pour éviter qu’ils soient codés en clair.
- **pymongo** : Permet d’établir une connexion avec MongoDB et d’effectuer des requêtes sur la base de données.

### Hébergement
Le bot est hébergé sur la plateforme **Sparked Host**, offrant un panneau de contrôle intuitif pour gérer facilement les paramètres et les configurations du bot.

#### Lien d’accès :
[control.sparkedhost.us](https://control.sparkedhost.us)

> **Note** : Pour accéder au panneau de contrôle, veuillez m'envoyer votre adresse e-mail sur Discord. Je vous ajouterai aux utilisateurs autorisés.

### Base de données
Nous utilisons **MongoDB**, une base de données NoSQL flexible et performante.

#### Raisons de ce choix :
- Expérimenter une technologie différente (par rapport à une base SQL).
- Simplicité de gestion des données non structurées.

> **Note** : Il y a une base de donnée SQL directement intégré à la platforme de hosting Sparked Host, mais je trouvais ça plus marrant de tester autre chose.

#### Lien d’accès :
[MongoDB Atlas](https://cloud.mongodb.com/)

> **Note** : Pour accéder au panneau de contrôle MongoDB, vous devrez créer un compte avec l’adresse e-mail que vous m’avez communiquée.

#### Recommandation :
Pour faciliter la gestion de MongoDB, téléchargez [MongoDB Compass](https://www.mongodb.com/try/download/compass).

---

## Comment rejoindre le développement du bot ?

1. **Envoyez-moi votre adresse e-mail** sur Discord en message privé.
2. **Accès aux outils collaboratifs** :
   - Je vous ajouterai sur Sparked Host et MongoDB Atlas.
   - Vous pourrez configurer vos accès avec l’adresse e-mail fournie.
3. Clonez ce repository et commencez à contribuer !

---

## Fonctionnalités prévues / Idées

- **Statistiques serveur** : Suivi de l’activité et des interactions sur le serveur.
- **Systèmes de jeu** : Mini-jeux intégrés au bot.
- **Personnalisation** : Commandes spécifiques au thème du serveur OVER.

---

## Ressources utiles

- [Documentation Discord.py](https://discordpy.readthedocs.io/en/stable/)
- [MongoDB Atlas](https://cloud.mongodb.com/)
- [MongoDB Compass](https://www.mongodb.com/try/download/compass)

---

<p align="center">✨ **Merci à tous les membres de la team OVER pour leur collaboration !** ✨</p>
