#!/usr/bin/env python3
"""
Simple test script to demonstrate rate limiting functionality.
This version doesn't require Home Assistant dependencies.
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the custom_components directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'custom_components'))

# Import only the rate limiter (no Home Assistant dependencies)
from govee_lights.rate_limiter import GoveeRateLimiter


async def test_rate_limiter_directly():
    """Test the rate limiter class directly."""
    
    print("🧪 Testing Govee Rate Limiter")
    print("=" * 50)
    
    # Create rate limiter with test file
    test_file = "test_rate_limit.json"
    rate_limiter = GoveeRateLimiter(test_file)
    
    # Test initial state
    print("📊 Initial State:")
    status = rate_limiter.get_rate_limit_status()
    print(f"   Request Count: {status['request_count']}")
    print(f"   Device Count: {status['device_count']}")
    print(f"   Remaining Requests: {status['remaining_requests']}")
    print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
    print(f"   Can Make Request: {status['can_make_request']}")
    print(f"   Adaptive Polling Interval: {status['adaptive_polling_interval']} seconds")
    
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
    
    # Test rate limit enforcement
    print("\n⚠️  Testing Rate Limit Enforcement:")
    print("   Simulating high request usage...")
    
    # Reset for testing
    rate_limiter.update_device_count(5)
    
    # Simulate high usage
    for i in range(100):
        rate_limiter.increment_request_count()
        if i % 20 == 0:
            status = rate_limiter.get_rate_limit_status()
            can_make = rate_limiter.can_make_request()
            print(f"   Request {i}: {status['usage_percentage']:.1f}% usage, "
                  f"{status['adaptive_polling_interval']}s interval, "
                  f"can make request: {can_make}")
    
    # Show final status
    print("\n📊 Final Rate Limit Status:")
    status = rate_limiter.get_rate_limit_status()
    print(f"   Request Count: {status['request_count']}")
    print(f"   Device Count: {status['device_count']}")
    print(f"   Remaining Requests: {status['remaining_requests']}")
    print(f"   Usage Percentage: {status['usage_percentage']:.1f}%")
    print(f"   Can Make Request: {status['can_make_request']}")
    print(f"   Adaptive Polling Interval: {status['adaptive_polling_interval']} seconds")
    
    # Test daily reset
    print("\n🔄 Testing Daily Reset:")
    print(f"   Current reset date: {status['last_reset_date']}")
    print("   (Daily reset happens automatically at midnight)")
    
    print("\n✅ Rate limiter test completed!")
    print("\n📋 Key Features Demonstrated:")
    print("   ✅ Request counting and daily reset")
    print("   ✅ Adaptive polling based on device count")
    print("   ✅ Usage percentage tracking")
    print("   ✅ Rate limit enforcement")
    print("   ✅ Smart polling interval calculation")
    
    # Clean up test file
    try:
        os.remove(test_file)
        print(f"   🧹 Cleaned up test file: {test_file}")
    except:
        pass


async def test_api_simulation():
    """Simulate API usage patterns."""
    
    print("\n🧪 Testing API Usage Simulation")
    print("=" * 50)
    
    # Create rate limiter
    test_file = "test_api_simulation.json"
    rate_limiter = GoveeRateLimiter(test_file)
    
    # Simulate a typical day with different device counts
    print("📅 Simulating a typical day...")
    
    # Morning: 5 devices active
    print("\n🌅 Morning (5 devices):")
    rate_limiter.update_device_count(5)
    for i in range(50):  # 50 requests in morning
        rate_limiter.increment_request_count()
    status = rate_limiter.get_rate_limit_status()
    print(f"   Requests: {status['request_count']}, Usage: {status['usage_percentage']:.1f}%, "
          f"Interval: {status['adaptive_polling_interval']}s")
    
    # Afternoon: 10 devices active
    print("\n☀️  Afternoon (10 devices):")
    rate_limiter.update_device_count(10)
    for i in range(100):  # 100 requests in afternoon
        rate_limiter.increment_request_count()
    status = rate_limiter.get_rate_limit_status()
    print(f"   Requests: {status['request_count']}, Usage: {status['usage_percentage']:.1f}%, "
          f"Interval: {status['adaptive_polling_interval']}s")
    
    # Evening: 15 devices active
    print("\n🌆 Evening (15 devices):")
    rate_limiter.update_device_count(15)
    for i in range(200):  # 200 requests in evening
        rate_limiter.increment_request_count()
    status = rate_limiter.get_rate_limit_status()
    print(f"   Requests: {status['request_count']}, Usage: {status['usage_percentage']:.1f}%, "
          f"Interval: {status['adaptive_polling_interval']}s")
    
    # Night: 3 devices active
    print("\n🌙 Night (3 devices):")
    rate_limiter.update_device_count(3)
    for i in range(30):  # 30 requests at night
        rate_limiter.increment_request_count()
    status = rate_limiter.get_rate_limit_status()
    print(f"   Requests: {status['request_count']}, Usage: {status['usage_percentage']:.1f}%, "
          f"Interval: {status['adaptive_polling_interval']}s")
    
    print(f"\n📊 End of Day Summary:")
    print(f"   Total Requests: {status['request_count']}")
    print(f"   Usage: {status['usage_percentage']:.1f}%")
    print(f"   Remaining: {status['remaining_requests']}")
    print(f"   Final Polling Interval: {status['adaptive_polling_interval']}s")
    
    # Clean up
    try:
        os.remove(test_file)
    except:
        pass


async def main():
    """Main test function."""
    print("🧪 Govee Rate Limiting Test Suite")
    print("=" * 50)
    
    while True:
        print("\nChoose a test:")
        print("1. Test Rate Limiter Features")
        print("2. Test API Usage Simulation")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await test_rate_limiter_directly()
        elif choice == "2":
            await test_api_simulation()
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-3.")


if __name__ == "__main__":
    asyncio.run(main()) 