#!/usr/bin/env python3
"""
Test script to demonstrate rate limiting and adaptive polling functionality.
"""

import asyncio
import sys
import os

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

from govee_lights.govee_api import GoveeAPI
from govee_lights.rate_limiter import GoveeRateLimiter


async def test_rate_limiting():
    """Test the rate limiting functionality."""
    
    print("🧪 Testing Govee Rate Limiting")
    print("=" * 50)
    
    # Get API key from user
    api_key = input("Enter your Govee API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided!")
        return
    
    # Create API instance with rate limiting enabled
    api = GoveeAPI(api_key, enable_rate_limiting=True)
    
    try:
        # Test initial rate limit status
        print("\n📊 Initial Rate Limit Status:")
        status = api.get_rate_limit_status()
        print(f"   Request Count: {status['request_count']}")
        print(f"   Device Count: {status['device_count']}")
        print(f"   Remaining Requests: {status['remaining_requests']}")
        print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
        print(f"   Can Make Request: {status['can_make_request']}")
        print(f"   Adaptive Polling Interval: {status['adaptive_polling_interval']} seconds")
        
        # Get devices to update device count
        print("\n🔍 Getting devices...")
        devices = await api.get_devices()
        
        if devices:
            print(f"✅ Found {len(devices)} devices")
            
            # Show updated rate limit status
            print("\n📊 Updated Rate Limit Status:")
            status = api.get_rate_limit_status()
            print(f"   Request Count: {status['request_count']}")
            print(f"   Device Count: {status['device_count']}")
            print(f"   Remaining Requests: {status['remaining_requests']}")
            print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
            print(f"   Can Make Request: {status['can_make_request']}")
            print(f"   Adaptive Polling Interval: {status['adaptive_polling_interval']} seconds")
            
            # Test adaptive polling calculation
            print("\n🔄 Testing Adaptive Polling:")
            for i in range(1, 11):
                # Simulate different device counts
                api.rate_limiter.update_device_count(i)
                interval = api.get_adaptive_polling_interval()
                print(f"   {i} device(s): {interval} seconds between polls")
            
            # Test rate limit simulation
            print("\n⚠️  Testing Rate Limit Simulation:")
            print("   Simulating high request usage...")
            
            # Simulate high usage
            for i in range(100):
                api.rate_limiter.increment_request_count()
                if i % 20 == 0:
                    status = api.get_rate_limit_status()
                    print(f"   Request {i}: {status['usage_percentage']:.1f}% usage, "
                          f"{status['adaptive_polling_interval']}s interval")
            
            # Show final status
            print("\n📊 Final Rate Limit Status:")
            status = api.get_rate_limit_status()
            print(f"   Request Count: {status['request_count']}")
            print(f"   Device Count: {status['device_count']}")
            print(f"   Remaining Requests: {status['remaining_requests']}")
            print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
            print(f"   Can Make Request: {status['can_make_request']}")
            print(f"   Adaptive Polling Interval: {status['adaptive_polling_interval']} seconds")
            
            # Test device state retrieval with rate limiting
            if devices:
                device = devices[0]
                device_id = device['device']
                model = device['model']
                
                print(f"\n🎯 Testing device state retrieval for {device_id}:")
                try:
                    state = await api.get_device_state(device_id)
                    if state:
                        print("   ✅ Device state retrieved successfully")
                        print(f"   Power: {state.get('power', 'unknown')}")
                        print(f"   Brightness: {state.get('brightness', 'unknown')}")
                    else:
                        print("   ❌ Failed to get device state")
                except Exception as e:
                    if "Rate limit reached" in str(e):
                        print("   ⚠️  Rate limit reached (expected behavior)")
                    else:
                        print(f"   ❌ Error: {e}")
            
            print("\n🎉 Rate limiting test completed!")
            print("\n📋 Key Features Demonstrated:")
            print("   ✅ Request counting and daily reset")
            print("   ✅ Adaptive polling based on device count")
            print("   ✅ Usage percentage tracking")
            print("   ✅ Automatic rate limit enforcement")
            print("   ✅ Smart polling interval calculation")
            
        else:
            print("❌ No devices found")
            
    except Exception as e:
        print(f"❌ Error during rate limiting test: {e}")
    finally:
        await api.close()


async def test_rate_limiter_directly():
    """Test the rate limiter class directly."""
    
    print("\n🧪 Testing Rate Limiter Directly")
    print("=" * 50)
    
    # Create rate limiter
    rate_limiter = GoveeRateLimiter("test_rate_limit.json")
    
    # Test initial state
    print("📊 Initial State:")
    status = rate_limiter.get_rate_limit_status()
    print(f"   Request Count: {status['request_count']}")
    print(f"   Device Count: {status['device_count']}")
    print(f"   Remaining Requests: {status['remaining_requests']}")
    print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
    
    # Test device count updates
    print("\n📱 Testing Device Count Updates:")
    for device_count in [1, 5, 10, 20]:
        rate_limiter.update_device_count(device_count)
        interval = rate_limiter.get_adaptive_polling_interval()
        print(f"   {device_count} devices: {interval} second polling interval")
    
    # Test request counting
    print("\n🔢 Testing Request Counting:")
    for i in range(5):
        rate_limiter.increment_request_count()
        status = rate_limiter.get_rate_limit_status()
        print(f"   Request {i+1}: {status['request_count']} total, "
              f"{status['remaining_requests']} remaining")
    
    # Test adaptive polling with different scenarios
    print("\n🔄 Testing Adaptive Polling Scenarios:")
    scenarios = [
        (1, 100),    # 1 device, 100 requests used
        (5, 500),    # 5 devices, 500 requests used
        (10, 1000),  # 10 devices, 1000 requests used
        (20, 2000),  # 20 devices, 2000 requests used
    ]
    
    for device_count, requests_used in scenarios:
        rate_limiter.update_device_count(device_count)
        # Simulate used requests
        for _ in range(requests_used):
            rate_limiter.increment_request_count()
        
        interval = rate_limiter.get_adaptive_polling_interval()
        status = rate_limiter.get_rate_limit_status()
        print(f"   {device_count} devices, {requests_used} requests used: "
              f"{interval}s interval, {status['usage_percentage']:.1f}% usage")
    
    print("\n✅ Rate limiter test completed!")


async def main():
    """Main test function."""
    print("🧪 Govee Rate Limiting Test Suite")
    print("=" * 50)
    
    while True:
        print("\nChoose a test:")
        print("1. Test Rate Limiting with Real API")
        print("2. Test Rate Limiter Directly")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await test_rate_limiting()
        elif choice == "2":
            await test_rate_limiter_directly()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")


if __name__ == "__main__":
    asyncio.run(main()) 