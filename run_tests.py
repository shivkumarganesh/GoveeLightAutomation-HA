#!/usr/bin/env python3
"""
Test runner for Govee Lights Integration.
Choose from different testing options.
"""

import asyncio
import sys
import os

def print_menu():
    """Print the test menu."""
    print("\n🧪 Govee Light Automation Test Suite")
    print("=" * 50)
    print("Choose a test option:")
    print("1. Quick API Key Test (Basic connectivity)")
    print("2. Full Integration Test (Uses actual integration code)")
    print("3. Run Unit Tests (pytest)")
    print("4. Exit")
    print("-" * 50)

async def run_quick_test():
    """Run the quick API test."""
    print("\n🚀 Running Quick API Test...")
    from test_api_key import main as quick_test_main
    await quick_test_main()

async def run_integration_test():
    """Run the full integration test."""
    print("\n🔧 Running Full Integration Test...")
    from test_integration import main as integration_test_main
    await integration_test_main()

def run_unit_tests():
    """Run the unit tests."""
    print("\n🧪 Running Unit Tests...")
    import subprocess
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running unit tests: {e}")
        return False

async def main():
    """Main test runner."""
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == "1":
                await run_quick_test()
            elif choice == "2":
                await run_integration_test()
            elif choice == "3":
                success = run_unit_tests()
                if success:
                    print("✅ Unit tests passed!")
                else:
                    print("❌ Unit tests failed!")
            elif choice == "4":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 