"""Platform for climate integration."""

from __future__ import annotations
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.climate import ClimateEntity, HVACMode
from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=10)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    loex_api = hass.data[DOMAIN][config_entry.entry_id]
    try:
        rooms = await loex_api.get_rooms()
        async_add_entities(LoexRoom(room, loex_api) for room in rooms)
    except Exception as e:
        _LOGGER.error(e)
        async_add_entities([])


class LoexRoom(ClimateEntity):
    _attr_hvac_modes = [HVACMode.HEAT_COOL]
    _attr_hvac_mode = HVACMode.HEAT_COOL
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_preset_modes = ["auto", "comfort", "eco", "off"]

    def __init__(self, room, loex_api) -> None:
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, room["id"])},
            name=room["name"],
            manufacturer="Loex",
        )
        self._attr_name = room["name"]
        self._attr_unique_id = f"{room["id"]}"
        self.current_temperature = room["temp"]
        self.current_humidity = room["humidity"]
        self.target_temperature = room["set"]
        self.preset_mode = room["mode"]
        self.loex_api = loex_api

    async def async_update(self):
        try:
            rooms = await self.loex_api.get_rooms()
            me = next(room for room in rooms if f"{room["id"]}" == self._attr_unique_id)
            if me:
                self.current_temperature = me["temp"]
                self.current_humidity = me["humidity"]
                self.target_temperature = me["set"]
                self.preset_mode = me["mode"]
                self._attr_name = me["name"]
                self._attr_device_info = DeviceInfo(
                    identifiers={(DOMAIN, me["id"])},
                    name=me["name"],
                    manufacturer="Loex",
                )
        except Exception as e:
            _LOGGER.error(e)
