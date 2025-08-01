"""Rate limiter for Govee Light Automation API to prevent hitting daily limits."""
"""
Govee Light Automation Integration for Home Assistant
Author: Shiv Kumar Ganesh (gshiv.sk@gmail.com)
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json
import os

from .const import (
    DAILY_REQUEST_LIMIT,
    SAFE_REQUEST_LIMIT,
    REQUESTS_PER_DEVICE_PER_DAY,
    MIN_POLLING_INTERVAL,
    MAX_POLLING_INTERVAL,
    DEFAULT_POLLING_INTERVAL,
    RATE_LIMIT_STORAGE_KEY,
    RATE_LIMIT_LAST_RESET_KEY,
    RATE_LIMIT_REQUEST_COUNT_KEY,
    RATE_LIMIT_DEVICE_COUNT_KEY,
)

_LOGGER = logging.getLogger(__name__)


class GoveeRateLimiter:
    """Rate limiter for Govee API calls."""

    def __init__(self, storage_path: str = None):
        """Initialize the rate limiter."""
        self.storage_path = storage_path or "govee_rate_limit.json"
        self._load_rate_limit_data()

    def _load_rate_limit_data(self) -> None:
        """Load rate limit data from storage."""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.last_reset_date = data.get(RATE_LIMIT_LAST_RESET_KEY)
                    self.request_count = data.get(RATE_LIMIT_REQUEST_COUNT_KEY, 0)
                    self.device_count = data.get(RATE_LIMIT_DEVICE_COUNT_KEY, 0)
            else:
                self._reset_rate_limit_data()
        except Exception as e:
            _LOGGER.error("Error loading rate limit data: %s", e)
            self._reset_rate_limit_data()

    def _save_rate_limit_data(self) -> None:
        """Save rate limit data to storage."""
        try:
            data = {
                RATE_LIMIT_LAST_RESET_KEY: self.last_reset_date,
                RATE_LIMIT_REQUEST_COUNT_KEY: self.request_count,
                RATE_LIMIT_DEVICE_COUNT_KEY: self.device_count,
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            _LOGGER.error("Error saving rate limit data: %s", e)

    def _reset_rate_limit_data(self) -> None:
        """Reset rate limit data for a new day."""
        self.last_reset_date = datetime.now().strftime("%Y-%m-%d")
        self.request_count = 0
        self.device_count = 0
        self._save_rate_limit_data()

    def _check_and_reset_daily(self) -> None:
        """Check if we need to reset for a new day."""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.last_reset_date != today:
            _LOGGER.info("Resetting rate limit for new day")
            self._reset_rate_limit_data()

    def increment_request_count(self) -> None:
        """Increment the request count."""
        self._check_and_reset_daily()
        self.request_count += 1
        self._save_rate_limit_data()
        _LOGGER.debug("Request count: %d/%d", self.request_count, SAFE_REQUEST_LIMIT)

    def update_device_count(self, device_count: int) -> None:
        """Update the device count."""
        self._check_and_reset_daily()
        if self.device_count != device_count:
            self.device_count = device_count
            self._save_rate_limit_data()
            _LOGGER.info("Updated device count: %d", device_count)

    def get_remaining_requests(self) -> int:
        """Get the number of remaining requests for today."""
        self._check_and_reset_daily()
        return max(0, SAFE_REQUEST_LIMIT - self.request_count)

    def get_usage_percentage(self) -> float:
        """Get the current usage percentage."""
        self._check_and_reset_daily()
        return (self.request_count / SAFE_REQUEST_LIMIT) * 100

    def can_make_request(self) -> bool:
        """Check if we can make a request without hitting the limit."""
        return self.get_remaining_requests() > 0

    def get_adaptive_polling_interval(self) -> int:
        """Calculate adaptive polling interval based on device count and usage."""
        self._check_and_reset_daily()
        
        if self.device_count == 0:
            return DEFAULT_POLLING_INTERVAL
        
        # Calculate how many requests we need per day for all devices
        required_requests_per_day = self.device_count * REQUESTS_PER_DEVICE_PER_DAY
        
        # Calculate how many requests we have left
        remaining_requests = self.get_remaining_requests()
        
        # Calculate how many requests we can make per device per day
        if remaining_requests <= 0:
            # We're at the limit, use maximum interval
            return MAX_POLLING_INTERVAL
        
        # Calculate optimal interval based on remaining requests and devices
        if self.device_count > 0:
            requests_per_device_per_day = remaining_requests / self.device_count
            if requests_per_device_per_day > 0:
                # Convert to seconds (86400 seconds in a day)
                optimal_interval = 86400 / requests_per_device_per_day
                
                # Clamp to our min/max range
                optimal_interval = max(MIN_POLLING_INTERVAL, min(MAX_POLLING_INTERVAL, optimal_interval))
                
                _LOGGER.debug(
                    "Adaptive polling: %d devices, %d remaining requests, "
                    "%.1f requests/device/day, %.1f second interval",
                    self.device_count, remaining_requests, requests_per_device_per_day, optimal_interval
                )
                
                return int(optimal_interval)
        
        return DEFAULT_POLLING_INTERVAL

    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status."""
        self._check_and_reset_daily()
        
        return {
            "request_count": self.request_count,
            "device_count": self.device_count,
            "remaining_requests": self.get_remaining_requests(),
            "usage_percentage": self.get_usage_percentage(),
            "can_make_request": self.can_make_request(),
            "adaptive_polling_interval": self.get_adaptive_polling_interval(),
            "last_reset_date": self.last_reset_date,
        }

    def log_rate_limit_status(self) -> None:
        """Log current rate limit status."""
        status = self.get_rate_limit_status()
        _LOGGER.info(
            "Rate limit status: %d/%d requests used (%.1f%%), "
            "%d devices, %d remaining requests, %d second polling interval",
            status["request_count"], SAFE_REQUEST_LIMIT, status["usage_percentage"],
            status["device_count"], status["remaining_requests"], 
            status["adaptive_polling_interval"]
        ) 