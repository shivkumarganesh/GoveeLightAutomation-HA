"""Config flow for Govee Light Automation integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult

DOMAIN = "govee_light_automation"


class GoveeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Govee Light Automation."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            return self.async_create_entry(
                title="Govee Light Automation",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
        )
