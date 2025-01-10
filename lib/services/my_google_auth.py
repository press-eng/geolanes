from datetime import datetime

import aiohttp

from lib import config


async def verify_id_token(token):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"
            ) as response:
                info = await response.json()
                expiration = datetime.fromtimestamp(int(info["exp"]))
                if (
                    info["aud"] == config.GOOGLE_CLIENT_ID
                    and info["iss"] == "https://accounts.google.com"
                    and expiration > datetime.utcnow()
                ):
                    return info
    except:
        raise Exception("Cannot verify Google ID token!")
