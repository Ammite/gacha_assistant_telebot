from uu import Error
import requests
from urllib3 import response

promocodes_api = {
    "genshin": "https://hoyo-codes.seria.moe/codes?game=genshin",
    "hsr": "https://hoyo-codes.seria.moe/codes?game=hkrpg",
    "zzz": "https://hoyo-codes.seria.moe/codes?game=nap",
    "wuwa": None
}


def get_promocodes(game_name):
    url = promocodes_api.get(game_name, None)
    if not url:
        raise Error(f"No such game as {game_name}")
    
    response = requests.get(url)
    data: dict = response.json()

    codes = data.get("codes", [])

    return codes
