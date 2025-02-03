# config.py

import os
from dotenv import load_dotenv

# variables d'environnement
load_dotenv()
TOKEN = os.getenv('TEST')
uri = os.getenv('URI')