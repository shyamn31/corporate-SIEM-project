
import os
import logging

# Directory paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
CSS_DIR = os.path.join(STATIC_DIR, "css")
JS_DIR = os.path.join(STATIC_DIR, "js")

# Web server settings
WEB_HOST = "0.0.0.0"
WEB_PORT = 5000
DEBUG_MODE = True
SECRET_KEY = "siem-secret-key"  # In production, use a proper secret key

# SIEM settings
LOG_SOURCES = {
    'auth_log': os.path.join(LOGS_DIR, 'auth.log'),
    'web_log': os.path.join(LOGS_DIR, 'web.log'),
    'firewall_log': os.path.join(LOGS_DIR, 'firewall.log'),
    'ids_log': os.path.join(LOGS_DIR, 'ids.log'),
    'windows_log': os.path.join(LOGS_DIR, 'windows.log'),
}

# SIEM rules with MITRE ATT&CK mappings
DETECTION_RULES = [
    {
        'name': 'Brute Force Attack',
        'pattern': r'Failed password for .+ from (\d+\.\d+\.\d+\.\d+)',
        'log_source': 'auth_log',
        'threshold': 5,
        'time_window': 120,  # 2 minutes
        'severity': 'high',
        'mitre_tactic': 'Credential Access',
        'mitre_technique': 'Brute Force'
    },
    {
        'name': 'Port Scan Detection',
        'pattern': r'BLOCKED.+SRC=(\d+\.\d+\.\d+\.\d+)',
        'log_source': 'firewall_log',
        'threshold': 10,
        'time_window': 60,  # 1 minute
        'severity': 'medium',
        'mitre_tactic': 'Discovery',
        'mitre_technique': 'Network Service Scanning'
    },
    {
        'name': 'Web Attack',
        'pattern': r'GET .+(?:\'|<script>|alert\(|../../).+HTTP.+(\d+\.\d+\.\d+\.\d+)',
        'log_source': 'web_log',
        'threshold': 2,
        'time_window': 60,  # 1 minute
        'severity': 'high',
        'mitre_tactic': 'Initial Access',
        'mitre_technique': 'Exploit Public-Facing Application'
    },
    {
        'name': 'IDS Alert',
        'pattern': r'\[\*\*\].+\[\*\*\].+{{TCP}} (\d+\.\d+\.\d+\.\d+)',
        'log_source': 'ids_log',
        'threshold': 1,  # Any IDS alert is significant
        'time_window': 300,  # 5 minutes
        'severity': 'high',
        'mitre_tactic': 'Multiple',
        'mitre_technique': 'Multiple'
    },
    {
        'name': 'Suspicious Process',
        'pattern': r'EventID 4688.+Process: (powershell\.exe|cmd\.exe|certutil\.exe|regsvr32\.exe).+CommandLine: .+(-enc|urlcache|-f|http:)',
        'log_source': 'windows_log',
        'threshold': 1,
        'time_window': 300,  # 5 minutes
        'severity': 'high',
        'mitre_tactic': 'Execution',
        'mitre_technique': 'Command and Scripting Interpreter'
    },
    {
        'name': 'Data Exfiltration',
        'pattern': r'ACCEPT.+SRC=(\d+\.\d+\.\d+\.\d+).+SIZE=(\d+)',
        'log_source': 'firewall_log',
        'threshold': 1,
        'time_window': 300,  # 5 minutes
        'severity': 'critical',
        'mitre_tactic': 'Exfiltration',
        'mitre_technique': 'Exfiltration Over C2 Channel',
        'custom_match': lambda match: int(match.group(2)) > 1000000  # Only if size > 1MB
    }
]

# Logging configuration
LOGGING_CONFIG = {
    'level': logging.INFO,
    'format': '%(asctime)s - %(levelname)s - %(message)s',
    'filename': 'siem.log'
}

# State persistence
STATE_FILE = 'siem_state.json'