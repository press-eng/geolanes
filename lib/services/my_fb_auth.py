import aiohttp

from lib import config

client_id = config.FB_CLIENT_ID
client_secret = config.FB_CLIENT_SECRET


async def verify_access_token(access_token):
    # Send the first accessToken returned by Facebook SDK to backend
    user_token = access_token

    # copy clientId, clientSecret from MY APP Page
    appLink = (
        "https://graph.facebook.com/oauth/access_token?client_id="
        + client_id
        + "&client_secret="
        + client_secret
        + "&grant_type=client_credentials"
    )

    try:
        # From appLink, retrieve the second accessToken: app access_token
        async with aiohttp.ClientSession() as session:
            async with session.get(appLink) as response:
                response_json = await response.json()
                app_token = response_json["access_token"]
                link = (
                    "https://graph.facebook.com/debug_token?input_token="
                    + user_token
                    + "&access_token="
                    + app_token
                )

                async with session.get(link) as user_response:
                    user_response_json = await user_response.json()

                    return user_response_json["data"]

    except Exception as e:
        print(e)
        return None


async def get_facebook_friends(customer):
    appLink = (
        "https://graph.facebook.com/oauth/access_token?client_id="
        + client_id
        + "&client_secret="
        + client_secret
        + "&grant_type=client_credentials"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(appLink) as response:
            if response.status == 200:
                response_json = await response.json()
                app_access_token = response_json["access_token"]
            else:
                raise Exception("Failed to obtain app access token")

        api_url = f"https://graph.facebook.com/{customer.facebook_id}/friends"
        params = {"access_token": app_access_token}

        async with session.get(api_url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                return [friend["id"] for friend in data["data"]]
            else:
                raise Exception("Failed to fetch Facebook friends")
