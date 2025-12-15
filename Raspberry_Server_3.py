from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import RPi.GPIO as GPIO
import time
import threading
import json

app = Flask(__name__)

# Enable CORS for ALL routes and ALL origins
CORS(app, resources={
    r"/*": {
        "origins": "*",  # Allow all origins
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type"]
    }
})

# Add headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Expose-Headers'] = 'Content-Type'
    return response

# Handle OPTIONS requests for all routes
@app.before_request
def handle_options_request():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "*")
        response.headers.add("Access-Control-Allow-Methods", "*")
        return response

# GPIO pin mapping for relays (BCM numbering)
RELAY_PINS = {
    1: 17,  # Relay 1 on GPIO 17
    2: 18,  # Relay 2 on GPIO 18
    3: 27,  # Relay 3 on GPIO 27
    4: 22   # Relay 4 on GPIO 22
}

# Store current relay states
relay_states = {1: False, 2: False, 3: False, 4: False}

def setup_gpio():
    """Initialize GPIO pins for relays"""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    for relay_num, pin in RELAY_PINS.items():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Relay OFF state (HIGH = OFF)
        relay_states[relay_num] = False

def pulse_relay(relay_num, duration_ms):
    """Pulse a relay for a specific duration in a separate thread"""
    def pulse():
        pin = RELAY_PINS.get(relay_num)
        if pin:
            GPIO.output(pin, GPIO.LOW)  # Turn ON
            relay_states[relay_num] = True
            time.sleep(duration_ms / 1000.0)
            GPIO.output(pin, GPIO.HIGH)  # Turn OFF
            relay_states[relay_num] = False
    
    thread = threading.Thread(target=pulse)
    thread.daemon = True
    thread.start()
    return thread

@app.route('/')
def index():
    """Home page - test if server is running"""
    return jsonify({
        'status': 'online',
        'message': 'Raspberry Pi Relay Server',
        'endpoints': {
            'relay_control': '/relay/<int:relay_num>/on',
            'relay_off': '/relay/<int:relay_num>/off',
            'relay_pulse': '/relay/<int:relay_num>/pulse?duration=<ms>',
            'relay_status': '/relay/<int:relay_num>/status',
            'all_relays': '/relays/status',
            'all_on': '/relays/all/on',
            'all_off': '/relays/all/off'
        },
        'relay_pins': RELAY_PINS
    })

@app.route('/relay/<int:relay_num>/on', methods=['GET'])
def relay_on(relay_num):
    """Turn a specific relay ON"""
    pin = RELAY_PINS.get(relay_num)
    if not pin:
        return jsonify({'error': f'Relay {relay_num} not found'}), 404
    
    GPIO.output(pin, GPIO.LOW)  # LOW turns relay ON
    relay_states[relay_num] = True
    
    return jsonify({
        'relay': relay_num,
        'status': 'ON',
        'pin': pin,
        'gpio_state': 'LOW'
    })

@app.route('/relay/<int:relay_num>/off', methods=['GET'])
def relay_off(relay_num):
    """Turn a specific relay OFF"""
    pin = RELAY_PINS.get(relay_num)
    if not pin:
        return jsonify({'error': f'Relay {relay_num} not found'}), 404
    
    GPIO.output(pin, GPIO.HIGH)  # HIGH turns relay OFF
    relay_states[relay_num] = False
    
    return jsonify({
        'relay': relay_num,
        'status': 'OFF',
        'pin': pin,
        'gpio_state': 'HIGH'
    })

@app.route('/relay/<int:relay_num>/pulse', methods=['GET'])
def relay_pulse(relay_num):
    """Pulse a relay for a specified duration in milliseconds"""
    duration = request.args.get('duration', default=1000, type=int)
    
    pin = RELAY_PINS.get(relay_num)
    if not pin:
        return jsonify({'error': f'Relay {relay_num} not found'}), 404
    
    if duration <= 0:
        return jsonify({'error': 'Duration must be positive'}), 400
    
    # Pulse in background thread
    pulse_relay(relay_num, duration)
    
    return jsonify({
        'relay': relay_num,
        'action': 'pulsed',
        'duration_ms': duration,
        'pin': pin
    })

@app.route('/relay/<int:relay_num>/status', methods=['GET'])
def relay_status(relay_num):
    """Get the current status of a relay"""
    pin = RELAY_PINS.get(relay_num)
    if not pin:
        return jsonify({'error': f'Relay {relay_num} not found'}), 404
    
    # Read GPIO state (LOW = ON, HIGH = OFF)
    state = GPIO.input(pin)
    status = 'ON' if state == GPIO.LOW else 'OFF'
    relay_states[relay_num] = (status == 'ON')
    
    return jsonify({
        'relay': relay_num,
        'status': status,
        'pin': pin,
        'gpio_state': state,
        'state': relay_states[relay_num]
    })

@app.route('/relays/status', methods=['GET'])
def all_relays_status():
    """Get status of all relays"""
    statuses = []
    for relay_num, pin in RELAY_PINS.items():
        state = GPIO.input(pin)
        status = 'ON' if state == GPIO.LOW else 'OFF'
        relay_states[relay_num] = (status == 'ON')
        statuses.append({
            'relay': relay_num,
            'status': status,
            'pin': pin,
            'gpio_state': state,
            'state': relay_states[relay_num]
        })
    
    return jsonify({'relays': statuses})

@app.route('/relays/all/on', methods=['GET'])
def all_relays_on():
    """Turn ALL relays ON"""
    results = []
    for relay_num, pin in RELAY_PINS.items():
        GPIO.output(pin, GPIO.LOW)  # LOW turns relay ON
        relay_states[relay_num] = True
        results.append({
            'relay': relay_num,
            'status': 'ON',
            'pin': pin
        })
    
    return jsonify({'action': 'all_on', 'results': results})

@app.route('/relays/all/off', methods=['GET'])
def all_relays_off():
    """Turn ALL relays OFF"""
    results = []
    for relay_num, pin in RELAY_PINS.items():
        GPIO.output(pin, GPIO.HIGH)  # HIGH turns relay OFF
        relay_states[relay_num] = False
        results.append({
            'relay': relay_num,
            'status': 'OFF',
            'pin': pin
        })
    
    return jsonify({'action': 'all_off', 'results': results})

@app.route('/test', methods=['GET'])
def test_connection():
    """Test endpoint to verify server is responding"""
    return jsonify({
        'status': 'success',
        'message': 'Server is responding',
        'timestamp': time.time(),
        'relay_states': relay_states
    })

def cleanup():
    """Cleanup GPIO on exit"""
    GPIO.cleanup()

if __name__ == '__main__':
    try:
        setup_gpio()
        print("Starting Raspberry Pi Relay Server...")
        print("GPIO pins initialized")
        print("Available relays:", RELAY_PINS)
        print("CORS enabled for all origins")
        
        # Run on all network interfaces, port 5000
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()