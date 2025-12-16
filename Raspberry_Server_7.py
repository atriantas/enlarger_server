#!/usr/bin/env python3
"""
Darkroom Timer Relay Server for Raspberry Pi
Controls 4 relays on GPIO pins 25, 17, 27, 22
Lightweight Flask server optimized for timing accuracy
"""

from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
import time
import threading
import logging
import atexit
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GPIO Pin Configuration
RELAY_PINS = {
    25: {"name": "Enlarger Timer", "state": False},
    17: {"name": "Safelight", "state": False},
    27: {"name": "Ventilation", "state": False},
    22: {"name": "White Light", "state": False}
}

# Active timer threads
active_timers = {}

app = Flask(__name__)

def setup_gpio():
    """Initialize GPIO pins"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in RELAY_PINS.keys():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Relay OFF (HIGH state for active-low relays)
        RELAY_PINS[pin]["state"] = False
        logger.info(f"Initialized GPIO {pin} as OUTPUT (OFF)")
    
    logger.info("GPIO setup complete")

def cleanup_gpio():
    """Cleanup GPIO on exit"""
    logger.info("Cleaning up GPIO...")
    
    # Turn off all relays
    for pin in RELAY_PINS.keys():
        GPIO.output(pin, GPIO.HIGH)
    
    GPIO.cleanup()
    logger.info("GPIO cleanup complete")

def set_relay_state(pin, state):
    """Set relay state (True=ON, False=OFF)"""
    try:
        # Most relays are active-low: HIGH=OFF, LOW=ON
        gpio_state = GPIO.LOW if state else GPIO.HIGH
        GPIO.output(pin, gpio_state)
        RELAY_PINS[pin]["state"] = state
        logger.info(f"GPIO {pin} ({RELAY_PINS[pin]['name']}): {'ON' if state else 'OFF'}")
        return True
    except Exception as e:
        logger.error(f"Error setting relay {pin}: {e}")
        return False

def timer_thread(pin, duration):
    """Thread function for timed relay activation"""
    thread_id = f"timer_{pin}_{datetime.now().timestamp()}"
    active_timers[thread_id] = {"pin": pin, "running": True}
    
    try:
        logger.info(f"Timer started: GPIO {pin} for {duration}s")
        
        # Turn relay ON
        set_relay_state(pin, True)
        
        # Wait for duration
        time.sleep(duration)
        
        # Turn relay OFF
        set_relay_state(pin, False)
        
        logger.info(f"Timer completed: GPIO {pin}")
        
    except Exception as e:
        logger.error(f"Timer error on GPIO {pin}: {e}")
    finally:
        # Clean up thread reference
        if thread_id in active_timers:
            del active_timers[thread_id]

def start_timer(pin, duration):
    """Start a timer thread for relay activation"""
    # Cancel any existing timer for this pin
    stop_timer(pin)
    
    # Start new timer thread
    thread = threading.Thread(
        target=timer_thread,
        args=(pin, duration),
        daemon=True
    )
    thread.start()
    
    return True

def stop_timer(pin):
    """Stop any active timer for the given pin"""
    threads_to_stop = []
    
    for thread_id, timer_info in list(active_timers.items()):
        if timer_info["pin"] == pin and timer_info["running"]:
            timer_info["running"] = False
            threads_to_stop.append(thread_id)
    
    for thread_id in threads_to_stop:
        if thread_id in active_timers:
            # Turn off the relay immediately
            set_relay_state(pin, False)
            del active_timers[thread_id]
            logger.info(f"Stopped timer for GPIO {pin}")
    
    return len(threads_to_stop) > 0

@app.route('/')
def index():
    """Root endpoint - server info"""
    status = {
        "server": "Darkroom Timer Relay Server",
        "version": "1.0",
        "status": "running",
        "gpio_pins": list(RELAY_PINS.keys()),
        "current_states": {pin: RELAY_PINS[pin]["state"] for pin in RELAY_PINS},
        "active_timers": len(active_timers)
    }
    return jsonify(status)

@app.route('/ping')
def ping():
    """Simple ping endpoint for connection testing"""
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/relay', methods=['GET'])
def control_relay():
    """Control relay state (ON/OFF)"""
    try:
        gpio = int(request.args.get('gpio', 14))
        state = request.args.get('state', 'off').lower()
        
        if gpio not in RELAY_PINS:
            return jsonify({"error": f"Invalid GPIO pin: {gpio}"}), 400
        
        # Set relay state
        if state == 'on':
            success = set_relay_state(gpio, True)
        elif state == 'off':
            success = set_relay_state(gpio, False)
            # Also stop any timer for this pin
            stop_timer(gpio)
        else:
            return jsonify({"error": "State must be 'on' or 'off'"}), 400
        
        if success:
            return jsonify({
                "status": "success",
                "gpio": gpio,
                "state": state,
                "name": RELAY_PINS[gpio]["name"]
            })
        else:
            return jsonify({"error": "Failed to set relay state"}), 500
            
    except ValueError:
        return jsonify({"error": "Invalid GPIO parameter"}), 400
    except Exception as e:
        logger.error(f"Error in relay control: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/timer', methods=['GET'])
def timer_endpoint():
    """Trigger timer relay with duration parameter"""
    try:
        gpio = int(request.args.get('gpio', 14))
        duration = float(request.args.get('duration', 1.0))
        
        if gpio not in RELAY_PINS:
            return jsonify({"error": f"Invalid GPIO pin: {gpio}"}), 400
        
        if duration <= 0:
            return jsonify({"error": "Duration must be positive"}), 400
        
        if duration > 3600:  # 1 hour max
            return jsonify({"error": "Duration too long (max 3600s)"}), 400
        
        # Start timer
        success = start_timer(gpio, duration)
        
        if success:
            return jsonify({
                "status": "success",
                "gpio": gpio,
                "duration": duration,
                "message": f"Timer started for {duration}s"
            })
        else:
            return jsonify({"error": "Failed to start timer"}), 500
            
    except ValueError:
        return jsonify({"error": "Invalid parameters"}), 400
    except Exception as e:
        logger.error(f"Error in timer endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get current status of all relays"""
    states = {}
    for pin in RELAY_PINS:
        states[pin] = {
            "name": RELAY_PINS[pin]["name"],
            "state": RELAY_PINS[pin]["state"]
        }
    
    return jsonify({
        "status": "success",
        "relays": states,
        "active_timers": len(active_timers)
    })

@app.route('/all', methods=['GET'])
def control_all():
    """Control all relays at once"""
    try:
        state = request.args.get('state', 'off').lower()
        
        if state not in ['on', 'off']:
            return jsonify({"error": "State must be 'on' or 'off'"}), 400
        
        results = {}
        for pin in RELAY_PINS:
            if state == 'on':
                set_relay_state(pin, True)
            else:
                set_relay_state(pin, False)
                stop_timer(pin)
            results[pin] = RELAY_PINS[pin]["state"]
        
        return jsonify({
            "status": "success",
            "state": state,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Error controlling all relays: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        # Setup GPIO
        setup_gpio()
        
        # Register cleanup function
        atexit.register(cleanup_gpio)
        
        # Get network info
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        logger.info("=" * 50)
        logger.info("Darkroom Timer Relay Server Starting...")
        logger.info(f"Host: {hostname}")
        logger.info(f"Local IP: {local_ip}")
        logger.info("GPIO Pins configured:")
        for pin, info in RELAY_PINS.items():
            logger.info(f"  GPIO {pin}: {info['name']}")
        logger.info("=" * 50)
        
        # Run Flask server
        # Use threaded=True for better performance
        # Use port 5000 (default) or specify with --port argument
        import sys
        port = 5000
        if len(sys.argv) > 1:
            try:
                port = int(sys.argv[1])
            except ValueError:
                pass
        
        logger.info(f"Server starting on http://{local_ip}:{port}")
        logger.info("Endpoints:")
        logger.info("  GET /ping - Test connection")
        logger.info("  GET /relay?gpio=14&state=on - Control relay")
        logger.info("  GET /timer?gpio=14&duration=5.0 - Timer relay")
        logger.info("  GET /status - Get all relay states")
        logger.info("  GET /all?state=on - Control all relays")
        
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            threaded=True,
            debug=False  # Set to False for production
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        cleanup_gpio()
