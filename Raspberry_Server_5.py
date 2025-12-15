#!/usr/bin/env python3
from flask import Flask, jsonify, request
import RPi.GPIO as GPIO
import time
import sys

app = Flask(__name__)

# GPIO Setup - CHANGE THESE TO YOUR ACTUAL GPIO PINS
RELAY_PINS = {
    1: 14,  # Relay 1
    2: 15,  # Relay 2
    3: 18,  # Relay 3
    4: 23   # Relay 4
}

# Relay state tracking
relay_states = {1: 'off', 2: 'off', 3: 'off', 4: 'off'}

def setup_gpio():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        print("Setting up GPIO pins:")
        for relay, pin in RELAY_PINS.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Start with relay OFF (HIGH for active-low relays)
            relay_states[relay] = 'off'
            print(f"  Relay {relay} -> GPIO{pin}: OFF")
        
        print("GPIO setup complete")
    except Exception as e:
        print(f"GPIO setup error: {e}")
        sys.exit(1)

@app.route('/')
def home():
    return jsonify({
        'status': 'ok',
        'message': 'Flask Relay Control Server',
        'endpoints': {
            'control': '/control?relay=<1-4>&action=<on|off|pulse>',
            'status': '/status',
            'test': '/test',
            'all_on': '/all/on',
            'all_off': '/all/off'
        },
        'current_states': relay_states
    })

@app.route('/control', methods=['GET'])
def control():
    try:
        relay = request.args.get('relay', type=int)
        action = request.args.get('action', '').lower()
        
        print(f"Control request: relay={relay}, action={action}")
        
        if not relay or relay not in RELAY_PINS:
            return jsonify({'error': 'Invalid relay number. Use 1-4'}), 400
        
        if action not in ['on', 'off', 'pulse']:
            return jsonify({'error': 'Invalid action. Use on, off, or pulse'}), 400
        
        pin = RELAY_PINS[relay]
        
        if action == 'on':
            GPIO.output(pin, GPIO.LOW)  # Relay ON
            relay_states[relay] = 'on'
            print(f"Relay {relay} (GPIO{pin}) -> ON")
            return jsonify({'status': 'ok', 'relay': relay, 'state': 'on'})
        
        elif action == 'off':
            GPIO.output(pin, GPIO.HIGH)  # Relay OFF
            relay_states[relay] = 'off'
            print(f"Relay {relay} (GPIO{pin}) -> OFF")
            return jsonify({'status': 'ok', 'relay': relay, 'state': 'off'})
        
        elif action == 'pulse':
            duration = request.args.get('duration', 1, type=float)
            GPIO.output(pin, GPIO.LOW)  # ON
            time.sleep(duration)
            GPIO.output(pin, GPIO.HIGH)  # OFF
            relay_states[relay] = 'off'
            print(f"Relay {relay} (GPIO{pin}) -> PULSE for {duration}s")
            return jsonify({'status': 'ok', 'relay': relay, 'state': 'pulsed', 'duration': duration})
    
    except Exception as e:
        print(f"Control error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        # Read actual GPIO states
        states = {}
        for relay, pin in RELAY_PINS.items():
            # GPIO.HIGH = OFF, GPIO.LOW = ON (for active-low relays)
            pin_state = GPIO.input(pin)
            states[relay] = 'off' if pin_state == GPIO.HIGH else 'on'
            relay_states[relay] = states[relay]
        
        return jsonify(states)
    except Exception as e:
        print(f"Status error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/all/<action>', methods=['GET'])
def all_relays(action):
    try:
        if action == 'on':
            for relay, pin in RELAY_PINS.items():
                GPIO.output(pin, GPIO.LOW)
                relay_states[relay] = 'on'
            print("All relays -> ON")
            return jsonify({'status': 'ok', 'message': 'All relays ON'})
        
        elif action == 'off':
            for relay, pin in RELAY_PINS.items():
                GPIO.output(pin, GPIO.HIGH)
                relay_states[relay] = 'off'
            print("All relays -> OFF")
            return jsonify({'status': 'ok', 'message': 'All relays OFF'})
        
        else:
            return jsonify({'error': 'Invalid action. Use on or off'}), 400
    
    except Exception as e:
        print(f"All relays error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'ok',
        'message': 'Server is running',
        'relay_pins': RELAY_PINS,
        'current_states': relay_states
    })

# Add CORS headers for all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    try:
        print("=" * 60)
        print("Starting Flask Relay Control Server")
        print("=" * 60)
        
        # Setup GPIO
        setup_gpio()
        
        # Display IP information
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        
        print(f"\nServer IP: {ip_address}")
        print("Port: 5000")
        print("\nTest URLs:")
        print(f"  http://{ip_address}:5000/")
        print(f"  http://{ip_address}:5000/test")
        print(f"  http://{ip_address}:5000/status")
        print(f"  http://{ip_address}:5000/control?relay=1&action=on")
        print(f"  http://{ip_address}:5000/control?relay=1&action=off")
        print(f"  http://{ip_address}:5000/all/on")
        print(f"  http://{ip_address}:5000/all/off")
        print("\n" + "=" * 60)
        
        # Run server
        app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
        
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        GPIO.cleanup()
        print("GPIO cleaned up. Goodbye!")