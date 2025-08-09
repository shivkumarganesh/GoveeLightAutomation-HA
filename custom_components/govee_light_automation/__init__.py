"""Govee Light Automation integration for Home Assistant.

Author: Shiv Kumar Ganesh (gshiv.sk@gmail.com)
"""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryNotReady
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, CONF_ENABLE_RATE_LIMITING
from .govee_api import GoveeAPI

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT, Platform.SENSOR]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the Govee Light Automation component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Govee Light Automation from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    enable_rate_limiting = entry.data.get(CONF_ENABLE_RATE_LIMITING, True)
    
    govee_api = GoveeAPI(api_key, enable_rate_limiting)
    
    try:
        # Test the API connection
        await govee_api.get_devices()
    except Exception as ex:
        _LOGGER.error("Failed to connect to Govee API: %s", ex)
        raise ConfigEntryNotReady from ex

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = govee_api

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
            }
        )
    }
)
