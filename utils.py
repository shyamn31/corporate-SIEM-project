
import os
import socket
import logging
import json
from datetime import datetime
import config

def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(**config.LOGGING_CONFIG)
    logging.info("Logging initialized")


def check_port_availability(port=None):
    """
    Check if the specified port is available
    Returns True if port is available, False otherwise
    """
    if port is None:
        port = config.WEB_PORT
        
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        available = True
    except socket.error:
        available = False
    finally:
        s.close()
    return available

def ensure_directories_exist():
    """Create necessary directories if they don't exist"""
    directories = [
        config.LOGS_DIR,
        config.TEMPLATES_DIR,
        config.STATIC_DIR,
        config.CSS_DIR,
        config.JS_DIR
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created directory: {directory}")

def save_json(data, filename):
    """Save data to a JSON file"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {filename}: {str(e)}")
        return False

def load_json(filename):
    """Load data from a JSON file"""
    if not os.path.exists(filename):
        return None
        
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {filename}: {str(e)}")
        return None

def format_timestamp(timestamp=None):
    """Format a timestamp for display"""
    if timestamp is None:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elif isinstance(timestamp, str):
        return datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def extract_ip_addresses(text):
    """Extract IP addresses from text using regex"""
    import re
    ipv4_regex = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
    matches = re.findall(ipv4_regex, text)
    return list(set(matches))  # Remove duplicates

def is_valid_ip(ip):
    """Check if string is a valid IP address"""
    import re
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    if not re.match(pattern, ip):
        return False
    try:
        return all(0 <= int(octet) <= 255 for octet in ip.split('.'))
    except ValueError:
        return False

def calculate_uptime(start_time):
    """Calculate and format system uptime"""
    uptime_seconds = datetime.now().timestamp() - start_time
    return {
        'hours': int(uptime_seconds // 3600),
        'minutes': int((uptime_seconds % 3600) // 60),
        'seconds': int(uptime_seconds % 60)
    }