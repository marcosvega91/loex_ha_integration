import aiohttp
import base64

from homeassistant.exceptions import HomeAssistantError


class Authenticator:
    def __init__(self, identifier, username, password):
        self.username = username
        self.password = password
        self.identifier = identifier

    async def authenticate(self):
        basic_auth = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode("utf-8")

        # URL dell'API con il parametro di query identifier
        url = "https://xsmart.loex.it/jwt"
        params = {"id": self.identifier}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url, params=params, headers={"Authorization": f"Basic {basic_auth}"}
            ) as response:
                if response.status == 200:
                    content = await response.text()
                    return content
                else:
                    raise InvalidAuth(f"Error authentication: {response.status}")


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
