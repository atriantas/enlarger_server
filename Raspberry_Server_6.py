#!/usr/bin/env python3
"""
Raspberry Pi Relay Control Server for Darkroom Timer
Pins: GPIO14, GPIO15, GPIO18, GPIO23
Run with: python3 relay_server.py
"""

from flask import Flask, jsonify, request, render_template_string
import RPi.GPIO as GPIO
import time
import threading
import os

# Pin configuration
RELAY_PINS = {
    1: 14,  # Relay 1
    2: 15,  # Relay 2
    3: 18,  # Relay 3
    4: 23   # Relay 4
}

# Default relay names
RELAY_NAMES = {
    1: "Relay 1",
    2: "Relay 2", 
    3: "Relay 3",
    4: "Relay 4"
}

# Relay states
relay_states = {pin: False for pin in RELAY_PINS.keys()}

app = Flask(__name__)

# HTML interface for testing
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Raspberry Pi Relay Control</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .relay { margin: 10px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
        .status { padding: 5px; margin: 5px; border-radius: 3px; }
        .on { background: #4CAF50; color: white; }
        .off { background: #f44336; color: white; }
        button { padding: 10px 15px; margin: 5px; cursor: pointer; }
        .all-controls { margin-top: 20px; padding: 15px; border: 2px solid #333; }
    </style>
</head>
<body>
    <h1>Raspberry Pi Relay Control</h1>
    <p>Server running on GPIO pins: 14, 15, 18, 23</p>
    
    {% for relay_num in [1, 2, 3, 4] %}
    <div class="relay">
        <h3>Relay {{ relay_num }} (GPIO{{ RELAY_PINS[relay_num] }})</h3>
        <div class="status {% if relay_states[relay_num] %}on{% else %}off{% endif %}">
            Status: {% if relay_states[relay_num] %}ON{% else %}OFF{% endif %}
        </div>
        <button onclick="controlRelay({{ relay_num }}, 'on')">Turn ON</button>
        <button onclick="controlRelay({{ relay_num }}, 'off')">Turn OFF</button>
        <button onclick="controlRelay({{ relay_num }}, 'toggle')">Toggle</button>
        <button onclick="pulseRelay({{ relay_num }})">Pulse (1s)</button>
    </div>
    {% endfor %}
    
    <div class="all-controls">
        <h3>All Relays Control</h3>
        <button onclick="controlAll('on')">Turn ALL ON</button>
        <button onclick="controlAll('off')">Turn ALL OFF</button>
        <button onclick="pulseAll()">Pulse ALL (1s)</button>
    </div>
    
    <div style="margin-top: 20px;">
        <h3>API Endpoints:</h3>
        <ul>
            <li>GET <a href="/relays/status">/relays/status</a> - Get all relay status</li>
            <li>GET <a href="/test">/test</a> - Test connection</li>
        </ul>
    </div>
    
    <script>
        function controlRelay(relay, action) {
            fetch(`/relay/${relay}/${action}`)
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Success');
                    location.reload();
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
        }
        
        function pulseRelay(relay) {
            fetch(`/relay/${relay}/pulse?duration=1000`)
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Pulse sent');
                    setTimeout(() => location.reload(), 1200);
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
        }
        
        function controlAll(action) {
            fetch(`/relays/all/${action}`)
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Success');
                    location.reload();
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
        }
        
        function pulseAll() {
            fetch('/relays/all/pulse?duration=1000')
                .then(response => response.json())
                .then(data => {
                    alert(data.message || 'Pulse sent');
                    setTimeout(() => location.reload(), 1200);
                })
                .catch(error => {
                    alert('Error: ' + error);
                });
        }
    </script>
</body>
</html>
"""

def setup_gpio():
    """Initialize GPIO pins"""
    try:
        GPIO.setmode(GPIO.BCM)  # Use BCM numbering
        
        # Setup each relay pin as output
        for pin in RELAY_PINS.values():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Start with relay OFF (assuming active LOW)
        
        print("GPIO initialized successfully")
        return True
    except Exception as e:
        print(f"Error setting up GPIO: {e}")
        return False

def control_relay(relay_num, state):
    """Control a specific relay"""
    try:
        if relay_num not in RELAY_PINS:
            return False, "Invalid relay number"
        
        pin = RELAY_PINS[relay_num]
        
        # Set GPIO pin
        # Assuming relay is active LOW (LOW = ON, HIGH = OFF)
        # Adjust if your relays are active HIGH
        if state == "on":
            GPIO.output(pin, GPIO.LOW)  # Turn relay ON
            relay_states[relay_num] = True
        else:  # "off"
            GPIO.output(pin, GPIO.HIGH)  # Turn relay OFF
            relay_states[relay_num] = False
            
        return True, f"Relay {relay_num} turned {state}"
    except Exception as e:
        return False, f"Error controlling relay: {e}"

def pulse_relay(relay_num, duration_ms=1000):
    """Pulse a relay for specified duration"""
    def pulse_thread():
        control_relay(relay_num, "on")
        time.sleep(duration_ms / 1000.0)
        control_relay(relay_num, "off")
    
    thread = threading.Thread(target=pulse_thread)
    thread.daemon = True
    thread.start()
    return True, f"Relay {relay_num} pulsing for {duration_ms}ms"

# Flask Routes
@app.route('/')
def index():
    """Web interface for manual control"""
    return render_template_string(HTML_INTERFACE, 
                                  RELAY_PINS=RELAY_PINS, 
                                  relay_states=relay_states)

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint to verify server is running"""
    return jsonify({
        "success": True,
        "message": "Relay server is running",
        "relays": len(RELAY_PINS),
        "pins": list(RELAY_PINS.values())
    })

@app.route('/relay/<int:relay_num>/on', methods=['GET'])
def relay_on(relay_num):
    """Turn a specific relay ON"""
    success, message = control_relay(relay_num, "on")
    return jsonify({
        "success": success,
        "message": message,
        "relay": relay_num,
        "state": "on"
    })

@app.route('/relay/<int:relay_num>/off', methods=['GET'])
def relay_off(relay_num):
    """Turn a specific relay OFF"""
    success, message = control_relay(relay_num, "off")
    return jsonify({
        "success": success,
        "message": message,
        "relay": relay_num,
        "state": "off"
    })

@app.route('/relay/<int:relay_num>/toggle', methods=['GET'])
def relay_toggle(relay_num):
    """Toggle a relay state"""
    current_state = relay_states.get(relay_num, False)
    new_state = "off" if current_state else "on"
    success, message = control_relay(relay_num, new_state)
    return jsonify({
        "success": success,
        "message": message,
        "relay": relay_num,
        "state": new_state
    })

@app.route('/relay/<int:relay_num>/pulse', methods=['GET'])
def relay_pulse(relay_num):
    """Pulse a relay for specified duration"""
    duration = request.args.get('duration', default=1000, type=int)
    success, message = pulse_relay(relay_num, duration)
    return jsonify({
        "success": success,
        "message": message,
        "relay": relay_num,
        "duration_ms": duration
    })

@app.route('/relays/status', methods=['GET'])
def relays_status():
    """Get status of all relays"""
    status = {}
    for relay_num in RELAY_PINS.keys():
        status[relay_num] = {
            "state": "on" if relay_states.get(relay_num, False) else "off",
            "pin": RELAY_PINS[relay_num],
            "name": RELAY_NAMES.get(relay_num, f"Relay {relay_num}")
        }
    
    return jsonify({
        "success": True,
        "relays": status,
        "count": len(RELAY_PINS)
    })

@app.route('/relays/all/on', methods=['GET'])
def all_relays_on():
    """Turn all relays ON"""
    results = []
    for relay_num in RELAY_PINS.keys():
        success, message = control_relay(relay_num, "on")
        results.append({
            "relay": relay_num,
            "success": success,
            "message": message
        })
    
    return jsonify({
        "success": all(r["success"] for r in results),
        "message": "All relays turned on",
        "results": results
    })

@app.route('/relays/all/off', methods=['GET'])
def all_relays_off():
    """Turn all relays OFF"""
    results = []
    for relay_num in RELAY_PINS.keys():
        success, message = control_relay(relay_num, "off")
        results.append({
            "relay": relay_num,
            "success": success,
            "message": message
        })
    
    return jsonify({
        "success": all(r["success"] for r in results),
        "message": "All relays turned off",
        "results": results
    })

@app.route('/relays/all/pulse', methods=['GET'])
def all_relays_pulse():
    """Pulse all relays"""
    duration = request.args.get('duration', default=1000, type=int)
    
    def pulse_all_thread():
        # Turn all on
        for relay_num in RELAY_PINS.keys():
            control_relay(relay_num, "on")
        
        time.sleep(duration / 1000.0)
        
        # Turn all off
        for relay_num in RELAY_PINS.keys():
            control_relay(relay_num, "off")
    
    thread = threading.Thread(target=pulse_all_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "message": f"All relays pulsing for {duration}ms",
        "duration_ms": duration
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Endpoint not found"
    }), 404

def cleanup():
    """Cleanup GPIO on exit"""
    print("\nCleaning up GPIO...")
    try:
        # Turn all relays off before exiting
        for relay_num in RELAY_PINS.keys():
            control_relay(relay_num, "off")
        GPIO.cleanup()
        print("GPIO cleaned up")
    except:
        pass

if __name__ == '__main__':
    try:
        # Setup GPIO
        if not setup_gpio():
            print("Failed to setup GPIO. Exiting.")
            exit(1)
        
        # Register cleanup function
        import atexit
        atexit.register(cleanup)
        
        print(f"Starting Relay Control Server...")
        print(f"Relay pins: {RELAY_PINS}")
        print(f"Web interface: http://<raspberry-pi-ip>:5000")
        print(f"API endpoints available")
        print("Press Ctrl+C to stop\n")
        
        # Run Flask server
        # Use host='0.0.0.0' to make it accessible from other devices
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
        
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cleanup()