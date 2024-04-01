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

import pandas as pd

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
  api_key = env_vars["anthropic_api_key"]
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
  'concepts': pb.collection('concepts'),
  'nations': pb.collection('nations'),
  'tags': pb.collection('tags')
}

ai_models = {
      "haiku": "claude-3-haiku-20240307",
      "sonnet": "claude-3-sonnet-20240229",
      "opus": "claude-3-opus-20240229"
  }

game = collections['game']
npcs = collections['npcs']
concepts = collections["concepts"]
nations = collections["nations"]
tags = collections["tags"]

knowledge_list = []
tag_list = []

for tag in tags.get_full_list(200, {
  'sort': 'name'
}):
  tag_list.append(tag.name)

all_tags = ", ".join(tag_list)

current_tags = "Blixt Imperium, Kentucky"
current_tag_list = current_tags.split(", ")

for tag in current_tag_list:
  for concept in concepts.get_full_list(50, {'filter': f'tags.name ?= "{tag}"'}):
      knowledge_list.append(f"{concept.name} \n--- \n{concept.description}\n""")

temp_df = pd.DataFrame({'col': knowledge_list})
temp_df.drop_duplicates(inplace = True)

pruned_knowledge_list = temp_df['col'].to_list()
knowledge = "\n".join(pruned_knowledge_list)

print(knowledge)

