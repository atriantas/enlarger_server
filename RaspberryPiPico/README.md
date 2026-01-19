# Darkroom Timer - Raspberry Pi Pico 2 W

Professional darkroom timer system running on Raspberry Pi Pico 2 W with MicroPython v1.27.0.

## Features

- **WiFi Hotspot Mode (AP)**: Connect directly to the Pico at `192.168.4.1`
- **WiFi Station Mode (STA)**: Connect to your router for mDNS access at `darkroom.local`
- **4-Channel Relay Control**: Enlarger, Safelight, Ventilation, White Light
- **Active-LOW Relay Logic**: Compatible with standard relay modules
- **Async Architecture**: Non-blocking HTTP server and timer management
- **Chunked File Serving**: 512-byte chunks for memory-efficient HTML delivery
- **Safelight Auto-Off**: Automatically turns off safelight during exposures

## Hardware Requirements

- Raspberry Pi Pico 2 W
- 4-Channel Relay Module (Active-LOW)
- USB Power Supply (5V)

## GPIO Pin Mapping

| Relay | GPIO Pin | Function       |
| ----- | -------- | -------------- |
| 1     | GP14     | Enlarger Timer |
| 2     | GP15     | Safelight      |
| 3     | GP16     | Ventilation    |
| 4     | GP17     | White Light    |

## File Structure

```
RaspberryPiPico/
├── boot.py              # Main entry point
├── index.html           # Web client (served via HTTP)
├── README.md            # This file
└── lib/
    ├── gpio_control.py  # Relay control module
    ├── http_server.py   # Async HTTP server
    ├── timer_manager.py # Async timer management
    ├── wifi_ap.py       # WiFi hotspot (with mDNS hostname)
    └── wifi_sta.py      # WiFi station (with mDNS hostname)
```

**Note**: mDNS is handled natively by MicroPython v1.27.0 via `network.hostname()` - no custom module needed.

## Installation

### 1. Flash MicroPython Firmware

1. Download MicroPython v1.27.0 for Pico 2 W from [micropython.org](https://micropython.org/download/rp2w/)
2. Hold the BOOTSEL button on the Pico 2 W
3. Connect USB to your computer
4. Release BOOTSEL button
5. Copy the UF2 file to the mounted RPI-RP2 drive
6. Pico will reboot with MicroPython

### 2. Deploy Files

Using **Thonny IDE** (recommended):

1. Open Thonny and connect to the Pico 2 W
2. Copy all files maintaining the folder structure
3. Save to the Pico's root folder

Using **ampy** (command line):

```bash
# Install ampy
pip3 install adafruit-ampy

# Set port (Linux/Mac)
export AMPY_PORT=/dev/ttyACM0

# Create lib directory
ampy mkdir lib

# Upload files
ampy put boot.py
ampy put index.html
ampy put lib/gpio_control.py lib/gpio_control.py
ampy put lib/http_server.py lib/http_server.py
ampy put lib/timer_manager.py lib/timer_manager.py
ampy put lib/wifi_ap.py lib/wifi_ap.py
ampy put lib/wifi_sta.py lib/wifi_sta.py
```

### 3. Verify Installation

1. Disconnect and reconnect USB power
2. Monitor console output (Thonny or `screen /dev/ttyACM0 115200`)
3. Look for: `✅ SYSTEM READY`
4. Note the WiFi credentials displayed

## Usage

### First Boot (AP Mode)

1. Power on the Pico 2 W
2. Connect your phone/tablet to WiFi network:
   - **SSID**: `DarkroomTimer`
   - **Password**: `darkroom123`
3. Open browser to: `http://192.168.4.1/`

### Connecting to Your Router

1. Go to the **CONTROL** tab in the web interface
2. Under **WiFi Configuration**:
   - Enter your router's SSID
   - Enter your router's password
3. Click **Connect to WiFi**
4. Once connected, the Pico will be accessible at:
   - `http://darkroom.local/` (via mDNS)
   - `http://<assigned-ip>/` (direct IP)

**Note**: The AP hotspot remains active for 5 seconds after STA connects, then shuts down.

## API Endpoints

| Endpoint       | Method | Description                     |
| -------------- | ------ | ------------------------------- |
| `/`            | GET    | Redirect to /index.html         |
| `/index.html`  | GET    | Serve web client                |
| `/ping`        | GET    | Connection test                 |
| `/relay`       | GET    | Control relay (gpio, state)     |
| `/timer`       | GET    | Timed relay (gpio, duration)    |
| `/status`      | GET    | Get all relay states            |
| `/all`         | GET    | Control all relays              |
| `/wifi-config` | GET    | Configure WiFi (ssid, password) |
| `/wifi-status` | GET    | Get WiFi connection status      |

### Example API Calls

```bash
# Test connection
curl http://192.168.4.1/ping

# Turn on enlarger
curl "http://192.168.4.1/relay?gpio=14&state=on"

# Start 10 second timer
curl "http://192.168.4.1/timer?gpio=14&duration=10.0"

# Get all relay states
curl http://192.168.4.1/status

# Configure WiFi
curl "http://192.168.4.1/wifi-config?ssid=MyNetwork&password=mypassword"
```

## Timer Synchronization

The timer uses a **scheduled start timestamp** for synchronization:

1. Client requests timer: `/timer?gpio=14&duration=10.5`
2. Server responds with `start_at` timestamp (current time + 150ms)
3. Client schedules countdown to start at the same timestamp
4. Both client and server begin counting simultaneously

## Configuration

Edit `boot.py` to change default settings:

```python
# WiFi AP settings (lines 27-29)
WIFI_SSID = "DarkroomTimer"
WIFI_PASSWORD = "darkroom123"
HTTP_PORT = 80
```

WiFi credentials are saved to `wifi_config.json` after successful connection.

## Troubleshooting

### Cannot Connect to AP

- Ensure MicroPython is properly flashed
- Check console output for errors
- Verify the Pico's onboard LED is on

### HTML Page Won't Load

- Wait 5-10 seconds after boot for initialization
- The HTML file is large (~610KB) and may take time to serve
- Refresh the page if it times out

### WiFi Connection Fails

- Verify SSID and password are correct
- Check if router is within range
- Try AP mode first to verify hardware works

### Relays Not Responding

- Verify GPIO connections (GP14, GP15, GP16, GP17)
- Check relay module power supply
- Relays are active-LOW: 0 = ON, 1 = OFF

### mDNS Not Working

- Ensure device is on the same network as the router
- Try direct IP access instead
- mDNS may take 30 seconds to propagate
- mDNS is set via `network.hostname("darkroom")` BEFORE WiFi activation
- Both AP and STA modes use the same hostname

## Differences from Raspberry Pi Version

| Feature         | Raspberry Pi      | Pico 2 W                      |
| --------------- | ----------------- | ----------------------------- |
| Server          | Flask (threading) | Socket (asyncio)              |
| WiFi            | Client on network | Hotspot + Station             |
| GPIO Pins       | BCM 25,17,27,22   | GP 14,15,16,17                |
| Default Port    | 5000              | 80                            |
| Default IP      | DHCP              | 192.168.4.1 (AP)              |
| mDNS            | Avahi (system)    | Native via network.hostname() |
| Shutdown/Reboot | API endpoints     | Not available                 |

## License

MIT License - See main repository for details.

## Contributing

This is part of the Darkroom Timer project. See the main repository for contribution guidelines.
