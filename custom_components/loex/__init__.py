"""The Loex integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from .api import LoexAPI
from .const import DOMAIN, IDENTIFIER
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME

PLATFORMS: list[Platform] = [Platform.CLIMATE]


# TODO Update entry annotation
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    loex_api = LoexAPI(
        entry.data[IDENTIFIER], entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
    )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = loex_api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True
