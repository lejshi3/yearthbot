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
batches = collections["batches"]
trades = collections["trades"]

batch_dict = {}

def group_batches():
  for res_batch in batches.get_full_list(200, {
    'sort': 'owner',
    'expand': 'owner, resource',
  }):
    batch_id = res_batch.id
    batch_owner = res_batch.expand['owner'].name
    batch_resource = res_batch.expand['resource'].name
    batch_qty = res_batch.quantity

    key = (batch_owner, batch_resource)
    
    if key not in batch_dict:
      batch_dict[key] = {
        'batch_ids': [batch_id],
        'quantity': batch_qty
      }

    else:
      batch_dict[key]['batch_ids'].append(batch_id)
      batch_dict[key]['quantity'] += batch_qty

  for key, value in batch_dict.items():
    prime_id = value['batch_ids'][0]
    total_qty = value['quantity']
    
    batches.update(prime_id, {'quantity': total_qty})

    for extra_id in value['batch_ids'][1:]:
      batches.delete(extra_id) 

# Use `'filter': 'id = "tdzm2lsrfyxlg9n"'` to filter to just Solia.

def check_trades():
  for trade in trades.get_full_list(200, {
    'sort': 'name',
    'filter': 'isActive = True',
    'expand': 'partyA, partyB'
  }):
    name = trade.name
    partyA = trade.expand['partyA'].id
    partyA_name = trade.expand['partyA'].name
    partyB = trade.expand['partyB'].id
    partyB_name = trade.expand['partyB'].name
    print(f'{name}: {partyA_name} & {partyB_name}')


def monthly_prod():
  for nation in nations.get_full_list(200, {
      'sort': 'name'
    }):
    nation_id = nation.id
    base_prod = nation.base_production
    prod_mod = nation.production_modifiers
    prod = base_prod

    for resource, value in prod_mod.items():
      if resource in prod:
        prod[resource] += value

      else:
        prod[resource] = value
      
    for resource, value in prod.items():
      current_resource = resources.get_first_list_item(
        f'name = "{resource}"'
      )
      
      batches.create({
        'owner': nation_id,
        'resource': current_resource.id,
        'quantity': value
        })
    
check_trades()
group_batches()