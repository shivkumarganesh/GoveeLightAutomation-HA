"""Config flow for Govee Light Automation integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import ConfigEntryNotReady

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
            api_key = user_input[CONF_API_KEY]
            enable_rate_limiting = user_input.get(CONF_ENABLE_RATE_LIMITING, True)

            # Test the API connection
            api = GoveeAPI(api_key, enable_rate_limiting)
            try:
                await api.get_devices()
                return self.async_create_entry(
                    title="Govee Light Automation",
                    data=user_input,
                )
            except Exception as ex:
                _LOGGER.error("Failed to connect to Govee API: %s", ex)
                errors["base"] = "cannot_connect"

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
