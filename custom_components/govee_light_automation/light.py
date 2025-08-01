"""Platform for Govee Light Automation integration."""

from __future__ import annotations

import logging
from typing import Any, Optional

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ATTR_HS_COLOR,
    ATTR_RGB_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.util.color import (
    color_hs_to_RGB,
    color_RGB_to_hs,
    color_temperature_kelvin_to_mired,
    color_temperature_mired_to_kelvin,
)

from .const import DOMAIN, SCAN_INTERVAL
from .govee_api import GoveeAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Govee Light Automation platform."""
    api: GoveeAPI = hass.data[DOMAIN][config_entry.entry_id]

    # Create coordinator for device updates with adaptive polling
    def get_adaptive_update_interval():
        """Get adaptive update interval based on rate limiting."""
        return api.get_adaptive_polling_interval()
    
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="govee_lights",
        update_method=api.get_devices,
        update_interval=get_adaptive_update_interval,
    )

    # Get initial devices
    devices = await api.get_devices()
    
    # Create light entities
    entities = []
    for device in devices:
        device_id = device["device"]
        model = device["model"]
        name = device.get("deviceName", f"Govee Light {device_id}")
        
        # Create coordinator for this specific device with adaptive polling
        def get_device_adaptive_interval():
            """Get adaptive update interval for this device."""
            return api.get_adaptive_polling_interval()
        
        device_coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"govee_light_{device_id}",
            update_method=lambda: api.get_device_state(device_id),
            update_interval=get_device_adaptive_interval,
        )
        
        entity = GoveeLight(
            api,
            device_coordinator,
            device_id,
            model,
            name,
        )
        entities.append(entity)

    async_add_entities(entities)


class GoveeLight(CoordinatorEntity, LightEntity):
    """Representation of a Govee Light."""

    def __init__(
        self,
        api: GoveeAPI,
        coordinator: DataUpdateCoordinator,
        device_id: str,
        model: str,
        name: str,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.api = api
        self.device_id = device_id
        self.model = model
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{device_id}"
        self._attr_has_entity_name = False
        
        # Set supported features
        self._attr_supported_color_modes = {ColorMode.RGB}
        self._attr_color_mode = ColorMode.RGB
        self._attr_supported_features = LightEntityFeature.TRANSITION

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        device_info = self.api.get_device_info(self.device_id)
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_id)},
            name=self.name,
            manufacturer="Govee",
            model=device_info.get("model", "Unknown") if device_info else "Unknown",
            sw_version=device_info.get("version", "Unknown") if device_info else "Unknown",
        )

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        if not self.coordinator.data:
            return False
        
        power_state = self.coordinator.data.get("power", "off")
        return power_state == "on"

    @property
    def brightness(self) -> Optional[int]:
        """Return the brightness of this light between 0..255."""
        if not self.coordinator.data:
            return None
        
        brightness = self.coordinator.data.get("brightness", 0)
        # Convert from 0-100 to 0-255
        return int((brightness / 100) * 255)

    @property
    def rgb_color(self) -> Optional[tuple[int, int, int]]:
        """Return the rgb color value."""
        if not self.coordinator.data:
            return None
        
        color_data = self.coordinator.data.get("color", {})
        if color_data:
            return (
                color_data.get("r", 0),
                color_data.get("g", 0),
                color_data.get("b", 0),
            )
        return None

    @property
    def hs_color(self) -> Optional[tuple[float, float]]:
        """Return the hs color value."""
        rgb_color = self.rgb_color
        if rgb_color:
            return color_RGB_to_hs(*rgb_color)
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        # Turn on the light first
        await self.api.turn_on(self.device_id, self.model)
        
        # Set brightness if provided
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
            # Convert from 0-255 to 0-100
            brightness_percent = int((brightness / 255) * 100)
            await self.api.set_brightness(self.device_id, self.model, brightness_percent)
        
        # Set color if provided
        if ATTR_RGB_COLOR in kwargs:
            rgb_color = kwargs[ATTR_RGB_COLOR]
            await self.api.set_color(self.device_id, self.model, rgb_color)
        elif ATTR_HS_COLOR in kwargs:
            hs_color = kwargs[ATTR_HS_COLOR]
            rgb_color = color_hs_to_RGB(*hs_color)
            await self.api.set_color(self.device_id, self.model, rgb_color)
        
        # Refresh the coordinator
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self.api.turn_off(self.device_id, self.model)
        await self.coordinator.async_request_refresh() 