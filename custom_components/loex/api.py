import aiohttp
from aiohttp import ClientTimeout
import logging
from .authenticator import Authenticator

_LOGGER = logging.getLogger(__name__)


class LoexAPI:
    def __init__(self, identifier, username, password):
        self.authenticator = Authenticator(identifier, username, password)
        self.identifier = identifier

    async def get_rooms(self):
        url = f"https://xsmart.loex.it/{self.identifier}/input.json"
        if not hasattr(self, "jwt"):
            self.jwt = await self.authenticator.authenticate()
        timeout = ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(
                url, headers={"Authorization": f"{self.jwt}"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    rooms = []
                    index = 0
                    while True:
                        try:
                            name_key = f"t{20201 + 7 * index}"
                            type_key = f"t{11021 + 10 * index}"
                            temp_key = f"t{11022 + 10 * index}"
                            set_key = f"t{11023 + 10 * index}"
                            error_key = f"t{11024 + 10 * index}"
                            output_key = f"t{11025 + 10 * index}"
                            mode_key = f"t{11026 + 10 * index}"
                            humidity_key = f"t{11027 + 10 * index}"
                            corr_key = f"t{17621 + 10 * index}"
                            symbol_key = f"t{17624 + 10 * index}"
                            schedule_key = f"t{17623 + 10 * index}"
                            gradient_key = f"t{17625 + 10 * index}"

                            if all(
                                key in data
                                for key in [
                                    name_key,
                                    type_key,
                                    temp_key,
                                    set_key,
                                    error_key,
                                    output_key,
                                    mode_key,
                                    humidity_key,
                                    corr_key,
                                    symbol_key,
                                    schedule_key,
                                    gradient_key,
                                ]
                            ):
                                if data[type_key] == 0:
                                    index += 1
                                    continue
                                room = {
                                    "id": 20201 + 7 * index,
                                    "name": data[name_key],
                                    "type": data[type_key],
                                    "temp_key": temp_key,
                                    "temp": round(data[temp_key] / 10, 1),
                                    "set": round(data[set_key] / 10, 1),
                                    "error": data[error_key],
                                    "output": data[output_key],
                                    "mode": data[mode_key],
                                    "humidity": round(data[humidity_key] / 10, 1),
                                    "update_temp_key": 17621 + 10 * index,
                                    "corr": data[corr_key],
                                    "symbol": data[symbol_key],
                                    "schedule": data[schedule_key],
                                    "gradient": data["t10042"]
                                    * (
                                        1
                                        + (
                                            1
                                            if data[gradient_key] == 0
                                            else 3 == data[mode_key]
                                        )
                                    ),
                                }

                                rooms.append(room)
                                index += 1
                            else:
                                break
                        except KeyError:
                            break
                    return rooms
                else:
                    raise Exception(
                        f"Errore durante la richiesta delle stanze: {response.status}"
                    )

    async def set_temperature(self, id, delta_temperature):
        url = f"https://xsmart.loex.it/{self.identifier}/output.json"
        if not hasattr(self, "jwt"):
            self.jwt = await self.authenticator.authenticate()
        body = f"{id}={delta_temperature}"
        _LOGGER.info(f"Setting temperature: {body}")
        timeout = ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                url,
                headers={"Authorization": f"{self.jwt}", "Content-Type": "text/plain"},
                data=body,
            ) as response:
                if response.status != 200:
                    raise Exception(
                        f"Errore durante la richiesta di impostazione della temperatura: {response.status}"
                    )
