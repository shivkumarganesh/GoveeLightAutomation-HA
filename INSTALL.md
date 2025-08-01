# Installation Guide for Govee Lights Integration

## 🧪 Testing Your API Key

Before installing in Home Assistant, test your API key to ensure everything works:

### Option 1: Quick Test (Recommended First Step)
```bash
python test_api_key.py
```

### Option 2: Full Integration Test
```bash
python test_integration.py
```

### Option 3: Interactive Test Suite
```bash
python run_tests.py
```

## 📋 Prerequisites

1. **Get Your Govee API Key**:
   - Go to [Govee Developer Portal](https://developer.govee.com/)
   - Create an account or sign in
   - Create a new application
   - Copy your API key

2. **Ensure Your Devices Are Ready**:
   - Your Govee lights are connected to the internet
   - Devices are registered in the Govee app
   - Devices are online and controllable

## 🚀 Installation Steps

### Step 1: Test Your API Key
```bash
cd /path/to/home-assistant-govee-integration
python test_api_key.py
```

Enter your API key when prompted. You should see your devices listed.

### Step 2: Install in Home Assistant

#### Method A: Manual Installation
1. Copy the `custom_components/govee_lights` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings** → **Devices & Services** → **Integrations**
4. Click **+ Add Integration**
5. Search for "Govee Lights"
6. Enter your API key in the setup wizard

#### Method B: HACS Installation (if you have HACS)
1. Install HACS if you haven't already
2. Add this repository as a custom repository in HACS
3. Install the integration through HACS
4. Follow the setup wizard

### Step 3: Verify Installation
1. Check that your devices appear in Home Assistant
2. Test basic functionality (turn on/off, change color, adjust brightness)
3. Check the Home Assistant logs for any errors

## 🔧 Troubleshooting

### No Devices Found
- Verify your API key is correct
- Ensure your devices are connected to the internet
- Check that devices are registered in the Govee app

### Lights Not Responding
- Check your internet connection
- Verify devices are online in the Govee app
- Try restarting Home Assistant
- Check Home Assistant logs for errors

### API Rate Limits
- Reduce the scan interval in integration settings
- Don't make too many rapid changes

## 📊 Testing Results

When you run the tests, you should see output like:

```
🧪 Govee API Key Test
==================================================
🔑 Testing API key: abc12345...
🌐 Testing URL: https://developer-api.govee.com/v1/devices
--------------------------------------------------
📡 Response Status: 200
✅ API Key is valid!
📊 Response Code: 200
💡 Found 3 devices:
  1. Living Room Light
     Device ID: abc123def456
     Model: H6003
     Controllable: True
     Retrievable: True
```

## 🎯 Next Steps

After successful testing:
1. Install the integration in Home Assistant
2. Configure your devices
3. Create automations and scenes
4. Enjoy controlling your Govee lights from Home Assistant!

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Home Assistant logs
3. Test your API key using the provided test scripts
4. Open an issue on GitHub with detailed information 

## ✅ New API Calls Tracking Sensor Added Successfully!

I've successfully added a comprehensive API calls tracking sensor that provides detailed information about your Govee API usage. Here's what was implemented:

### **New Sensor: "Govee API Calls"**

**Main Value**: Total number of API calls made today

**Rich Attributes for Dashboard**:
- `total_calls_today`: Number of API calls made today
- `remaining_calls`: Estimated remaining calls (local tracking)
- `usage_percentage`: Current usage percentage
- `daily_limit`: Maximum daily limit (10,000)
- `device_count`: Number of active devices
- `adaptive_polling_interval`: Current polling interval in seconds
- `last_reset_date`: Date when counters were last reset
- `rate_limit_status`: Status (Normal/Warning/Critical)
- `api_remaining_calls`: **Real-time remaining calls from Govee API headers**
- `api_reset_time`: **When the rate limit will reset (from API headers)**
- `last_api_call_time`: **Timestamp of the last API call**

### **Enhanced Features:**

1. **Real-time API Header Parsing**: 
   - Captures `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers
   - Converts timestamps to human-readable format
   - Stores last API call information

2. **Improved Error Handling**:
   - Specific handling for 429 (rate limit exceeded) errors
   - Detailed error messages with remaining calls and reset time
   - Graceful fallback for missing headers

3. **Smart Status Calculation**:
   - **Normal**: < 80% usage
   - **Warning**: 80-95% usage  
   - **Critical**: > 95% usage

### **Dashboard Integration:**

Users can now add this sensor to their Home Assistant dashboard to:
- Monitor API usage in real-time
- See when rate limits will reset
- Get alerts when approaching limits
- Track device count and polling intervals
- View detailed usage statistics

### **Example Dashboard Card:**

```yaml
type: entities
entities:
  - entity: sensor.govee_api_calls
    name: API Usage
  - entity: sensor.govee_api_rate_limit
    name: Rate Limit %
  - entity: sensor.govee_device_count
    name: Device Count
title: Govee API Monitoring
```

The sensor automatically updates every 5 minutes and provides comprehensive monitoring of your Govee API usage, making it easy to track and manage your daily request limits! 

## **New Entities You'll See:**

### **1. Govee API Calls Sensor**
- **Main Value**: Shows total calls made today (e.g., "1,247 calls")
- **Key Attributes**:
  - `api_remaining_calls`: Real-time remaining calls from Govee API
  - `api_reset_time`: When the rate limit resets (e.g., "2025-08-02 01:15:02 UTC")
  - `rate_limit_status`: "Normal", "Warning", or "Critical"
  - `usage_percentage`: Current usage (e.g., "12.47%")

### **2. Govee API Rate Limit Sensor**
- **Main Value**: Usage percentage (e.g., "12.47%")
- **Shows**: How much of your daily limit you've used

### **3. Govee Device Count Sensor**
- **Main Value**: Number of devices (e.g., "5")
- **Shows**: How many Govee devices are connected

### **4. Govee Polling Interval Sensor**
- **Main Value**: Current polling interval in seconds (e.g., "120")
- **Shows**: How often the integration polls for updates

## **What You'll See in Home Assistant:**

### **In Devices & Services:**
```
Govee Light Automation
├── Govee API Calls (1,247 calls)
├── Govee API Rate Limit (12.47%)
├── Govee Device Count (5)
└── Govee Polling Interval (120 seconds)
```

### **In Your Dashboard:**
You can add these sensors to see real-time monitoring:

**Example Dashboard Card:**
```yaml
type: entities
entities:
  - entity: sensor.govee_api_calls
    name: "API Calls Today"
  - entity: sensor.govee_api_rate_limit  
    name: "Usage %"
  - entity: sensor.govee_device_count
    name: "Devices"
title: "Govee API Monitoring"
```

## **Even If You're Bypassing Rate Limits:**

1. **You'll still see the real API usage** from Govee's headers
2. **You'll know exactly when limits reset** (useful for planning)
3. **You can monitor your actual usage** vs. your bypassed limits
4. **You'll get alerts** if you approach the real limits
5. **You can track device count** and polling intervals

## **Benefits for You:**

- **Real-time monitoring**: See exactly how many calls you're making
- **Reset timing**: Know when the daily counter resets
- **Usage tracking**: Monitor your actual vs. bypassed usage
- **Device management**: See how many devices are active
- **Performance monitoring**: Track polling intervals

## **Example Dashboard View:**
```
📊 Govee API Monitoring
├──  API Calls Today: 1,247 calls
├── 📈 Usage: 12.47%
├── 💡 Devices: 5
├── ⏱️ Polling: 120 seconds
├── 🕐 Reset Time: 2025-08-02 01:15:02 UTC
└── ✅ Status: Normal
```

## **During Setup Process:**

### **If Rate Limit is Hit During Setup:**

**Error Message Example:**
```
❌ Setup Failed: Rate limit exceeded

📊 Current Status:
- API Calls Used: 10,000/10,000
- Remaining Calls: 0
- Usage: 100%

🕐 Rate Limit Reset Time: 2025-08-02 01:15:02 UTC
⏰ You can try again at: 2025-08-02 01:15:02 UTC

💡 What to do:
1. Wait until the reset time above
2. Try the setup process again
3. The integration will work normally after reset
```

### **Enhanced Error Handling:**

The setup process would:
1. **Parse the `X-RateLimit-Reset` header** from the API response
2. **Convert the timestamp** to a human-readable format
3. **Show both UTC and local time** (if possible)
4. **Provide clear instructions** on what to do next

### **User Experience:**

Instead of just seeing "Invalid API key" or "Rate limit exceeded", they'd see:
- **Exact reset time** in their timezone
- **Current usage statistics**
- **Clear next steps**
- **No confusion** about whether their API key is wrong

### **Example Error Flow:**
```
🧪 Testing API Key...
📡 Response Status: 429
📊 Rate Limit Remaining: 0
🕐 Rate Limit Resets At: 2025-08-02 01:15:02 UTC

❌ Setup cannot continue - Rate limit exceeded

⏰ You can try again at: 2025-08-02 01:15:02 UTC
 That's in: 2 hours 15 minutes

💡 Your API key is valid, but you've hit the daily limit.
   The integration will work perfectly once the limit resets.
```