"""Platform for climate integration."""

from __future__ import annotations

from typing import Any
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.components.climate import (
    ClimateEntity,
    HVACMode,
    ClimateEntityFeature,
)
from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN
from homeassistant.const import ATTR_TEMPERATURE

SCAN_INTERVAL = timedelta(seconds=5)

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
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )

    def __init__(self, room, loex_api) -> None:
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, room["id"])},
            name=room["name"],
            manufacturer="Loex",
        )
        self.room = room
        self._attr_name = room["name"]
        self._attr_unique_id = f"{room["id"]}"
        self._attr_current_temperature = room["temp"]
        self._attr_current_humidity = room["humidity"]
        self._attr_target_temperature = room["set"]
        self._attr_preset_mode = room["mode"]
        self.loex_api = loex_api

    async def async_update(self):
        try:
            rooms = await self.loex_api.get_rooms()
            me = next(room for room in rooms if f"{room["id"]}" == self._attr_unique_id)
            if me:
                self.room = me
                self._attr_current_temperature = me["temp"]
                self._attr_current_humidity = me["humidity"]
                self._attr_target_temperature = me["set"]
                self._attr_preset_mode = me["mode"]
                self._attr_name = me["name"]
                self._attr_device_info = DeviceInfo(
                    identifiers={(DOMAIN, me["id"])},
                    name=me["name"],
                    manufacturer="Loex",
                )
        except Exception as e:
            _LOGGER.error(e)

        _LOGGER.info(f"Room {self._attr_name} updated")

    async def async_set_temperature(self, **kwargs: Any) -> None:
        if ATTR_TEMPERATURE in kwargs:
            temperature = kwargs[ATTR_TEMPERATURE]
            diff_temp = temperature - self.target_temperature
            diff_temp = self.room["corr"] + int(diff_temp * 10)
            await self.loex_api.set_temperature(self.room["update_temp_key"], diff_temp)
            self.room["corr"] = diff_temp
            self.target_temperature = temperature
