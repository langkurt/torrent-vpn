import json
import os
import shutil
import time
import requests

# VirusTotal API configuration
API_URL = "https://www.virustotal.com/api/v3/files"

# Load API key from external configuration
CONFIG_PATH = "/root/env.json"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Configuration file not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as config_file:
    config = json.load(config_file)

API_KEY = config.get("virustotal_api_key")
if not API_KEY:
    raise ValueError("API key not found in configuration file")

# Directories
DOWNLOAD_DIR = "/root/downloads"  # The torrent download folder
SAFE_DIR = "/root/safe_downloads"  # The folder for clean files

# Function to upload and scan a file with VirusTotal
def scan_file(file_path):
    with open(file_path, "rb") as file:
        response = requests.post(
            API_URL,
            headers={"x-apikey": API_KEY},
            files={"file": file}
        )
    return response

# Monitor and scan downloaded files
def monitor_and_scan():
    backoff_time = 15  # Initial backoff time in seconds

    while True:
        for filename in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            if os.path.isfile(file_path):
                print(f"Scanning {filename}...")

                # Attempt to scan the file
                response = scan_file(file_path)

                if response.status_code == 429:  # Too many requests
                    print("Rate limit exceeded. Backing off...")
                    time.sleep(backoff_time)
                    backoff_time = min(backoff_time * 2, 300)  # Exponential backoff, max 5 minutes
                    continue
                elif response.status_code != 200:
                    print(f"Error scanning {filename}: {response.status_code}, {response.text}")
                    continue

                # Reset backoff time on success
                backoff_time = 15

                # Process the response
                result = response.json()
                scan_id = result.get("data", {}).get("id")
                if not scan_id:
                    print(f"Error: Unable to retrieve scan ID for {filename}")
                    continue

                # Get the scan result
                report_url = f"{API_URL}/{scan_id}"
                report_response = requests.get(
                    report_url, headers={"x-apikey": API_KEY}
                )
                report = report_response.json()
                malicious = report.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0)

                if malicious == 0:
                    print(f"{filename} is clean. Moving to {SAFE_DIR}.")
                    # Use shutil.move instead of os.rename
                    shutil.move(file_path, os.path.join(SAFE_DIR, filename))
                else:
                    print(f"{filename} is malicious. Deleting file.")
                    os.remove(file_path)

        time.sleep(10)  # Check for new files every 10 seconds

if __name__ == "__main__":
    print("Starting VirusTotal file scanner process. ")
    os.makedirs(SAFE_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    monitor_and_scan()