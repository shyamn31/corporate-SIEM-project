# SIEM Dashboard

A Security Information and Event Management (SIEM) dashboard for cybersecurity training and analysis practice.

## Overview

This project creates a comprehensive SIEM tool with a web-based dashboard for security monitoring and analysis. It's designed for cybersecurity beginners who want to gain hands-on experience with security log analysis, event correlation, and incident response.

The system generates realistic security logs (authentication attempts, web attacks, port scans, etc.) and provides a modern interface for monitoring and analyzing these events.

## Features

- **Real-time Log Generation**: Simulates realistic security events including:
  - Brute force attacks
  - Port scanning
  - Web application attacks (SQL injection, XSS, path traversal)
  - Malware command & control communication
  - Data exfiltration
  - Normal user activity

- **Web-based Dashboard**: 
  - Visual statistics and trend analysis
  - Alert management with MITRE ATT&CK mapping
  - Event browser with security analysis
  - Real-time updates via WebSockets

- **Core SIEM Functionality**:
  - Log collection and normalization
  - Event correlation with configurable rules
  - Alert generation and management
  - State persistence

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/siem-dashboard.git
   cd siem-dashboard
   ```

2. Install required packages:
   ```bash
   pip install flask flask-socketio
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```

## Project Structure

```
siem-project/
├── app.py                 # Main application entry point
├── log_generator.py       # Log generation functionality
├── siem_core.py           # Core SIEM monitoring functionality
├── web_server.py          # Web server and routes  
├── utils.py               # Utility functions
├── static_generator.py    # Static file generation
├── config.py              # Configuration settings
├── static/                # Static web assets
│   ├── css/
│   └── js/ 
├── templates/             # HTML templates
├── logs/                  # Generated logs
└── README.md              # Project documentation
```

## Usage

### Main Dashboard

The main dashboard provides an overview of security events, alerts, and system statistics. It includes:
- Alert counts and severity breakdown
- Event processing metrics
- Event trend visualization
- Top event sources and alert rules
- Recent alerts and events

### Alerts Management

The alerts page allows you to:
- View all security alerts
- Filter by severity, status, or search term
- Acknowledge alerts
- View detailed alert information
- Get recommended response actions based on alert type

### Event Browser

The events browser lets you:
- View all security events
- Filter by source or search term
- Analyze event details
- Extract and highlight important information

### Settings

The settings page provides:
- System controls (save/load state)
- Alert threshold configuration
- Attack simulation controls

## Learning Opportunities

This SIEM dashboard provides numerous learning opportunities for cybersecurity beginners:

1. **Log Analysis**: Practice identifying patterns and anomalies in security logs
2. **Alert Triage**: Learn to prioritize and respond to security alerts
3. **Event Correlation**: Understand how different events relate to each other
4. **MITRE ATT&CK**: See how attacks map to the MITRE ATT&CK framework
5. **Incident Response**: Practice following recommended response procedures

## Extending the Project

Here are some ways to extend this project for further learning:

1. Add more data sources:
   - Windows Event Logs
   - Network device logs
   - Endpoint telemetry

2. Implement custom detection rules for specific attack scenarios

3. Add case management for tracking incident response

4. Integrate with open-source threat intelligence feeds

5. Implement machine learning for anomaly detection

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project is designed for educational purposes to help beginners gain practical SIEM experience
- Inspired by enterprise SIEM solutions like Splunk, ELK Stack, and QRadar
- Built with Flask, Socket.IO, and Bootstrap
