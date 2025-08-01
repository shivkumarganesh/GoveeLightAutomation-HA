#!/usr/bin/env python3
"""
Test script using the actual integration code.
This tests the GoveeAPI class and simulates Home Assistant Light Automation integration.
"""

import asyncio
import sys
import os

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from govee_light_automation.govee_api import GoveeAPI


async def test_integration_api(api_key: str):
    """Test the integration using the actual GoveeAPI class."""
    
    print("🧪 Testing Govee Light Automation API")
    print("=" * 50)
    
    # Create API instance
    api = GoveeAPI(api_key)
    
    try:
        # Test device discovery
        print("🔍 Testing device discovery...")
        devices = await api.get_devices()
        
        if devices:
            print(f"✅ Found {len(devices)} devices:")
            
            for i, device in enumerate(devices, 1):
                device_id = device.get('device')
                model = device.get('model')
                name = device.get('deviceName', 'Unknown')
                
                print(f"\n  {i}. {name}")
                print(f"     Device ID: {device_id}")
                print(f"     Model: {model}")
                print(f"     Controllable: {device.get('controllable')}")
                print(f"     Retrievable: {device.get('retrievable')}")
                
                # Test device state if retrievable
                if device.get('retrievable'):
                    print("     📊 Testing device state...")
                    state = await api.get_device_state(device_id)
                    if state:
                        print(f"        Power: {state.get('power', 'unknown')}")
                        print(f"        Brightness: {state.get('brightness', 'unknown')}")
                        
                        color = state.get('color', {})
                        if color:
                            print(f"        Color: R={color.get('r')}, G={color.get('g')}, B={color.get('b')}")
                    else:
                        print("        ❌ Failed to get device state")
                
                # Test basic control if controllable
                if device.get('controllable'):
                    print("     🎛️  Testing basic control...")
                    
                    # Test turn on
                    print("        Testing turn on...")
                    on_success = await api.turn_on(device_id, model)
                    print(f"        Turn on: {'✅' if on_success else '❌'}")
                    
                    # Wait a moment
                    await asyncio.sleep(2)
                    
                    # Test brightness
                    print("        Testing brightness control...")
                    brightness_success = await api.set_brightness(device_id, model, 50)
                    print(f"        Set brightness: {'✅' if brightness_success else '❌'}")
                    
                    # Wait a moment
                    await asyncio.sleep(2)
                    
                    # Test color
                    print("        Testing color control...")
                    color_success = await api.set_color(device_id, model, (255, 0, 0))  # Red
                    print(f"        Set color: {'✅' if color_success else '❌'}")
                    
                    # Wait a moment
                    await asyncio.sleep(2)
                    
                    # Test turn off
                    print("        Testing turn off...")
                    off_success = await api.turn_off(device_id, model)
                    print(f"        Turn off: {'✅' if off_success else '❌'}")
                    
                    print("        ✅ Control tests completed")
                else:
                    print("     ⚠️  Device not controllable")
            
            print(f"\n🎉 Integration test completed successfully!")
            print(f"📊 Summary: {len(devices)} devices found and tested")
            
        else:
            print("❌ No devices found. Please check:")
            print("   - Your API key is correct")
            print("   - Your devices are connected to the internet")
            print("   - Your devices are registered in the Govee app")
            return False
            
    except Exception as e:
        print(f"❌ Error during integration test: {e}")
        return False
    finally:
        # Clean up
        await api.close()
    
    return True


async def test_specific_device(api_key: str, device_id: str, model: str):
    """Test a specific device with more detailed control."""
    
    print(f"🎯 Testing specific device: {device_id}")
    print("=" * 50)
    
    api = GoveeAPI(api_key)
    
    try:
        # Test different colors
        colors = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("White", (255, 255, 255)),
            ("Purple", (128, 0, 128)),
        ]
        
        print("🎨 Testing color sequence...")
        for color_name, rgb in colors:
            print(f"   Setting {color_name}...")
            success = await api.set_color(device_id, model, rgb)
            print(f"   {color_name}: {'✅' if success else '❌'}")
            await asyncio.sleep(1)
        
        # Test brightness levels
        print("\n💡 Testing brightness levels...")
        brightness_levels = [25, 50, 75, 100]
        for level in brightness_levels:
            print(f"   Setting brightness to {level}%...")
            success = await api.set_brightness(device_id, model, level)
            print(f"   {level}%: {'✅' if success else '❌'}")
            await asyncio.sleep(1)
        
        # Turn off
        print("\n🔌 Turning off...")
        await api.turn_off(device_id, model)
        print("   ✅ Device turned off")
        
    except Exception as e:
        print(f"❌ Error testing specific device: {e}")
    finally:
        await api.close()


async def main():
    """Main test function."""
    print("🧪 Govee Integration Test")
    print("=" * 50)
    
    # Get API key from user
    api_key = input("Enter your Govee API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    # Test basic integration
    success = await test_integration_api(api_key)
    
    if success:
        print("\n🎉 Integration test successful!")
        print("\n📋 Ready to install in Home Assistant:")
        print("1. Copy custom_components/govee_lights to your HA config/custom_components/")
        print("2. Restart Home Assistant")
        print("3. Add 'Govee Lights' integration via UI")
        
        # Ask if user wants to test a specific device
        test_specific = input("\nWould you like to test a specific device? (y/n): ").strip().lower()
        if test_specific == 'y':
            device_id = input("Enter device ID: ").strip()
            model = input("Enter device model: ").strip()
            if device_id and model:
                await test_specific_device(api_key, device_id, model)
    else:
        print("\n❌ Integration test failed. Please check your setup.")


if __name__ == "__main__":
    asyncio.run(main()) 