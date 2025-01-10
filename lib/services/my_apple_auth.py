from datetime import datetime
import aiohttp
from jose import jwt as jose_jwt
from lib import config


async def verify_id_token(token: str):
    try:
        async with aiohttp.ClientSession() as session:

            async with session.get("https://appleid.apple.com/auth/keys") as response:

                jwks = await response.json()

                # Get the appropriate key for token verification
                header = jose_jwt.get_unverified_header(token)
                rsa_key = {}
                for key in jwks["keys"]:
                    if key["kid"] == header["kid"]:
                        rsa_key = {
                            "kty": key["kty"],
                            "kid": key["kid"],
                            "use": key["use"],
                            "n": key["n"],
                            "e": key["e"],
                        }
                        break
                if rsa_key:
                    info = jose_jwt.decode(
                        token, rsa_key, algorithms=["RS256"], audience=config.APPLE_CLIENT_ID
                    )
                    expiration = datetime.fromtimestamp(info["exp"])
                    if (
                        info["aud"] == config.APPLE_CLIENT_ID
                        and info["iss"] == "https://appleid.apple.com"
                        and expiration > datetime.utcnow()
                    ):
                        return info
    except Exception as e:
        raise Exception("Cannot verify Apple ID token!") from e
