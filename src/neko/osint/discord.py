import os
import requests

ENDPOINT = "https://discord.com/api/v10"

def get_token():
    return os.getenv("DISCORD_BOT_TOKEN")

def get_user(user_id):
    token = get_token()
    result = requests.get(f"{ENDPOINT}/users/{user_id}", headers={"Authorization": f"Bot {token}"})
    return result.json()
