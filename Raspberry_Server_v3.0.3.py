#!/usr/bin/env python3
"""
Darkroom Timer Relay Server for Raspberry Pi
Controls 4 relays on GPIO pins 25, 17, 27, 22
Lightweight Flask server with CORS support for cross-browser compatibility
"""

from flask import Flask, request, jsonify, send_file, make_response
import RPi.GPIO as GPIO
import time
import threading
import logging
import atexit
from datetime import datetime
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# GPIO Pin Configuration - Updated to match HTML mapping
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
    """
    Initialize GPIO pins for relay control.
    
    Sets up all configured GPIO pins as outputs and initializes them to HIGH (OFF state)
    for active-low relay modules. Logs each pin initialization.
    
    Returns:
        None
        
    Raises:
        Exception: If GPIO setup fails
        
    Example:
        setup_gpio()  # Initialize all relay pins
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for pin in RELAY_PINS.keys():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Relay OFF (HIGH state for active-low relays)
        RELAY_PINS[pin]["state"] = False
        logger.info(f"Initialized GPIO {pin} as OUTPUT (OFF)")
    
    logger.info("GPIO setup complete")

def cleanup_gpio():
    """
    Cleanup GPIO on exit.
    
    Turns off all relays and performs GPIO cleanup to ensure safe shutdown.
    Called automatically on program exit via atexit.register().
    
    Returns:
        None
        
    Example:
        cleanup_gpio()  # Safe shutdown of GPIO
    """
    logger.info("Cleaning up GPIO...")
    
    # Turn off all relays
    for pin in RELAY_PINS.keys():
        GPIO.output(pin, GPIO.HIGH)
    
    GPIO.cleanup()
    logger.info("GPIO cleanup complete")

def set_relay_state(pin, state):
    """
    Set relay state (True=ON, False=OFF).
    
    Handles active-low relay logic: GPIO.LOW = ON, GPIO.HIGH = OFF.
    Updates RELAY_PINS state dictionary and logs the action.
    
    Args:
        pin (int): GPIO pin number to control
        state (bool): True to turn relay ON, False to turn relay OFF
        
    Returns:
        bool: True if successful, False if error occurred
        
    Example:
        set_relay_state(25, True)  # Turn on enlarger relay
        set_relay_state(17, False) # Turn off safelight relay
    """
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
    """
    Thread function for timed relay activation.
    
    Runs as a daemon thread to provide non-blocking timer functionality.
    Turns relay ON, waits for specified duration, then turns relay OFF.
    Automatically cleans up thread reference on completion.
    
    Args:
        pin (int): GPIO pin number to control
        duration (float): Duration in seconds to keep relay ON
        
    Returns:
        None
        
    Example:
        timer_thread(25, 5.5)  # Turn on GPIO 25 for 5.5 seconds
    """
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
    """
    Start a timer thread for relay activation.
    
    Cancels any existing timer for the pin, then starts a new daemon thread
    for timed relay control. Non-blocking operation.
    
    Args:
        pin (int): GPIO pin number to control
        duration (float): Duration in seconds for relay activation
        
    Returns:
        bool: Always returns True
        
    Example:
        start_timer(25, 10.5)  # Start 10.5s timer on enlarger
    """
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
    """
    Stop any active timer for the given pin.
    
    Searches for active timers on the specified pin and stops them immediately.
    Turns off the relay and removes timer from active_timers dictionary.
    
    Args:
        pin (int): GPIO pin number to stop timer for
        
    Returns:
        bool: True if any timer was stopped, False if no timer found
        
    Example:
        stop_timer(25)  # Stop any timer on enlarger
    """
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

# ===== CORS MIDDLEWARE =====
@app.after_request
def after_request(response):
    """
    Add CORS headers to all responses.
    
    Enables cross-origin requests from any domain for browser compatibility.
    Configured to allow all standard HTTP methods and headers.
    
    Args:
        response (Response): Flask response object
        
    Returns:
        Response: Modified response with CORS headers
        
    Example:
        Automatically applied to all Flask routes
    """
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    response.headers.add('Access-Control-Max-Age', '86400')  # 24 hours
    return response

@app.route('/')
def index():
    """
    Root endpoint - serves HTML interface or returns server info.
    
    If Darkroom_Tools_v3.0.3.html exists in the same directory, serves it.
    Otherwise returns JSON with server status and available endpoints.
    
    Returns:
        Response: HTML file or JSON server info
        
    Example:
        GET /  # Serves HTML or returns server info
    """
    # Check if HTML file exists in same directory
    html_file = 'Darkroom_Tools_v3.0.3.html'
    if os.path.exists(html_file):
        logger.info(f"Serving HTML file: {html_file}")
        return send_file(html_file)
    
    # Otherwise return server info
    status = {
        "server": "Darkroom Timer Relay Server",
        "version": "2.0",
        "status": "running",
        "gpio_pins": {pin: RELAY_PINS[pin]["name"] for pin in RELAY_PINS},
        "current_states": {pin: RELAY_PINS[pin]["state"] for pin in RELAY_PINS},
        "active_timers": len(active_timers),
        "cors_enabled": True,
        "endpoints": {
            "/": "This info",
            "/ping": "Test connection",
            "/relay?gpio=25&state=on": "Control relay",
            "/timer?gpio=25&duration=5.0": "Timer relay",
            "/status": "Get all relay states",
            "/all?state=on": "Control all relays"
        }
    }
    return jsonify(status)

@app.route('/ping')
def ping():
    """
    Simple ping endpoint for connection testing.
    
    Returns a simple status response to verify server connectivity.
    
    Returns:
        JSON: Status object with timestamp
        
    Example:
        GET /ping  # Returns {"status": "ok", ...}
    """
    return jsonify({
        "status": "ok", 
        "message": "Server is running",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/relay', methods=['GET', 'OPTIONS'])
def control_relay():
    """
    Control relay state (ON/OFF).
    
    Query parameters:
        gpio (int): GPIO pin number (default: 25)
        state (str): 'on' or 'off' (default: 'off')
    
    Returns:
        JSON: Success response with relay info or error
        
    Example:
        GET /relay?gpio=25&state=on  # Turn on enlarger
        GET /relay?gpio=17&state=off # Turn off safelight
    """
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        gpio = int(request.args.get('gpio', 25))  # Default to GPIO 25 for enlarger
        state = request.args.get('state', 'off').lower()
        
        if gpio not in RELAY_PINS:
            return jsonify({"error": f"Invalid GPIO pin: {gpio}. Valid pins: {list(RELAY_PINS.keys())}"}), 400
        
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
                "name": RELAY_PINS[gpio]["name"],
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to set relay state"}), 500
            
    except ValueError as e:
        return jsonify({"error": f"Invalid parameter: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error in relay control: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/timer', methods=['GET', 'OPTIONS'])
def timer_endpoint():
    """
    Trigger timer relay with duration parameter.
    
    Query parameters:
        gpio (int): GPIO pin number (default: 25)
        duration (float): Duration in seconds (default: 1.0, max: 3600)
    
    Returns:
        JSON: Success response with timer info or error
        
    Example:
        GET /timer?gpio=25&duration=5.5  # 5.5 second exposure
    """
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        gpio = int(request.args.get('gpio', 25))  # Default to GPIO 25 for enlarger
        duration = float(request.args.get('duration', 1.0))
        
        if gpio not in RELAY_PINS:
            return jsonify({"error": f"Invalid GPIO pin: {gpio}. Valid pins: {list(RELAY_PINS.keys())}"}), 400
        
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
                "name": RELAY_PINS[gpio]["name"],
                "message": f"Timer started for {duration}s",
                "timestamp": datetime.now().isoformat()
            })
        else:
            return jsonify({"error": "Failed to start timer"}), 500
            
    except ValueError as e:
        return jsonify({"error": f"Invalid parameters: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error in timer endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """
    Get current status of all relays.
    
    Returns:
        JSON: Status of all relays and active timer count
        
    Example:
        GET /status  # Get all relay states
    """
    states = {}
    for pin in RELAY_PINS:
        states[pin] = {
            "name": RELAY_PINS[pin]["name"],
            "state": RELAY_PINS[pin]["state"]
        }
    
    return jsonify({
        "status": "success",
        "relays": states,
        "active_timers": len(active_timers),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/all', methods=['GET', 'OPTIONS'])
def control_all():
    """
    Control all relays at once.
    
    Query parameters:
        state (str): 'on' or 'off' (default: 'off')
    
    Returns:
        JSON: Success response with all relay states
        
    Example:
        GET /all?state=on   # Turn on all relays
        GET /all?state=off  # Turn off all relays
    """
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
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
            results[pin] = {
                "name": RELAY_PINS[pin]["name"],
                "state": RELAY_PINS[pin]["state"]
            }
        
        return jsonify({
            "status": "success",
            "state": state,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error controlling all relays: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        "server": "Darkroom Relay Server",
        "cors_enabled": True,
        "client_ip": request.remote_addr,
        "user_agent": request.user_agent.string,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/favicon.ico')
def favicon():
    """Return empty favicon to avoid 404 errors"""
    return '', 204

@app.route('/shutdown', methods=['GET', 'OPTIONS'])
def shutdown_pi():
    """
    Gracefully shutdown the Raspberry Pi.
    
    Returns response immediately, then schedules shutdown in 3 seconds
    to allow the HTTP response to be sent.
    
    Returns:
        JSON: Success message with 3-second delay warning
        
    Example:
        GET /shutdown  # Initiate system shutdown
    """
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        logger.info("Shutdown command received from %s", request.remote_addr)
        
        # Return response first, then shutdown
        response = jsonify({
            "status": "success",
            "message": "Raspberry Pi shutting down in 3 seconds...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Schedule shutdown in a separate thread after sending response
        def delayed_shutdown():
            time.sleep(3)  # Wait 3 seconds to allow response to be sent
            logger.info("Initiating system shutdown...")
            os.system("sudo shutdown -h now")
        
        threading.Thread(target=delayed_shutdown, daemon=True).start()
        
        return response
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/reboot', methods=['GET', 'OPTIONS'])
def reboot_pi():
    """
    Reboot the Raspberry Pi.
    
    Returns response immediately, then schedules reboot in 3 seconds
    to allow the HTTP response to be sent.
    
    Returns:
        JSON: Success message with 3-second delay warning
        
    Example:
        GET /reboot  # Initiate system reboot
    """
    if request.method == 'OPTIONS':
        return make_response('', 200)
    
    try:
        logger.info("Reboot command received from %s", request.remote_addr)
        
        # Return response first, then reboot
        response = jsonify({
            "status": "success",
            "message": "Raspberry Pi rebooting in 3 seconds...",
            "timestamp": datetime.now().isoformat()
        })
        
        def delayed_reboot():
            time.sleep(3)
            logger.info("Initiating system reboot...")
            os.system("sudo reboot")
        
        threading.Thread(target=delayed_reboot, daemon=True).start()
        
        return response
        
    except Exception as e:
        logger.error(f"Error during reboot: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    """
    Main entry point for the Darkroom Timer Relay Server.
    
    Initializes GPIO, sets up logging, displays network info, and starts Flask server.
    Handles graceful shutdown on Ctrl+C and ensures GPIO cleanup.
    
    Command line arguments:
        sys.argv[1] (optional): Port number (default: 5000)
    
    Example:
        python Raspberry_Server_v3.0.3.py      # Start on port 5000
        python Raspberry_Server_v3.0.3.py 8080 # Start on port 8080
    """
    try:
        # Setup GPIO
        setup_gpio()
        
        # Register cleanup function
        atexit.register(cleanup_gpio)
        
        # Get network info
        import socket
        hostname = socket.gethostname()
        
        # Get local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.254.254.254', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        
        logger.info("=" * 60)
        logger.info("Darkroom Timer Relay Server v2.0 Starting...")
        logger.info(f"Host: {hostname}")
        logger.info(f"Local IP: {local_ip}")
        logger.info("GPIO Pins configured:")
        for pin, info in RELAY_PINS.items():
            logger.info(f"  GPIO {pin}: {info['name']}")
        logger.info("CORS: ENABLED for all origins")
        logger.info("=" * 60)
        
        # Check if HTML file exists
        html_file = 'Darkroom_Tools_v3.0.3.html'
        if os.path.exists(html_file):
            logger.info(f"HTML file found: {html_file}")
            logger.info(f"Access the interface at: http://{local_ip}:5000/")
        else:
            logger.info(f"HTML file not found: {html_file}")
            logger.info("Place Darkroom_Tools_v3.0.3.html in the same directory")
            logger.info("Or access the API directly at: http://{local_ip}:5000/")
        
        # Get port from command line or use default
        import sys
        port = 5000
        if len(sys.argv) > 1:
            try:
                port = int(sys.argv[1])
            except ValueError:
                logger.warning(f"Invalid port: {sys.argv[1]}, using default: {port}")
        
        logger.info(f"Server starting on http://{local_ip}:{port}")
        logger.info("Available endpoints:")
        logger.info("  GET /             - Server info or HTML interface")
        logger.info("  GET /ping         - Test connection")
        logger.info("  GET /relay        - Control single relay (gpio, state)")
        logger.info("  GET /timer        - Timer relay (gpio, duration)")
        logger.info("  GET /status       - Get all relay states")
        logger.info("  GET /all          - Control all relays")
        logger.info("  GET /test         - Debug/test endpoint")
        logger.info("")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        
        # Run Flask server
        app.run(
            host='0.0.0.0',  # Listen on all interfaces
            port=port,
            threaded=True,
            debug=False
        )
        
    except KeyboardInterrupt:
        logger.info("Server shutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        cleanup_gpio()
