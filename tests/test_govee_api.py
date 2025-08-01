"""Tests for the Govee Light Automation API client."""

import pytest
import aiohttp
from unittest.mock import AsyncMock, patch

from custom_components.govee_light_automation.govee_api import GoveeAPI


class TestGoveeAPI:
    """Test the Govee Light Automation API client."""

    @pytest.fixture
    def api(self):
        """Create a Govee API instance for testing."""
        return GoveeAPI("test_api_key")

    @pytest.mark.asyncio
    async def test_init(self, api):
        """Test API initialization."""
        assert api.api_key == "test_api_key"
        assert api.session is None
        assert api._devices == {}

    @pytest.mark.asyncio
    async def test_get_session(self, api):
        """Test session creation."""
        session = await api._get_session()
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed

    @pytest.mark.asyncio
    async def test_make_request_get(self, api):
        """Test GET request."""
        with patch.object(api, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.json.return_value = {"code": 200, "data": {"test": "data"}}
            mock_response.raise_for_status.return_value = None
            mock_session.get.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await api._make_request("GET", "http://test.com")
            assert result == {"code": 200, "data": {"test": "data"}}

    @pytest.mark.asyncio
    async def test_make_request_put(self, api):
        """Test PUT request."""
        with patch.object(api, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.json.return_value = {"code": 200, "data": {"test": "data"}}
            mock_response.raise_for_status.return_value = None
            mock_session.put.return_value.__aenter__.return_value = mock_response
            mock_get_session.return_value = mock_session

            result = await api._make_request("PUT", "http://test.com", {"test": "data"})
            assert result == {"code": 200, "data": {"test": "data"}}

    @pytest.mark.asyncio
    async def test_get_devices_success(self, api):
        """Test successful device retrieval."""
        mock_devices = [
            {"device": "test_device_1", "model": "test_model_1", "deviceName": "Test Light 1"},
            {"device": "test_device_2", "model": "test_model_2", "deviceName": "Test Light 2"},
        ]
        
        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = {
                "code": 200,
                "data": {"devices": mock_devices}
            }

            result = await api.get_devices()
            assert result == mock_devices
            assert len(api._devices) == 2
            assert "test_device_1" in api._devices

    @pytest.mark.asyncio
    async def test_get_devices_failure(self, api):
        """Test failed device retrieval."""
        with patch.object(api, '_make_request') as mock_request:
            mock_request.return_value = {
                "code": 400,
                "message": "Invalid API key"
            }

            result = await api.get_devices()
            assert result == []

    @pytest.mark.asyncio
    async def test_turn_on(self, api):
        """Test turning on a device."""
        with patch.object(api, 'control_device') as mock_control:
            mock_control.return_value = True

            result = await api.turn_on("test_device", "test_model")
            assert result is True
            mock_control.assert_called_once()

    @pytest.mark.asyncio
    async def test_turn_off(self, api):
        """Test turning off a device."""
        with patch.object(api, 'control_device') as mock_control:
            mock_control.return_value = True

            result = await api.turn_off("test_device", "test_model")
            assert result is True
            mock_control.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_brightness(self, api):
        """Test setting brightness."""
        with patch.object(api, 'control_device') as mock_control:
            mock_control.return_value = True

            result = await api.set_brightness("test_device", "test_model", 50)
            assert result is True
            mock_control.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_color(self, api):
        """Test setting color."""
        with patch.object(api, 'control_device') as mock_control:
            mock_control.return_value = True

            result = await api.set_color("test_device", "test_model", (255, 0, 0))
            assert result is True
            mock_control.assert_called_once()

    @pytest.mark.asyncio
    async def test_close(self, api):
        """Test closing the API session."""
        with patch.object(api, '_get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.closed = False
            mock_get_session.return_value = mock_session

            await api.close()
            mock_session.close.assert_called_once() 