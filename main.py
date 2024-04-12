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
from pprint import pprint

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
  'characters': pb.collection('characters'),
  'concepts': pb.collection('concepts'),
  'nations': pb.collection('nations'),
  'tags': pb.collection('tags'),
  "resources": pb.collection("resources"),
  "batches": pb.collection("batches"),
  "trades": pb.collection("trades")
}

ai_models = {
      "haiku": "claude-3-haiku-20240307",
      "sonnet": "claude-3-sonnet-20240229",
      "opus": "claude-3-opus-20240229"
  }

game = collections['game']
npcs = collections['characters']
concepts = collections["concepts"]
nations = collections["nations"]
tags = collections["tags"]
resources = collections["resources"]


# Use `'filter': 'id = "tdzm2lsrfyxlg9n"'` to filter to just Solia.


def monthly_prod():
  for nation in nations.get_full_list(200, {
      'sort': 'name',
      'filter': 'id = "tdzm2lsrfyxlg9n"'
    }):
    nation_id = nation.id
    nation_res = nation.resources
    base_prod = nation.base_production
    prod_mod = nation.production_modifiers
    
    prod = base_prod
    pprint(nation_res)
    
    for modifier in prod_mod:
      name = modifier['name']
      valid = modifier['valid']
      res = modifier['resources']

      for cur_res, value in res.items():
        prod[cur_res] += value

      valid -= 1
      if valid <= 0:
        prod_mod.remove(modifier)

    for cur_res, value in prod.items():
      nation_res[cur_res] += value
      
    pprint(nation_res)
    
monthly_prod()