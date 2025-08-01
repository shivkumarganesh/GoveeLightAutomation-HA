"""Constants for the Govee Light Automation integration."""

DOMAIN = "govee_light_automation"

# Configuration
CONF_API_KEY = "api_key"
CONF_POLLING_INTERVAL = "polling_interval"
CONF_ENABLE_RATE_LIMITING = "enable_rate_limiting"

# API endpoints
GOVEE_API_BASE_URL = "https://developer-api.govee.com/v1"
GOVEE_API_DEVICES_URL = f"{GOVEE_API_BASE_URL}/devices"
GOVEE_API_CONTROL_URL = f"{GOVEE_API_BASE_URL}/devices/control"

# Device capabilities
CAPABILITY_COLOR = "color"
CAPABILITY_BRIGHTNESS = "brightness"
CAPABILITY_POWER = "power"

# Default values
DEFAULT_NAME = "Govee Light"
DEFAULT_BRIGHTNESS = 255
DEFAULT_COLOR = (255, 255, 255)  # White

# Rate limiting configuration
DAILY_REQUEST_LIMIT = 10000
SAFE_REQUEST_LIMIT = 9000  # Stay under 90% of limit
REQUESTS_PER_DEVICE_PER_DAY = 1440  # 1 request per minute per device
MIN_POLLING_INTERVAL = 60  # Minimum 60 seconds between polls
MAX_POLLING_INTERVAL = 300  # Maximum 5 minutes between polls
DEFAULT_POLLING_INTERVAL = 120  # Default 2 minutes

# Update intervals
SCAN_INTERVAL = 30  # seconds

# Rate limiting storage keys
RATE_LIMIT_STORAGE_KEY = "govee_rate_limit"
RATE_LIMIT_LAST_RESET_KEY = "last_reset_date"
RATE_LIMIT_REQUEST_COUNT_KEY = "request_count"
RATE_LIMIT_DEVICE_COUNT_KEY = "device_count" 