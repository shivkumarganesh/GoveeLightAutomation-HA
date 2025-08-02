"""Config flow for Govee Light Automation integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_ENABLE_RATE_LIMITING
from .govee_api import GoveeAPI

_LOGGER = logging.getLogger(__name__)


class GoveeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Govee Light Automation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                # Test the API key
                api_key = user_input[CONF_API_KEY]
                enable_rate_limiting = user_input.get(CONF_ENABLE_RATE_LIMITING, True)
                govee_api = GoveeAPI(api_key, enable_rate_limiting)
                
                # Try to get devices to validate the API key
                devices = await govee_api.get_devices()
                
                if devices:
                    await govee_api.close()
                    return self.async_create_entry(
                        title="Govee Light Automation",
                        data=user_input,
                    )
                else:
                    errors["base"] = "no_devices_found"
                    
            except Exception as ex:
                _LOGGER.error("Error during config flow: %s", ex)
                errors["base"] = "invalid_api_key"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                    vol.Optional(CONF_ENABLE_RATE_LIMITING, default=True): bool,
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Handle import from configuration.yaml."""
        return await self.async_step_user(import_info) 