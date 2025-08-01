"""Platform for Govee Light Automation rate limit sensor."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN
from .govee_api import GoveeAPI

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Govee Light Automation sensor platform."""
    api: GoveeAPI = hass.data[DOMAIN][config_entry.entry_id]

    # Create coordinator for rate limit updates
    def get_rate_limit_data():
        """Get rate limit status data."""
        return api.get_rate_limit_status()

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="govee_rate_limit",
        update_method=get_rate_limit_data,
        update_interval=300,  # Update every 5 minutes
    )

    # Create rate limit sensor
    entities = []
    
    # Rate limit sensor
    rate_limit_sensor = GoveeRateLimitSensor(
        coordinator,
        api,
        "Govee API Rate Limit",
        "govee_rate_limit",
    )
    entities.append(rate_limit_sensor)
    
    # Device count sensor
    device_count_sensor = GoveeDeviceCountSensor(
        coordinator,
        api,
        "Govee Device Count",
        "govee_device_count",
    )
    entities.append(device_count_sensor)
    
    # Polling interval sensor
    polling_sensor = GoveePollingIntervalSensor(
        coordinator,
        api,
        "Govee Polling Interval",
        "govee_polling_interval",
    )
    entities.append(polling_sensor)
    
    # API calls tracking sensor
    api_calls_sensor = GoveeAPICallsSensor(
        coordinator,
        api,
        "Govee API Calls",
        "govee_api_calls",
    )
    entities.append(api_calls_sensor)

    async_add_entities(entities)


class GoveeRateLimitSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Govee Rate Limit sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: GoveeAPI,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "rate_limit")},
            name="Govee Rate Limiter",
            manufacturer="Govee",
            model="Rate Limiter",
        )

    @property
    def native_value(self) -> float:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0.0
        
        return self.coordinator.data.get("usage_percentage", 0.0)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return PERCENTAGE

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "request_count": self.coordinator.data.get("request_count", 0),
            "remaining_requests": self.coordinator.data.get("remaining_requests", 0),
            "device_count": self.coordinator.data.get("device_count", 0),
            "can_make_request": self.coordinator.data.get("can_make_request", True),
            "last_reset_date": self.coordinator.data.get("last_reset_date", ""),
        }


class GoveeDeviceCountSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Govee Device Count sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: GoveeAPI,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "device_count")},
            name="Govee Device Counter",
            manufacturer="Govee",
            model="Device Counter",
        )

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
        
        return self.coordinator.data.get("device_count", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "request_count": self.coordinator.data.get("request_count", 0),
            "usage_percentage": self.coordinator.data.get("usage_percentage", 0.0),
            "remaining_requests": self.coordinator.data.get("remaining_requests", 0),
        }


class GoveePollingIntervalSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Govee Polling Interval sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: GoveeAPI,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "polling_interval")},
            name="Govee Polling Interval",
            manufacturer="Govee",
            model="Polling Interval",
        )

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 120
        
        return self.coordinator.data.get("adaptive_polling_interval", 120)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "seconds"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "device_count": self.coordinator.data.get("device_count", 0),
            "usage_percentage": self.coordinator.data.get("usage_percentage", 0.0),
            "remaining_requests": self.coordinator.data.get("remaining_requests", 0),
        }


class GoveeAPICallsSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Govee API Calls sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        api: GoveeAPI,
        name: str,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.api = api
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, "api_calls")},
            name="Govee API Calls Tracker",
            manufacturer="Govee",
            model="API Calls Tracker",
        )

    @property
    def native_value(self) -> int:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return 0
        
        return self.coordinator.data.get("request_count", 0)

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement."""
        return "calls"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}
        
        # Get rate limit status
        rate_limit_status = self.api.get_rate_limit_status()
        
        # Get last API rate limit info
        last_api_info = self.api.get_last_rate_limit_info()
        
        # Calculate status based on usage
        usage_percentage = rate_limit_status.get("usage_percentage", 0.0)
        if usage_percentage < 80:
            status = "Normal"
        elif usage_percentage < 95:
            status = "Warning"
        else:
            status = "Critical"
        
        # Parse reset time if available
        reset_time_formatted = "Unknown"
        if last_api_info.get("reset") and last_api_info.get("reset") != "Unknown":
            try:
                from datetime import datetime
                reset_timestamp = int(last_api_info.get("reset"))
                reset_time = datetime.fromtimestamp(reset_timestamp)
                reset_time_formatted = reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            except (ValueError, TypeError):
                reset_time_formatted = last_api_info.get("reset", "Unknown")
        
        return {
            "total_calls_today": rate_limit_status.get("request_count", 0),
            "remaining_calls": rate_limit_status.get("remaining_requests", 0),
            "usage_percentage": usage_percentage,
            "daily_limit": 10000,
            "device_count": rate_limit_status.get("device_count", 0),
            "adaptive_polling_interval": rate_limit_status.get("adaptive_polling_interval", 120),
            "last_reset_date": rate_limit_status.get("last_reset_date", "Unknown"),
            "rate_limit_status": status,
            "api_remaining_calls": last_api_info.get("remaining", "Unknown"),
            "api_reset_time": reset_time_formatted,
            "last_api_call_time": last_api_info.get("timestamp", "Unknown"),
        } 