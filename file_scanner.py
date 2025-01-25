import json
import os
import shutil
import time
import requests
import logging

# Configure logging
logging.basicConfig(
    filename="/var/log/file_scanner.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

DOWNLOAD_DIR = "/root/downloads"
SAFE_DIR = "/root/safe_downloads"

def scan_file(file_path, retries=3):
    for attempt in range(retries):
        try:
            with open(file_path, "rb") as file:
                response = requests.post(
                    API_URL,
                    headers={"x-apikey": API_KEY},
                    files={"file": file}
                )
            return response
        except requests.RequestException as e:
            logging.warning(f"Attempt {attempt + 1} failed for {file_path}: {e}")
            time.sleep(2)
    raise RuntimeError(f"Failed to scan {file_path} after {retries} attempts")

def monitor_and_scan():
    backoff_time = 15
    while True:
        logging.debug(f"Checking for new files in {DOWNLOAD_DIR}")
        for root, dirs, files in os.walk(DOWNLOAD_DIR):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    logging.info(f"Scanning {file_path}...")
                    try:
                        response = scan_file(file_path)
                    except RuntimeError as e:
                        logging.error(f"Error scanning {file_path}: {e}")
                        continue

                    if response.status_code == 429:
                        logging.warning("Rate limit exceeded. Backing off...")
                        time.sleep(backoff_time)
                        backoff_time = min(backoff_time * 2, 300)
                        continue
                    elif response.status_code != 200:
                        logging.error(f"Error scanning {file_path}: {response.status_code}, {response.text}")
                        continue

                    backoff_time = 15
                    result = response.json()
                    scan_id = result.get("data", {}).get("id")
                    if not scan_id:
                        logging.warning(f"Unable to retrieve scan ID for {file_path}")
                        continue

                    report_url = f"{API_URL}/{scan_id}"
                    report_response = requests.get(
                        report_url, headers={"x-apikey": API_KEY}
                    )
                    report = report_response.json()
                    malicious = report.get("data", {}).get("attributes", {}).get("last_analysis_stats", {}).get("malicious", 0)

                    relative_path = os.path.relpath(file_path, DOWNLOAD_DIR)
                    safe_file_path = os.path.join(SAFE_DIR, relative_path)

                    if malicious == 0:
                        logging.info(f"{file_path} is clean. Moving to {safe_file_path}.")
                        os.makedirs(os.path.dirname(safe_file_path), exist_ok=True)
                        shutil.move(file_path, safe_file_path)
                    else:
                        logging.warning(f"{file_path} is malicious. Deleting file.")
                        os.remove(file_path)

        for root, dirs, files in os.walk(DOWNLOAD_DIR, topdown=False):
            for directory in dirs:
                dir_path = os.path.join(root, directory)
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logging.debug(f"Removed empty directory: {dir_path}")

        time.sleep(10)

if __name__ == "__main__":
    logging.info("Starting VirusTotal file scanner process.")
    os.makedirs(SAFE_DIR, exist_ok=True)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    if not os.access(DOWNLOAD_DIR, os.R_OK):
        logging.error(f"DOWNLOAD_DIR {DOWNLOAD_DIR} is not readable. Exiting.")
        exit(1)
    if not os.access(SAFE_DIR, os.W_OK):
        logging.error(f"SAFE_DIR {SAFE_DIR} is not writable. Exiting.")
        exit(1)
    monitor_and_scan()