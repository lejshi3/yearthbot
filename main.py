# main.py
# ---
# The primary function for YearthBot.

import anthropic
import discord
import pocketbase
import dotenv
import os
import time
import asyncio

from anthropic import Anthropic
from pocketbase import PocketBase
from discord import Client as Discord
from dotenv import load_dotenv

# Loading environment variables
def load_env_vars():
  load_dotenv()

  webhook_url = os.getenv("WEBHOOK_URL")
  discord_token = os.getenv("DISCORD_API_KEY")
  anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
  pocketbase_url = os.getenv("POCKETBASE_URL")
  pocketbase_email = os.getenv("POCKETBASE_EMAIL")
  pocketbase_password = os.getenv("POCKETBASE_PASSWORD")

  return {
    "webhook_url": webhook_url,
    "discord_token": discord_token,
    "anthropic_api_key": anthropic_api_key,
    "pocketbase_url": pocketbase_url,
    "pocketbase_email": pocketbase_email,
    "pocketbase_password": pocketbase_password,
}

env_vars = load_env_vars()

# Intializing Discord, Pocketbase, and Anthropic.
snap = Discord (
  intents = discord.Intents.all()
)

claude = Anthropic (
  api_key = env_vars [
    "anthropic_api_key"
  ]
)

pb = PocketBase (
  base_url = env_vars["pocketbase_url"],
)

pb_auth = pb.admins.auth_with_password(
  email = env_vars["pocketbase_email"],
  password = env_vars["pocketbase_password"]
)

# Intialize Pocketbase Collections
collections = {
  'game': pb.collection('game'),
  'npcs': pb.collection('npcs'),
  'events': pb.collection('events'),
  'nations': pb.collection('nations')
}

game = collections['game'].get_full_list()
npcs = collections['npcs'].get_full_list()
events = collections["events"].get_full_list()
nations = collections["nations"].get_full_list()

for npc in npcs:
  print(npc.name)



