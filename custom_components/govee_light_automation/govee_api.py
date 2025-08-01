"""Govee API client for Home Assistant Light Automation integration."""
"""
Govee Light Automation Integration for Home Assistant
Author: Shiv Kumar Ganesh (gshiv.sk@gmail.com)
"""

import logging
from typing import Any, Dict, List, Optional
import aiohttp
import asyncio

from .const import (
    GOVEE_API_DEVICES_URL,
    GOVEE_API_CONTROL_URL,
    CAPABILITY_COLOR,
    CAPABILITY_BRIGHTNESS,
    CAPABILITY_POWER,
)
from .rate_limiter import GoveeRateLimiter

_LOGGER = logging.getLogger(__name__)


class GoveeAPI:
    """Govee API client."""

    def __init__(self, api_key: str, enable_rate_limiting: bool = True):
        """Initialize the Govee API client."""
        self.api_key = api_key
        self.enable_rate_limiting = enable_rate_limiting
        self.session: Optional[aiohttp.ClientSession] = None
        self._devices: Dict[str, Dict[str, Any]] = {}
        self._last_rate_limit_info: Dict[str, Any] = {}
        
        # Initialize rate limiter if enabled
        if self.enable_rate_limiting:
            self.rate_limiter = GoveeRateLimiter()
        else:
            self.rate_limiter = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _make_request(
        self, method: str, url: str, data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Govee API."""
        # Check rate limiting if enabled
        if self.rate_limiter and not self.rate_limiter.can_make_request():
            _LOGGER.warning("Rate limit reached, skipping request")
            raise Exception("Rate limit reached for today")
        
        session = await self._get_session()
        
        headers = {
            "Govee-API-Key": self.api_key,
            "Content-Type": "application/json",
        }

        try:
            if method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    # Capture rate limit headers
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
                    rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'Unknown')
                    
                    # Store rate limit info for sensor
                    if hasattr(self, '_last_rate_limit_info'):
                        self._last_rate_limit_info = {
                            'remaining': rate_limit_remaining,
                            'reset': rate_limit_reset,
                            'timestamp': response.headers.get('Date', 'Unknown')
                        }
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Increment request count if rate limiting is enabled
                    if self.rate_limiter:
                        self.rate_limiter.increment_request_count()
                    
                    return result
            elif method.upper() == "PUT":
                async with session.put(url, headers=headers, json=data) as response:
                    # Capture rate limit headers
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
                    rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'Unknown')
                    
                    # Store rate limit info for sensor
                    if hasattr(self, '_last_rate_limit_info'):
                        self._last_rate_limit_info = {
                            'remaining': rate_limit_remaining,
                            'reset': rate_limit_reset,
                            'timestamp': response.headers.get('Date', 'Unknown')
                        }
                    
                    response.raise_for_status()
                    result = await response.json()
                    
                    # Increment request count if rate limiting is enabled
                    if self.rate_limiter:
                        self.rate_limiter.increment_request_count()
                    
                    return result
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except aiohttp.ClientResponseError as err:
            # Handle rate limit errors specifically
            if err.status == 429:
                rate_limit_remaining = err.headers.get('X-RateLimit-Remaining', '0')
                rate_limit_reset = err.headers.get('X-RateLimit-Reset', 'Unknown')
                _LOGGER.error("Rate limit exceeded! Remaining: %s, Reset: %s", rate_limit_remaining, rate_limit_reset)
                raise Exception(f"Rate limit exceeded. Remaining: {rate_limit_remaining}, Reset: {rate_limit_reset}")
            else:
                _LOGGER.error("Govee API request failed with status %d: %s", err.status, err.message)
                raise
        except aiohttp.ClientError as err:
            _LOGGER.error("Govee API request failed: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Unexpected error during Govee API request: %s", err)
            raise

    async def get_devices(self) -> List[Dict[str, Any]]:
        """Get all devices from Govee API."""
        try:
            response = await self._make_request("GET", GOVEE_API_DEVICES_URL)
            
            if response.get("code") == 200:
                devices = response.get("data", {}).get("devices", [])
                self._devices = {device["device"]: device for device in devices}
                
                # Update device count in rate limiter
                if self.rate_limiter:
                    self.rate_limiter.update_device_count(len(devices))
                    self.rate_limiter.log_rate_limit_status()
                
                return devices
            else:
                _LOGGER.error("Failed to get devices: %s", response.get("message"))
                return []
        except Exception as err:
            _LOGGER.error("Error getting devices: %s", err)
            return []

    async def get_device_state(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a specific device."""
        try:
            url = f"{GOVEE_API_DEVICES_URL}/state?device={device_id}&model={self._devices[device_id]['model']}"
            response = await self._make_request("GET", url)
            
            if response.get("code") == 200:
                return response.get("data", {})
            else:
                _LOGGER.error("Failed to get device state: %s", response.get("message"))
                return None
        except Exception as err:
            _LOGGER.error("Error getting device state: %s", err)
            return None

    async def control_device(
        self, device_id: str, model: str, command: Dict[str, Any]
    ) -> bool:
        """Send control command to a device."""
        try:
            data = {
                "device": device_id,
                "model": model,
                "cmd": command,
            }
            
            response = await self._make_request("PUT", GOVEE_API_CONTROL_URL, data)
            
            if response.get("code") == 200:
                return True
            else:
                _LOGGER.error("Failed to control device: %s", response.get("message"))
                return False
        except Exception as err:
            _LOGGER.error("Error controlling device: %s", err)
            return False

    async def turn_on(self, device_id: str, model: str) -> bool:
        """Turn on a device."""
        command = {
            "name": CAPABILITY_POWER,
            "value": "on"
        }
        return await self.control_device(device_id, model, command)

    async def turn_off(self, device_id: str, model: str) -> bool:
        """Turn off a device."""
        command = {
            "name": CAPABILITY_POWER,
            "value": "off"
        }
        return await self.control_device(device_id, model, command)

    async def set_brightness(self, device_id: str, model: str, brightness: int) -> bool:
        """Set brightness of a device."""
        command = {
            "name": CAPABILITY_BRIGHTNESS,
            "value": brightness
        }
        return await self.control_device(device_id, model, command)

    async def set_color(self, device_id: str, model: str, color: tuple) -> bool:
        """Set color of a device."""
        command = {
            "name": CAPABILITY_COLOR,
            "value": {
                "r": color[0],
                "g": color[1],
                "b": color[2]
            }
        }
        return await self.control_device(device_id, model, command)

    def get_device_info(self, device_id: str) -> Optional[Dict[str, Any]]:
        """Get device information."""
        return self._devices.get(device_id)

    def get_rate_limit_status(self) -> Optional[Dict[str, Any]]:
        """Get current rate limit status."""
        if self.rate_limiter:
            return self.rate_limiter.get_rate_limit_status()
        return None

    def get_adaptive_polling_interval(self) -> int:
        """Get the adaptive polling interval based on rate limiting."""
        if self.rate_limiter:
            return self.rate_limiter.get_adaptive_polling_interval()
        return 120  # Default 2 minutes

    def get_last_rate_limit_info(self) -> Dict[str, Any]:
        """Get the last rate limit information from API headers."""
        return self._last_rate_limit_info

    async def close(self):
        """Close the API session."""
        if self.session and not self.session.closed:
            await self.session.close() 