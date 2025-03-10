

import os
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_socketio import SocketIO

import config
import utils
from siem_core import SIEMCore

# Instantiate Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins="*")

# Create reference to SIEM instance (will be set in initialize_web_server)
siem_instance = None

def initialize_web_server(siem):
    """Initialize the web server with a SIEM instance"""
    global siem_instance
    siem_instance = siem
    logging.info("Web server initialized with SIEM instance")

def emit_event(event_name, data):
    """Emit an event to connected clients"""
    try:
        socketio.emit(event_name, data)
    except Exception as e:
        logging.error(f"Error emitting {event_name} event: {str(e)}")

@app.route('/test')
def test_route():
    """Simple test endpoint to verify Flask is working"""
    return "SIEM Web Server is running!"

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/alerts')
def alerts_page():
    """Alerts management page"""
    return render_template('alerts.html')

@app.route('/events')
def events_page():
    """Events browser page"""
    return render_template('events.html')

@app.route('/settings')
def settings_page():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/stats')
def get_stats():
    """API endpoint for statistics"""
    if siem_instance:
        return jsonify(siem_instance.get_stats())
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/alerts')
def get_alerts():
    """API endpoint for alerts"""
    if siem_instance:
        acknowledged = request.args.get('acknowledged')
        if acknowledged is not None:
            acknowledged = acknowledged.lower() == 'true'
            
        severity = request.args.get('severity')
        limit = request.args.get('limit', 100, type=int)
        
        return jsonify(siem_instance.get_alerts(limit, acknowledged, severity))
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/events')
def get_events():
    """API endpoint for events"""
    if siem_instance:
        source = request.args.get('source')
        limit = request.args.get('limit', 100, type=int)
        
        return jsonify(siem_instance.get_events(limit, source))
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/acknowledge_alert', methods=['POST'])
def acknowledge_alert():
    """API endpoint to acknowledge an alert"""
    if siem_instance:
        try:
            data = request.get_json()
            alert_id = data.get('alert_id')
            
            if alert_id and siem_instance.acknowledge_alert(alert_id):
                return jsonify({'success': True})
            return jsonify({'success': False, 'error': 'Alert not found'})
        except Exception as e:
            logging.error(f"Error acknowledging alert: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/save_state', methods=['POST'])
def save_state():
    """API endpoint to save state"""
    if siem_instance:
        if siem_instance.save_state():
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to save state'})
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/load_state', methods=['POST'])
def load_state():
    """API endpoint to load state"""
    if siem_instance:
        if siem_instance.load_state():
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Failed to load state'})
    return jsonify({'error': 'SIEM not initialized'})

@app.route('/api/reset_alerts', methods=['POST'])
def reset_alerts():
    """API endpoint to reset all alerts"""
    if siem_instance:
        try:
            with siem_instance.lock:
                siem_instance.alerts = []
                siem_instance.stats['alerts_generated'] = 0
                siem_instance.stats['alerts_per_rule'] = {}
            return jsonify({'success': True})
        except Exception as e:
            logging.error(f"Error resetting alerts: {str(e)}")
            return jsonify({'success': False, 'error': str(e)})
    return jsonify({'error': 'SIEM not initialized'})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logging.info("Client connected")
    
@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logging.info("Client disconnected")

def get_socketio_instance():
    """Get SocketIO instance for event emitting"""
    return socketio

def start_web_server(host=None, port=None, debug=None):
    """Start the web server"""
    if host is None:
        host = config.WEB_HOST
    if port is None:
        port = config.WEB_PORT
    if debug is None:
        debug = config.DEBUG_MODE
        
    # Check if port is available
    if not utils.check_port_availability(port):
        fallback_port = port + 1
        logging.warning(f"Port {port} is already in use! Using port {fallback_port} instead.")
        port = fallback_port
        
    logging.info(f"Starting web server at http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == "__main__":
    # Stand-alone test
    utils.setup_logging()
    utils.ensure_directories_exist()
    
    # Create a test SIEM instance
    import static_generator
    static_generator.generate_static_files()
    
    siem = SIEMCore()
    initialize_web_server(siem)
    
    print("Starting web server for testing...")
    start_web_server(host='127.0.0.1', port=5000, debug=True)