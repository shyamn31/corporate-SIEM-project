

import os
import logging

import config

def create_directory_structure():
    """Create all necessary directories for the web interface"""
    # Create templates directory
    if not os.path.exists(config.TEMPLATES_DIR):
        os.makedirs(config.TEMPLATES_DIR)
        logging.info(f"Created templates directory: {config.TEMPLATES_DIR}")
    
    # Create static directory and subdirectories
    for directory in [config.STATIC_DIR, config.CSS_DIR, config.JS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Created static directory: {directory}")

def create_template_files():
    """Create HTML template files"""
    
    # Base template
    with open(os.path.join(config.TEMPLATES_DIR, "base.html"), "w") as f:
        f.write(r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}SIEM Dashboard{% endblock %}</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="/">SIEM Dashboard</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/' %}active{% endif %}" href="/">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/alerts' %}active{% endif %}" href="/alerts">
                            <i class="bi bi-exclamation-triangle"></i> Alerts
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/events' %}active{% endif %}" href="/events">
                            <i class="bi bi-list-ul"></i> Events
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.path == '/settings' %}active{% endif %}" href="/settings">
                            <i class="bi bi-gear"></i> Settings
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container-fluid py-3">
        {% block content %}{% endblock %}
    </div>

    <footer class="bg-dark text-white text-center py-3">
        <div class="container">
            <p class="mb-0">SIEM Dashboard - Built by Shyam Natarajan</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/socket.io@4.5.1/client-dist/socket.io.min.js"></script>
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>""")

    # Index (Dashboard) template
    with open(os.path.join(config.TEMPLATES_DIR, "index.html"), "w") as f:
        f.write(r"""{% extends "base.html" %}

{% block title %}SIEM Dashboard{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-12 mb-4">
        <div class="card border-0 shadow">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-house"></i> Security Overview
                    <span class="float-end" id="uptime-display">Uptime: Calculating...</span>
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-3">
                        <div class="card text-white bg-danger mb-3">
                            <div class="card-header">Active Alerts</div>
                            <div class="card-body">
                                <h3 class="card-title" id="active-alerts-count">0</h3>
                                <div class="d-flex justify-content-between mt-3">
                                    <small>Critical: <span id="critical-alerts-count">0</span></small>
                                    <small>High: <span id="high-alerts-count">0</span></small>
                                    <small>Medium: <span id="medium-alerts-count">0</span></small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-white bg-success mb-3">
                            <div class="card-header">Event Processing</div>
                            <div class="card-body">
                                <h3 class="card-title" id="events-processed">0</h3>
                                <div class="d-flex justify-content-between mt-3">
                                    <small>Per second: <span id="events-per-second">0</span></small>
                                    <small>Per minute: <span id="events-per-minute">0</span></small>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header">Event Activity Trend</div>
                            <div class="card-body">
                                <canvas id="events-trend-chart" height="100"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card border-0 shadow mb-4">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0"><i class="bi bi-exclamation-triangle"></i> Recent Alerts</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Rule</th>
                                <th>Source</th>
                                <th>Severity</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="recent-alerts-table">
                            <tr>
                                <td colspan="5" class="text-center">No alerts yet</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="text-end">
                    <a href="/alerts" class="btn btn-sm btn-outline-danger">View All Alerts</a>
                </div>
            </div>
        </div>
    </div>
    <div class="col-md-6">
        <div class="card border-0 shadow mb-4">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0"><i class="bi bi-list-ul"></i> Recent Events</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Source</th>
                                <th>Event</th>
                            </tr>
                        </thead>
                        <tbody id="recent-events-table">
                            <tr>
                                <td colspan="3" class="text-center">No events yet</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="text-end">
                    <a href="/events" class="btn btn-sm btn-outline-info">View All Events</a>
                </div>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card border-0 shadow mb-4">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0"><i class="bi bi-bar-chart"></i> Top Event Sources</h5>
            </div>
            <div class="card-body">
                <canvas id="sources-chart" height="250"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow mb-4">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0"><i class="bi bi-bar-chart"></i> Top Alert Rules</h5>
            </div>
            <div class="card-body">
                <canvas id="rules-chart" height="250"></canvas>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="card border-0 shadow mb-4">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0"><i class="bi bi-shield"></i> Security Posture</h5>
            </div>
            <div class="card-body">
                <canvas id="severity-chart" height="250"></canvas>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/dashboard.js') }}"></script>
{% endblock %}""")

    # Alerts template
    with open(os.path.join(config.TEMPLATES_DIR, "alerts.html"), "w") as f:
        f.write(r"""{% extends "base.html" %}

{% block title %}SIEM Alerts{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <div class="card border-0 shadow">
            <div class="card-header bg-danger text-white">
                <h5 class="mb-0">
                    <i class="bi bi-exclamation-triangle"></i> Alert Management
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-8">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-outline-secondary active" id="filter-all">All Alerts</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="filter-active">Active Only</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="filter-ack">Acknowledged</button>
                        </div>
                        
                        <div class="btn-group ms-2" role="group">
                            <button type="button" class="btn btn-sm btn-outline-danger" id="filter-critical">Critical</button>
                            <button type="button" class="btn btn-sm btn-outline-danger" id="filter-high">High</button>
                            <button type="button" class="btn btn-sm btn-outline-warning" id="filter-medium">Medium</button>
                            <button type="button" class="btn btn-sm btn-outline-success" id="filter-low">Low</button>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="input-group">
                            <input type="text" class="form-control form-control-sm" placeholder="Search alerts..." id="alert-search">
                            <button class="btn btn-sm btn-outline-secondary" type="button" id="search-btn">
                                <i class="bi bi-search"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Rule</th>
                                <th>Source</th>
                                <th>Severity</th>
                                <th>Status</th>
                                <th>MITRE Tactic</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="alerts-table">
                            <tr>
                                <td colspan="7" class="text-center">Loading alerts...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span id="alerts-count">0</span> alerts found
                    </div>
                    <div>
                        <nav>
                            <ul class="pagination pagination-sm justify-content-end mb-0">
                                <li class="page-item disabled">
                                    <a class="page-link" href="#" tabindex="-1">Previous</a>
                                </li>
                                <li class="page-item active"><a class="page-link" href="#">1</a></li>
                                <li class="page-item disabled">
                                    <a class="page-link" href="#">Next</a>
                                </li>
                            </ul>
                        </nav>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Alert Detail Modal -->
<div class="modal fade" id="alertDetailModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-danger text-white">
                <h5 class="modal-title" id="alertDetailTitle">Alert Details</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Rule:</strong> <span id="alert-detail-rule"></span></p>
                        <p><strong>Source:</strong> <span id="alert-detail-source"></span></p>
                        <p><strong>Timestamp:</strong> <span id="alert-detail-timestamp"></span></p>
                        <p><strong>Severity:</strong> <span id="alert-detail-severity"></span></p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>Status:</strong> <span id="alert-detail-status"></span></p>
                        <p><strong>Event Count:</strong> <span id="alert-detail-count"></span></p>
                        <p><strong>MITRE Tactic:</strong> <span id="alert-detail-tactic"></span></p>
                        <p><strong>MITRE Technique:</strong> <span id="alert-detail-technique"></span></p>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>Sample Log:</h6>
                    <pre class="bg-light p-2 rounded" id="alert-detail-log"></pre>
                </div>
                <div class="mt-3">
                    <h6>Recommended Actions:</h6>
                    <ul id="alert-detail-actions">
                    </ul>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-success" id="acknowledge-alert-btn">Acknowledge</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/alerts.js') }}"></script>
{% endblock %}""")

    # Events template
    with open(os.path.join(config.TEMPLATES_DIR, "events.html"), "w") as f:
        f.write(r"""{% extends "base.html" %}

{% block title %}SIEM Events{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <div class="card border-0 shadow">
            <div class="card-header bg-info text-white">
                <h5 class="mb-0">
                    <i class="bi bi-list-ul"></i> Event Browser
                </h5>
            </div>
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-8">
                        <div class="btn-group" role="group">
                            <button type="button" class="btn btn-sm btn-outline-secondary active" id="source-all">All Sources</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="source-auth">Auth</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="source-web">Web</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="source-firewall">Firewall</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="source-ids">IDS</button>
                            <button type="button" class="btn btn-sm btn-outline-secondary" id="source-windows">Windows</button>
                        </div>
                    </div>
                    <div class="col-md-4 text-end">
                        <div class="input-group">
                            <input type="text" class="form-control form-control-sm" placeholder="Search events..." id="event-search">
                            <button class="btn btn-sm btn-outline-secondary" type="button" id="search-btn">
                                <i class="bi bi-search"></i>
                            </button>
                        </div>
                    </div>
                </div>
                
                <div class="table-responsive">
                    <table class="table table-hover table-sm">
                        <thead>
                            <tr>
                                <th>Time</th>
                                <th>Source</th>
                                <th>Event</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="events-table">
                            <tr>
                                <td colspan="4" class="text-center">Loading events...</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <span id="events-count">0</span> events found
                    </div>
                    <div>
                        <button class="btn btn-sm btn-outline-info" id="refresh-events">
                            <i class="bi bi-arrow-clockwise"></i> Refresh
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Event Detail Modal -->
<div class="modal fade" id="eventDetailModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header bg-info text-white">
                <h5 class="modal-title">Event Details</h5>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
            </div>
            <div class="modal-body">
                <div class="row">
                    <div class="col-md-6">
                        <p><strong>Source:</strong> <span id="event-detail-source"></span></p>
                        <p><strong>Timestamp:</strong> <span id="event-detail-timestamp"></span></p>
                    </div>
                    <div class="col-md-6">
                        <p><strong>IP Address:</strong> <span id="event-detail-ip"></span></p>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>Raw Log:</h6>
                    <pre class="bg-light p-2 rounded" id="event-detail-log"></pre>
                </div>
                <div class="mt-3" id="event-analysis-section">
                    <h6>Event Analysis:</h6>
                    <div id="event-analysis-content">
                    </div>
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/events.js') }}"></script>
{% endblock %}""")

    # Settings template
    with open(os.path.join(config.TEMPLATES_DIR, "settings.html"), "w") as f:
        f.write(r"""{% extends "base.html" %}

{% block title %}SIEM Settings{% endblock %}

{% block content %}
<div class="row mb-3">
    <div class="col-md-12">
        <div class="card border-0 shadow">
            <div class="card-header bg-dark text-white">
                <h5 class="mb-0">
                    <i class="bi bi-gear"></i> SIEM Settings
                </h5>
            </div>
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header">System Controls</div>
                            <div class="card-body">
                                <div class="d-grid gap-2">
                                    <button class="btn btn-primary" id="save-state-btn">
                                        <i class="bi bi-save"></i> Save SIEM State
                                    </button>
                                    <button class="btn btn-warning" id="load-state-btn">
                                        <i class="bi bi-upload"></i> Load SIEM State
                                    </button>
                                    <button class="btn btn-danger" id="reset-alerts-btn">
                                        <i class="bi bi-x-circle"></i> Reset All Alerts
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="card mb-3">
                            <div class="card-header">Alert Thresholds</div>
                            <div class="card-body">
                                <form id="thresholds-form">
                                    <div class="mb-3">
                                        <label for="brute-force-threshold" class="form-label">Brute Force Attack Threshold</label>
                                        <input type="number" class="form-control" id="brute-force-threshold" value="5" min="1" max="20">
                                    </div>
                                    <div class="mb-3">
                                        <label for="port-scan-threshold" class="form-label">Port Scan Detection Threshold</label>
                                        <input type="number" class="form-control" id="port-scan-threshold" value="10" min="1" max="30">
                                    </div>
                                    <button type="submit" class="btn btn-success">
                                        <i class="bi bi-check-circle"></i> Update Thresholds
                                    </button>
                                </form>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row mt-3">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header">Attack Simulation Controls</div>
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="brute-force-switch" checked>
                                            <label class="form-check-label" for="brute-force-switch">Brute Force Attacks</label>
                                        </div>
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="port-scan-switch" checked>
                                            <label class="form-check-label" for="port-scan-switch">Port Scanning</label>
                                        </div>
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="web-attack-switch" checked>
                                            <label class="form-check-label" for="web-attack-switch">Web Application Attacks</label>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="malware-switch" checked>
                                            <label class="form-check-label" for="malware-switch">Malware Communication</label>
                                        </div>
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="exfil-switch" checked>
                                            <label class="form-check-label" for="exfil-switch">Data Exfiltration</label>
                                        </div>
                                        <div class="form-check form-switch mb-3">
                                            <input class="form-check-input" type="checkbox" id="normal-traffic-switch" checked>
                                            <label class="form-check-label" for="normal-traffic-switch">Normal Traffic</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <button class="btn btn-primary" id="apply-simulation-settings">
                                        <i class="bi bi-play-circle"></i> Apply Simulation Settings
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', filename='js/settings.js') }}"></script>
{% endblock %}""")

def create_css_files():
    """Create CSS files for the web interface"""
    # Main CSS
    with open(os.path.join(config.CSS_DIR, "style.css"), "w") as f:
        f.write(r"""/* Main SIEM Dashboard Styles */
body {
    background-color: #f8f9fa;
}

.card {
    border-radius: 8px;
    margin-bottom: 15px;
}

.card-header {
    border-radius: 8px 8px 0 0 !important;
}

.table thead th {
    border-top: none;
    border-bottom: 2px solid #dee2e6;
}

.alert-badge {
    font-size: 0.7em;
    padding: 0.35em 0.65em;
}

.alert-row-critical {
    background-color: rgba(220, 53, 69, 0.1);
}

.alert-row-high {
    background-color: rgba(253, 126, 20, 0.1);
}

.alert-row-medium {
    background-color: rgba(255, 193, 7, 0.1);
}

.alert-row-new {
    animation: highlight 2s ease-in-out;
}

@keyframes highlight {
    0% { background-color: rgba(13, 110, 253, 0.3); }
    100% { background-color: transparent; }
}

.event-row:hover {
    background-color: rgba(13, 110, 253, 0.05);
}

.truncate {
    max-width: 400px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
""")

def create_js_files():
    """Create JavaScript files for the web interface"""
    
    # Main JavaScript
    with open(os.path.join(config.JS_DIR, "main.js"), "w") as f:
        f.write(r"""// Main JavaScript for SIEM Dashboard

// Socket.io setup
const socket = io();

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Format uptime
function formatUptime(uptime) {
    return `${uptime.hours}h ${uptime.minutes}m ${uptime.seconds}s`;
}

// Get severity badge
function getSeverityBadge(severity) {
    let badgeClass = 'bg-secondary';
    
    switch(severity.toLowerCase()) {
        case 'critical':
            badgeClass = 'bg-danger';
            break;
        case 'high':
            badgeClass = 'bg-danger';
            break;
        case 'medium':
            badgeClass = 'bg-warning text-dark';
            break;
        case 'low':
            badgeClass = 'bg-success';
            break;
    }
    
    return `<span class="badge ${badgeClass}">${severity}</span>`;
}

// Get status badge
function getStatusBadge(acknowledged) {
    if (acknowledged) {
        return '<span class="badge bg-secondary">Acknowledged</span>';
    } else {
        return '<span class="badge bg-info">Active</span>';
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    // Could implement a toast notification system here
    console.log(`Toast: [${type}] ${message}`);
}

// Socket.io event handlers
socket.on('connect', () => {
    console.log('Connected to SIEM server');
});

socket.on('disconnect', () => {
    console.log('Disconnected from SIEM server');
});

socket.on('new_alert', (alert) => {
    showToast(`New alert: ${alert.rule_name} from ${alert.source}`, 'warning');
    
    // If we're on the dashboard or alerts page, update UI
    if (window.location.pathname === '/' || window.location.pathname === '/alerts') {
        fetchAlerts();
    }
});

socket.on('events_update', (data) => {
    // If we're on the dashboard or events page, update UI
    if (window.location.pathname === '/' || window.location.pathname === '/events') {
        fetchRecentEvents();
    }
});

socket.on('stats_update', (stats) => {
    // If we're on the dashboard, update stats
    if (window.location.pathname === '/') {
        updateDashboardStats(stats);
    }
});

// Generic API error handler
function handleApiError(error) {
    console.error('API Error:', error);
    showToast('Error communicating with the server', 'error');
}

// Alert acknowledgement
function acknowledgeAlert(alertId, callback) {
    fetch('/api/acknowledge_alert', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ alert_id: alertId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Alert acknowledged successfully', 'success');
            if (callback) callback(true);
        } else {
            showToast('Failed to acknowledge alert: ' + (data.error || 'Unknown error'), 'error');
            if (callback) callback(false);
        }
    })
    .catch(error => {
        handleApiError(error);
        if (callback) callback(false);
    });
}

// On document ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('SIEM Dashboard Initialized');
});
""")

    # Dashboard JavaScript
    with open(os.path.join(config.JS_DIR, "dashboard.js"), "w") as f:
        f.write(r"""// Dashboard specific JavaScript

// Charts
let eventsTrendChart = null;
let sourcesChart = null;
let rulesChart = null;
let severityChart = null;

// Initialize dashboard
function initDashboard() {
    fetchStats();
    fetchRecentAlerts();
    fetchRecentEvents();
    
    // Set up refresh intervals
    setInterval(fetchStats, 5000);
    setInterval(fetchRecentAlerts, 10000);
    setInterval(fetchRecentEvents, 10000);
}

// Fetch dashboard statistics
function fetchStats() {
    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(handleApiError);
}

// Update dashboard statistics
function updateDashboardStats(stats) {
    // Update uptime
    document.getElementById('uptime-display').textContent = `Uptime: ${formatUptime(stats.uptime)}`;
    
    // Update event stats
    document.getElementById('events-processed').textContent = stats.events_processed.toLocaleString();
    document.getElementById('events-per-second').textContent = stats.eps.toLocaleString();
    document.getElementById('events-per-minute').textContent = stats.epm.toLocaleString();
    
    // Update alert counts
    document.getElementById('active-alerts-count').textContent = (
        stats.severity_counts.critical + 
        stats.severity_counts.high + 
        stats.severity_counts.medium + 
        stats.severity_counts.low
    ).toLocaleString();
    
    document.getElementById('critical-alerts-count').textContent = stats.severity_counts.critical.toLocaleString();
    document.getElementById('high-alerts-count').textContent = stats.severity_counts.high.toLocaleString();
    document.getElementById('medium-alerts-count').textContent = stats.severity_counts.medium.toLocaleString();
    
    // Update charts
    updateEventsTrendChart(stats.events_trend);
    updateSourcesChart(stats.top_sources);
    updateRulesChart(stats.top_rules);
    updateSeverityChart(stats.severity_counts);
}

// Fetch recent alerts
function fetchRecentAlerts() {
    fetch('/api/alerts?limit=5&acknowledged=false')
        .then(response => response.json())
        .then(alerts => {
            const tableBody = document.getElementById('recent-alerts-table');
            
            if (alerts.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center">No alerts yet</td></tr>';
                return;
            }
            
            tableBody.innerHTML = '';
            
            alerts.forEach(alert => {
                const row = document.createElement('tr');
                if (alert.severity.toLowerCase() === 'critical') {
                    row.classList.add('alert-row-critical');
                } else if (alert.severity.toLowerCase() === 'high') {
                    row.classList.add('alert-row-high');
                } else if (alert.severity.toLowerCase() === 'medium') {
                    row.classList.add('alert-row-medium');
                }
                
                if (alert.new) {
                    row.classList.add('alert-row-new');
                }
                
                row.innerHTML = `
                    <td>${alert.timestamp}</td>
                    <td>${alert.rule_name}</td>
                    <td>${alert.source}</td>
                    <td>${getSeverityBadge(alert.severity)}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary acknowledge-btn" data-alert-id="${alert.id}">
                            Acknowledge
                        </button>
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // Add event listeners for acknowledge buttons
            document.querySelectorAll('.acknowledge-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const alertId = this.getAttribute('data-alert-id');
                    acknowledgeAlert(alertId, success => {
                        if (success) fetchRecentAlerts();
                    });
                });
            });
        })
        .catch(handleApiError);
}

// Fetch recent events
function fetchRecentEvents() {
    fetch('/api/events?limit=5')
        .then(response => response.json())
        .then(events => {
            const tableBody = document.getElementById('recent-events-table');
            
            if (events.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="3" class="text-center">No events yet</td></tr>';
                return;
            }
            
            tableBody.innerHTML = '';
            
            events.forEach(event => {
                const row = document.createElement('tr');
                row.classList.add('event-row');
                
                // Truncate long event content
                let content = event.content;
                if (content.length > 50) {
                    content = content.substring(0, 47) + '...';
                }
                
                row.innerHTML = `
                    <td>${event.timestamp}</td>
                    <td>${event.source}</td>
                    <td class="truncate">${content}</td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(handleApiError);
}

// Update events trend chart
function updateEventsTrendChart(eventsTrend) {
    const ctx = document.getElementById('events-trend-chart').getContext('2d');
    
    const labels = Array.from({length: eventsTrend.length}, (_, i) => `-${eventsTrend.length - i} min`);
    
    if (eventsTrendChart) {
        eventsTrendChart.data.labels = labels;
        eventsTrendChart.data.datasets[0].data = eventsTrend;
        eventsTrendChart.update();
    } else {
        eventsTrendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Events per Minute',
                    data: eventsTrend,
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    borderColor: 'rgba(40, 167, 69, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: 3
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                maintainAspectRatio: false
            }
        });
    }
}

// Update sources chart
function updateSourcesChart(topSources) {
    const ctx = document.getElementById('sources-chart').getContext('2d');
    
    const labels = topSources.map(source => source[0]);
    const data = topSources.map(source => source[1]);
    
    if (sourcesChart) {
        sourcesChart.data.labels = labels;
        sourcesChart.data.datasets[0].data = data;
        sourcesChart.update();
    } else {
        sourcesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Event Count',
                    data: data,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(201, 203, 207, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(201, 203, 207, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                maintainAspectRatio: false
            }
        });
    }
}

// Update rules chart
function updateRulesChart(topRules) {
    const ctx = document.getElementById('rules-chart').getContext('2d');
    
    const labels = topRules.map(rule => rule[0]);
    const data = topRules.map(rule => rule[1]);
    
    if (rulesChart) {
        rulesChart.data.labels = labels;
        rulesChart.data.datasets[0].data = data;
        rulesChart.update();
    } else {
        rulesChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Alert Count',
                    data: data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(255, 159, 64, 0.6)',
                        'rgba(255, 205, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(54, 162, 235, 0.6)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(255, 159, 64, 1)',
                        'rgba(255, 205, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(54, 162, 235, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                maintainAspectRatio: false
            }
        });
    }
}

// Update severity chart
function updateSeverityChart(severityCounts) {
    const ctx = document.getElementById('severity-chart').getContext('2d');
    
    const labels = ['Critical', 'High', 'Medium', 'Low'];
    const data = [
        severityCounts.critical,
        severityCounts.high,
        severityCounts.medium,
        severityCounts.low
    ];
    
    if (severityChart) {
        severityChart.data.datasets[0].data = data;
        severityChart.update();
    } else {
        severityChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(220, 53, 69, 0.8)',
                        'rgba(255, 128, 26, 0.8)',
                        'rgba(255, 193, 7, 0.8)',
                        'rgba(40, 167, 69, 0.8)'
                    ],
                    borderColor: [
                        'rgba(220, 53, 69, 1)',
                        'rgba(255, 128, 26, 1)',
                        'rgba(255, 193, 7, 1)',
                        'rgba(40, 167, 69, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initDashboard);
""")

    # Alerts JavaScript
    with open(os.path.join(config.JS_DIR, "alerts.js"), "w") as f:
        f.write(r"""// Alerts page specific JavaScript

// Current filter settings
let currentFilters = {
    acknowledged: null,
    severity: null,
    search: ''
};

// Initialize alerts page
function initAlertsPage() {
    fetchAlerts();
    
    // Set up refresh interval
    setInterval(fetchAlerts, 10000);
    
    // Set up filter event handlers
    document.getElementById('filter-all').addEventListener('click', function() {
        setActiveButton(this, 'status-filter');
        currentFilters.acknowledged = null;
        fetchAlerts();
    });
    
    document.getElementById('filter-active').addEventListener('click', function() {
        setActiveButton(this, 'status-filter');
        currentFilters.acknowledged = false;
        fetchAlerts();
    });
    
    document.getElementById('filter-ack').addEventListener('click', function() {
        setActiveButton(this, 'status-filter');
        currentFilters.acknowledged = true;
        fetchAlerts();
    });
    
    document.getElementById('filter-critical').addEventListener('click', function() {
        setActiveButton(this, 'severity-filter');
        currentFilters.severity = 'critical';
        fetchAlerts();
    });
    
    document.getElementById('filter-high').addEventListener('click', function() {
        setActiveButton(this, 'severity-filter');
        currentFilters.severity = 'high';
        fetchAlerts();
    });
    
    document.getElementById('filter-medium').addEventListener('click', function() {
        setActiveButton(this, 'severity-filter');
        currentFilters.severity = 'medium';
        fetchAlerts();
    });
    
    document.getElementById('filter-low').addEventListener('click', function() {
        setActiveButton(this, 'severity-filter');
        currentFilters.severity = 'low';
        fetchAlerts();
    });
    
    // Set up search functionality
    document.getElementById('search-btn').addEventListener('click', function() {
        currentFilters.search = document.getElementById('alert-search').value.trim();
        fetchAlerts();
    });
    
    document.getElementById('alert-search').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            currentFilters.search = this.value.trim();
            fetchAlerts();
        }
    });
    
    // Set up alert detail modal
    const alertDetailModal = document.getElementById('alertDetailModal');
    alertDetailModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const alertId = button.getAttribute('data-alert-id');
        
        // Find the alert data
        fetch(`/api/alerts`)
            .then(response => response.json())
            .then(alerts => {
                const alert = alerts.find(a => a.id === alertId);
                if (!alert) return;
                
                // Fill in alert details
                document.getElementById('alert-detail-rule').textContent = alert.rule_name;
                document.getElementById('alert-detail-source').textContent = alert.source;
                document.getElementById('alert-detail-timestamp').textContent = alert.timestamp;
                document.getElementById('alert-detail-severity').textContent = alert.severity;
                document.getElementById('alert-detail-status').textContent = alert.acknowledged ? 'Acknowledged' : 'Active';
                document.getElementById('alert-detail-count').textContent = alert.event_count;
                document.getElementById('alert-detail-tactic').textContent = alert.mitre_tactic || 'Unknown';
                document.getElementById('alert-detail-technique').textContent = alert.mitre_technique || 'Unknown';
                document.getElementById('alert-detail-log').textContent = alert.sample_log;
                
                // Set acknowledge button data
                document.getElementById('acknowledge-alert-btn').setAttribute('data-alert-id', alert.id);
                
                // Hide acknowledge button if already acknowledged
                document.getElementById('acknowledge-alert-btn').style.display = alert.acknowledged ? 'none' : 'block';
                
                // Generate recommended actions
                const actionsList = document.getElementById('alert-detail-actions');
                actionsList.innerHTML = '';
                
                // Add recommended actions based on alert type
                const actions = getRecommendedActions(alert);
                actions.forEach(action => {
                    const li = document.createElement('li');
                    li.textContent = action;
                    actionsList.appendChild(li);
                });
            })
            .catch(handleApiError);
    });
    
    // Set up acknowledge button in modal
    document.getElementById('acknowledge-alert-btn').addEventListener('click', function() {
        const alertId = this.getAttribute('data-alert-id');
        acknowledgeAlert(alertId, success => {
            if (success) {
                // Close modal and refresh alerts
                const modal = bootstrap.Modal.getInstance(document.getElementById('alertDetailModal'));
                modal.hide();
                fetchAlerts();
            }
        });
    });
}

// Set active button class
function setActiveButton(button, group) {
    if (group === 'status-filter') {
        document.querySelectorAll('#filter-all, #filter-active, #filter-ack').forEach(btn => {
            btn.classList.remove('active');
        });
    } else if (group === 'severity-filter') {
        document.querySelectorAll('#filter-critical, #filter-high, #filter-medium, #filter-low').forEach(btn => {
            btn.classList.remove('active');
        });
    }
    
    button.classList.add('active');
}

// Fetch alerts with current filters
function fetchAlerts() {
    // Build query string
    let queryParams = new URLSearchParams();
    
    if (currentFilters.acknowledged !== null) {
        queryParams.append('acknowledged', currentFilters.acknowledged);
    }
    
    if (currentFilters.severity !== null) {
        queryParams.append('severity', currentFilters.severity);
    }
    
    // Fetch alerts
    fetch(`/api/alerts?${queryParams.toString()}`)
        .then(response => response.json())
        .then(alerts => {
            // Filter by search term if provided
            if (currentFilters.search) {
                const searchTerm = currentFilters.search.toLowerCase();
                alerts = alerts.filter(alert => 
                    alert.rule_name.toLowerCase().includes(searchTerm) ||
                    alert.source.toLowerCase().includes(searchTerm) ||
                    alert.severity.toLowerCase().includes(searchTerm) ||
                    alert.sample_log.toLowerCase().includes(searchTerm)
                );
            }
            
            // Update alerts count
            document.getElementById('alerts-count').textContent = alerts.length;
            
            // Populate table
            const tableBody = document.getElementById('alerts-table');
            
            if (alerts.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No alerts found matching your criteria</td></tr>';
                return;
            }
            
            tableBody.innerHTML = '';
            
            alerts.forEach(alert => {
                const row = document.createElement('tr');
                
                // Add class for severity highlighting
                if (alert.severity.toLowerCase() === 'critical') {
                    row.classList.add('alert-row-critical');
                } else if (alert.severity.toLowerCase() === 'high') {
                    row.classList.add('alert-row-high');
                } else if (alert.severity.toLowerCase() === 'medium') {
                    row.classList.add('alert-row-medium');
                }
                
                if (alert.new) {
                    row.classList.add('alert-row-new');
                }
                
                row.innerHTML = `
                    <td>${alert.timestamp}</td>
                    <td>${alert.rule_name}</td>
                    <td>${alert.source}</td>
                    <td>${getSeverityBadge(alert.severity)}</td>
                    <td>${getStatusBadge(alert.acknowledged)}</td>
                    <td>${alert.mitre_tactic || 'Unknown'}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary view-alert-btn" 
                                data-bs-toggle="modal" 
                                data-bs-target="#alertDetailModal"
                                data-alert-id="${alert.id}">
                            <i class="bi bi-eye"></i>
                        </button>
                        
                        ${!alert.acknowledged ? `
                        <button class="btn btn-sm btn-outline-success acknowledge-btn ms-1" 
                                data-alert-id="${alert.id}">
                            <i class="bi bi-check"></i>
                        </button>
                        ` : ''}
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
            
            // Add event listeners for acknowledge buttons
            document.querySelectorAll('.acknowledge-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const alertId = this.getAttribute('data-alert-id');
                    acknowledgeAlert(alertId, success => {
                        if (success) fetchAlerts();
                    });
                });
            });
        })
        .catch(handleApiError);
}

// Get recommended actions based on alert type
function getRecommendedActions(alert) {
    const ruleName = alert.rule_name.toLowerCase();
    const actions = [];
    
    // Common action for all alerts
    actions.push('Review the full log entries related to this alert for additional context.');
    
    if (ruleName.includes('brute force')) {
        actions.push('Check authentication logs for the source IP address.');
        actions.push('Consider temporarily blocking the source IP if attacks persist.');
        actions.push('Verify that account lockout policies are properly configured.');
        actions.push('Ensure that password complexity requirements are enforced.');
    } 
    else if (ruleName.includes('port scan')) {
        actions.push('Verify that unnecessary ports and services are disabled.');
        actions.push('Consider adding the source IP to a watchlist or blocklist.');
        actions.push('Check if the scanning is coming from a known penetration testing tool.');
    }
    else if (ruleName.includes('web attack')) {
        actions.push('Examine web server logs for the specific attack pattern.');
        actions.push('Verify that web application firewalls are correctly configured.');
        actions.push('Check for patches or updates needed for the web application.');
    }
    else if (ruleName.includes('ids')) {
        actions.push('Examine the full IDS alert details for attack specifics.');
        actions.push('Correlate with other logs to determine if the attack was successful.');
        actions.push('Check if the affected system needs security patches.');
    }
    else if (ruleName.includes('suspicious process')) {
        actions.push('Investigate the process and command line arguments.');
        actions.push('Run a malware scan on the affected system.');
        actions.push('Check for unauthorized changes to system files.');
    }
    else if (ruleName.includes('data exfiltration')) {
        actions.push('Identify what data may have been exfiltrated.');
        actions.push('Isolate the affected system for forensic analysis.');
        actions.push('Consider immediate incident response procedures.');
        actions.push('Prepare for potential data breach notification requirements.');
    }
    
    // Add generic actions for any alert type
    actions.push('Document your investigation and findings.');
    
    return actions;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initAlertsPage);
""")

    # Events JavaScript
    with open(os.path.join(config.JS_DIR, "events.js"), "w") as f:
        f.write(r"""// Events page specific JavaScript

// Current filter settings
let currentFilters = {
    source: null,
    search: ''
};

// Initialize events page
function initEventsPage() {
    fetchEvents();
    
    // Set up refresh button
    document.getElementById('refresh-events').addEventListener('click', fetchEvents);
    
    // Set up source filter buttons
    document.getElementById('source-all').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = null;
        fetchEvents();
    });
    
    document.getElementById('source-auth').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = 'auth_log';
        fetchEvents();
    });
    
    document.getElementById('source-web').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = 'web_log';
        fetchEvents();
    });
    
    document.getElementById('source-firewall').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = 'firewall_log';
        fetchEvents();
    });
    
    document.getElementById('source-ids').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = 'ids_log';
        fetchEvents();
    });
    
    document.getElementById('source-windows').addEventListener('click', function() {
        setActiveButton(this);
        currentFilters.source = 'windows_log';
        fetchEvents();
    });
    
    // Set up search functionality
    document.getElementById('search-btn').addEventListener('click', function() {
        currentFilters.search = document.getElementById('event-search').value.trim();
        fetchEvents();
    });
    
    document.getElementById('event-search').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            currentFilters.search = this.value.trim();
            fetchEvents();
        }
    });
    
    // Set up event detail modal
    const eventDetailModal = document.getElementById('eventDetailModal');
    eventDetailModal.addEventListener('show.bs.modal', function(event) {
        const button = event.relatedTarget;
        const eventData = JSON.parse(button.getAttribute('data-event'));
        
        // Fill in event details
        document.getElementById('event-detail-source').textContent = eventData.source;
        document.getElementById('event-detail-timestamp').textContent = eventData.timestamp;
        document.getElementById('event-detail-log').textContent = eventData.content;
        
        // Extract IP addresses from the log
        const ipAddresses = extractIPAddresses(eventData.content);
        document.getElementById('event-detail-ip').textContent = ipAddresses.length > 0 ? ipAddresses.join(', ') : 'None detected';
        
        // Event analysis based on source and content
        const analysisDiv = document.getElementById('event-analysis-content');
        analysisDiv.innerHTML = '';
        
        const analysis = analyzeEvent(eventData);
        if (analysis.length > 0) {
            analysis.forEach(item => {
                const p = document.createElement('p');
                p.textContent = item;
                analysisDiv.appendChild(p);
            });
        } else {
            analysisDiv.innerHTML = '<p>No specific insights for this event.</p>';
        }
    });
}

// Set active button
function setActiveButton(button) {
    document.querySelectorAll('#source-all, #source-auth, #source-web, #source-firewall, #source-ids, #source-windows').forEach(btn => {
        btn.classList.remove('active');
    });
    
    button.classList.add('active');
}

// Fetch events with current filters
function fetchEvents() {
    // Build query string
    let queryParams = new URLSearchParams();
    
    if (currentFilters.source !== null) {
        queryParams.append('source', currentFilters.source);
    }
    
    // Fetch events
    fetch(`/api/events?${queryParams.toString()}`)
        .then(response => response.json())
        .then(events => {
            // Filter by search term if provided
            if (currentFilters.search) {
                const searchTerm = currentFilters.search.toLowerCase();
                events = events.filter(event => 
                    event.source.toLowerCase().includes(searchTerm) ||
                    event.content.toLowerCase().includes(searchTerm)
                );
            }
            
            // Update events count
            document.getElementById('events-count').textContent = events.length;
            
            // Populate table
            const tableBody = document.getElementById('events-table');
            
            if (events.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="4" class="text-center">No events found matching your criteria</td></tr>';
                return;
            }
            
            tableBody.innerHTML = '';
            
            events.forEach(event => {
                const row = document.createElement('tr');
                row.classList.add('event-row');
                
                // Truncate long event content
                let content = event.content;
                if (content.length > 80) {
                    content = content.substring(0, 77) + '...';
                }
                
                // Check for potential security relevance
                let rowClass = '';
                if (isSecurityRelevant(event)) {
                    rowClass = 'table-warning';
                }
                
                if (rowClass) {
                    row.classList.add(rowClass);
                }
                
                row.innerHTML = `
                    <td>${event.timestamp}</td>
                    <td>${event.source}</td>
                    <td class="truncate">${content}</td>
                    <td>
                        <button class="btn btn-sm btn-outline-info" 
                                data-bs-toggle="modal" 
                                data-bs-target="#eventDetailModal"
                                data-event='${JSON.stringify(event)}'>
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                `;
                
                tableBody.appendChild(row);
            });
        })
        .catch(handleApiError);
}

// Check if an event is likely security relevant
function isSecurityRelevant(event) {
    const content = event.content.toLowerCase();
    
    // Keywords that might indicate security relevance
    const securityKeywords = [
        'failed', 'failure', 'error', 'blocked', 'denied', 'unauthorized',
        'invalid', 'attack', 'malicious', 'exploit', 'vulnerability',
        'infection', 'malware', 'virus', 'trojan', 'ransomware',
        'brute force', 'injection', 'xss', 'sql', 'overflow', 'scan'
    ];
    
    return securityKeywords.some(keyword => content.includes(keyword));
}

// Extract IP addresses from a string
function extractIPAddresses(text) {
    const ipv4Regex = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g;
    const matches = text.match(ipv4Regex) || [];
    return [...new Set(matches)]; // Remove duplicates
}

// Analyze event for insights
function analyzeEvent(event) {
    const insights = [];
    const content = event.content.toLowerCase();
    const source = event.source;
    
    if (source === 'auth_log') {
        if (content.includes('failed password')) {
            insights.push('Authentication failure detected - could indicate brute force attempt if multiple failures occur.');
        }
        if (content.includes('accepted password')) {
            insights.push('Successful authentication.');
        }
        if (content.includes('invalid user')) {
            insights.push('Attempt to authenticate with a non-existent username - common in brute force attacks.');
        }
    }
    else if (source === 'firewall_log') {
        if (content.includes('blocked')) {
            insights.push('Traffic blocked by firewall - review for potential security implications.');
        }
        if (content.includes('size=') && /size=\d{7,}/.test(content)) {
            insights.push('Large data transfer detected - possible data exfiltration.');
        }
    }
    else if (source === 'web_log') {
        if (content.includes('404')) {
            insights.push('404 Not Found response - could be normal or part of reconnaissance/scanning if occurring frequently.');
        }
        if (content.includes('403')) {
            insights.push('403 Forbidden response - access denied to restricted resource.');
        }
        if (content.includes('500')) {
            insights.push('500 Server Error - application error which could be related to an attack or misconfiguration.');
        }
        if (/get .+\.(php|asp|aspx)/.test(content)) {
            insights.push('Access to server-side script detected.');
        }
        if (content.includes("'") || content.includes('union select') || content.includes('or 1=1')) {
            insights.push('Potential SQL injection attempt detected.');
        }
        if (content.includes('<script>') || content.includes('onerror=') || content.includes('alert(')) {
            insights.push('Potential XSS (Cross-Site Scripting) attempt detected.');
        }
    }
    else if (source === 'ids_log') {
        if (content.includes('scan')) {
            insights.push('Network scanning activity detected by IDS.');
        }
        if (content.includes('web-attack')) {
            insights.push('Web application attack detected by IDS - review attack details and affected systems.');
        }
        if (content.includes('malware')) {
            insights.push('Potential malware activity detected by IDS - isolate affected systems immediately.');
        }
    }
    else if (source === 'windows_log') {
        if (content.includes('process:') && (content.includes('powershell') || content.includes('cmd.exe'))) {
            insights.push('Command shell process execution detected - review command arguments for suspicious activity.');
        }
        if (content.includes('eventid 4688')) {
            insights.push('New process creation detected - standard Windows security audit event.');
        }
        if (content.includes('eventid 4663') && content.includes('file access:')) {
            insights.push('File access audit event - verify that access to sensitive files is authorized.');
        }
    }
    
    return insights;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initEventsPage);
""")

    # Settings JavaScript
    with open(os.path.join(config.JS_DIR, "settings.js"), "w") as f:
        f.write(r"""// Settings page specific JavaScript

// Initialize settings page
function initSettingsPage() {
    // Save state button
    document.getElementById('save-state-btn').addEventListener('click', function() {
        fetch('/api/save_state', {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert('SIEM state saved successfully', 'success');
            } else {
                showAlert('Failed to save SIEM state: ' + (data.error || 'Unknown error'), 'danger');
            }
        })
        .catch(error => {
            handleApiError(error);
        });
    });
    
    // Load state button
    document.getElementById('load-state-btn').addEventListener('click', function() {
        if (confirm('Loading state will replace current SIEM status. Continue?')) {
            fetch('/api/load_state', {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showAlert('SIEM state loaded successfully', 'success');
                } else {
                    showAlert('Failed to load SIEM state: ' + (data.error || 'Unknown error'), 'danger');
                }
            })
            .catch(error => {
                handleApiError(error);
            });
        }
    });
    
    // Reset alerts button
    document.getElementById('reset-alerts-btn').addEventListener('click', function() {
        if (confirm('This will delete all current alerts. This action cannot be undone. Continue?')) {
            // This would need a backend API endpoint
            showAlert('Alert reset functionality is not implemented in this demo', 'warning');
        }
    });
    
    // Thresholds form
    document.getElementById('thresholds-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        // This would need a backend API endpoint
        showAlert('Threshold update functionality is not implemented in this demo', 'warning');
    });
    
    // Attack simulation settings
    document.getElementById('apply-simulation-settings').addEventListener('click', function() {
        // This would need a backend API endpoint
        showAlert('Simulation settings functionality is not implemented in this demo', 'warning');
    });
}

// Show alert on the page
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the top of the page
    const firstCard = document.querySelector('.card');
    firstCard.parentNode.insertBefore(alertDiv, firstCard);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initSettingsPage);
""")

def generate_static_files():
    """Generate all static files for the web interface"""
    logging.info("Generating static files for the web interface")
    create_directory_structure()
    create_template_files()
    create_css_files()
    create_js_files()
    logging.info("Static file generation complete")


if __name__ == "__main__":
    # Stand-alone test
    logging.basicConfig(level=logging.INFO)
    generate_static_files()
    print("Static files generated successfully")