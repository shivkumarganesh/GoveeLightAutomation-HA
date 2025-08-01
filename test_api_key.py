#!/usr/bin/env python3
"""
Simple test script to verify your Govee API key works.
Run this before installing the Govee Light Automation integration in Home Assistant.
"""

import asyncio
import sys
import aiohttp
import json


async def test_govee_api(api_key: str):
    """Test the Govee API with your API key."""
    
    url = "https://developer-api.govee.com/v1/devices"
    headers = {
        "Govee-API-Key": api_key,
        "Content-Type": "application/json",
    }
    
    print(f"🔑 Testing API key: {api_key[:8]}...")
    print(f"🌐 Testing URL: {url}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📡 Response Status: {response.status}")
                
                # Parse rate limit headers
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
                rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'Unknown')
                
                print(f"📊 Rate Limit Remaining: {rate_limit_remaining}")
                
                # Parse and display reset time
                if rate_limit_reset != 'Unknown':
                    try:
                        reset_timestamp = int(rate_limit_reset)
                        from datetime import datetime
                        reset_time = datetime.fromtimestamp(reset_timestamp)
                        print(f"🕐 Rate Limit Resets At: {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    except (ValueError, TypeError):
                        print(f"🕐 Rate Limit Reset (raw): {rate_limit_reset}")
                else:
                    print("🕐 Rate Limit Reset: Unknown")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API Key is valid!")
                    print(f"📊 Response Code: {data.get('code')}")
                    
                    devices = data.get('data', {}).get('devices', [])
                    print(f"💡 Found {len(devices)} devices:")
                    
                    for i, device in enumerate(devices, 1):
                        print(f"  {i}. {device.get('deviceName', 'Unknown')}")
                        print(f"     Device ID: {device.get('device')}")
                        print(f"     Model: {device.get('model')}")
                        print(f"     Controllable: {device.get('controllable')}")
                        print(f"     Retrievable: {device.get('retrievable')}")
                        print()
                    
                    return True
                else:
                    error_data = await response.json()
                    print("❌ API Key test failed!")
                    print(f"Error Code: {error_data.get('code')}")
                    print(f"Error Message: {error_data.get('message')}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False


async def test_device_state(api_key: str, device_id: str, model: str):
    """Test getting device state."""
    
    url = f"https://developer-api.govee.com/v1/devices/state?device={device_id}&model={model}"
    headers = {
        "Govee-API-Key": api_key,
        "Content-Type": "application/json",
    }
    
    print(f"🔍 Testing device state for {device_id}")
    print(f"🌐 URL: {url}")
    print("-" * 50)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                print(f"📡 Response Status: {response.status}")
                
                # Parse rate limit headers
                rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', 'Unknown')
                rate_limit_reset = response.headers.get('X-RateLimit-Reset', 'Unknown')
                
                print(f"📊 Rate Limit Remaining: {rate_limit_remaining}")
                
                # Parse and display reset time
                if rate_limit_reset != 'Unknown':
                    try:
                        reset_timestamp = int(rate_limit_reset)
                        from datetime import datetime
                        reset_time = datetime.fromtimestamp(reset_timestamp)
                        print(f"🕐 Rate Limit Resets At: {reset_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
                    except (ValueError, TypeError):
                        print(f"🕐 Rate Limit Reset (raw): {rate_limit_reset}")
                else:
                    print("🕐 Rate Limit Reset: Unknown")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ Device state retrieved successfully!")
                    print(f"📊 Response Code: {data.get('code')}")
                    
                    state_data = data.get('data', {})
                    print("📋 Device State:")
                    print(f"  Power: {state_data.get('power')}")
                    print(f"  Brightness: {state_data.get('brightness')}")
                    
                    color = state_data.get('color', {})
                    if color:
                        print(f"  Color: R={color.get('r')}, G={color.get('g')}, B={color.get('b')}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print("❌ Failed to get device state!")
                    print(f"Error Code: {error_data.get('code')}")
                    print(f"Error Message: {error_data.get('message')}")
                    return False
                    
    except Exception as e:
        print(f"❌ Error getting device state: {e}")
        return False


async def main():
    """Main test function."""
    print("🧪 Govee API Key Test")
    print("=" * 50)
    
    # Get API key from user
    api_key = input("Enter your Govee API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    # Test basic API connectivity
    success = await test_govee_api(api_key)
    
    if success:
        print("\n🎉 Your API key is working! You can now install the integration.")
        print("\n📋 Next steps:")
        print("1. Copy the custom_components/govee_light_automation folder to your Home Assistant config/custom_components/")
        print("2. Restart Home Assistant")
        print("3. Go to Settings → Devices & Services → Integrations")
        print("4. Add 'Govee Light Automation' integration")
        print("5. Enter your API key in the setup wizard")
    else:
        print("\n❌ API key test failed. Please check your API key and try again.")
        print("Make sure you have:")
        print("- Obtained an API key from https://developer.govee.com/")
        print("- Your Govee devices are connected to the internet")
        print("- Your devices are registered in the Govee app")


if __name__ == "__main__":
    asyncio.run(main()) 