import logging
import time
import socket
import traceback
import sys
import threading

import config
import utils
from log_generator import LogGenerator
from siem_core import SIEMCore
import static_generator
import web_server



def shutdown_handler(siem, log_generator):
    """Handle graceful shutdown"""
    try:
        print("\nShutting down SIEM Dashboard...")
        
        # Save SIEM state
        if siem:
            print("Saving SIEM state...")
            siem.save_state()
            print("Stopping SIEM service...")
            siem.stop()
            
        # Stop log generator
        if log_generator:
            print("Stopping log generator...")
            log_generator.stop()
            
        print("Shutdown complete. Goodbye!")
    except Exception as e:
        print(f"Error during shutdown: {e}")

def setup_alert_notification_handler(siem):
    """Set up a thread to notify the web UI of new alerts"""
    def check_for_new_alerts():
        last_alert_count = 0
        while True:
            try:
                current_alert_count = 0
                new_alert = None
                
                # Get the latest alert if there are more alerts than before
                with siem.lock:
                    current_alert_count = len(siem.alerts)
                    if current_alert_count > last_alert_count and siem.alerts:
                        # Find the newest alert with 'new' flag
                        for alert in reversed(siem.alerts):
                            if alert.get('new', False):
                                new_alert = alert.copy()
                                alert['new'] = False  # Clear the new flag
                                break
                
                # Emit notification if we found a new alert
                if new_alert:
                    socketio = web_server.get_socketio_instance()
                    if socketio:
                        new_alert['timestamp'] = utils.format_timestamp(new_alert['timestamp'])
                        socketio.emit('new_alert', new_alert)
                        
                        # Also update stats
                        stats = siem.get_stats()
                        socketio.emit('stats_update', stats)
                        
                last_alert_count = current_alert_count
                
            except Exception as e:
                logging.error(f"Error in alert notification handler: {e}")
            
            # Check every second
            time.sleep(1)
    
    # Start thread
    thread = threading.Thread(target=check_for_new_alerts)
    thread.daemon = True
    thread.start()
    return thread

def main():
    """Main application entry point"""
    try:
        print("Starting SIEM Dashboard...")
        
       
        # Setup logging
        utils.setup_logging()
        logging.info("SIEM Dashboard starting up...")
        
        # Ensure all required directories exist
        utils.ensure_directories_exist()
        
        # Generate static files for web interface
        print("Generating static files...")
        static_generator.generate_static_files()
        
        # Setup log generator
        print("Initializing log generator...")
        log_generator = LogGenerator()
        
        # Setup SIEM system
        print("Initializing SIEM core...")
        siem = SIEMCore()
        
        # Load previous state if available
        print("Loading previous state...")
        siem.load_state()
        
        # Start log generator
        print("Starting log generator...")
        log_generator.start()
        
        # Start SIEM monitoring
        print("Starting SIEM monitoring...")
        siem.start()
        
        # Setup web server
        print("Initializing web server...")
        web_server.initialize_web_server(siem)
        
        # Setup alert notification handler
        setup_alert_notification_handler(siem)
        
        # Start web server (blocking call)
        print(f"Starting web server at http://localhost:{config.WEB_PORT}")
        web_server.start_web_server()
        
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
    finally:
        # Ensure clean shutdown
        shutdown_handler(siem if 'siem' in locals() else None, 
                        log_generator if 'log_generator' in locals() else None)

if __name__ == "__main__":
    main()