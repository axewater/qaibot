import os
import subprocess
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scan(target):
    try:
        # Determine the correct command based on the operating system
        if sys.platform.startswith('win'):
            command = ["where", "nmap.exe"]
        else:
            command = ["which", "nmap"]

        # Check if nmap is available on the system
        nmap_path = subprocess.check_output(command, stderr=subprocess.STDOUT).decode("utf-8").strip().split('\n')[0]
        if not nmap_path:
            logging.error("Nmap is not installed or not in the system path. Please install nmap.")
            return
    except subprocess.CalledProcessError:
        logging.error("Nmap binary not found in the system path. Please ensure nmap is installed.")
        return

    # Normalize the path to handle different OS path conventions
    nmap_path = os.path.normpath(nmap_path)
    logging.info(f"Using nmap binary at: {nmap_path}")

    # Check if the nmap binary can be executed
    if not os.access(nmap_path, os.X_OK):
        logging.error(f"The nmap binary at {nmap_path} does not have execution permissions.")
        return

    try:
        # Run the nmap command and capture the output
        print(f"Scanning {target} with nmap...")
        process = subprocess.Popen([nmap_path, "-sV", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nmap_output, nmap_errors = process.communicate()
        nmap_output = nmap_output.decode("utf-8")
        if process.returncode != 0:
            logging.error(f"Nmap scan failed with errors: {nmap_errors.decode('utf-8')}")
            return
        if "failed to resolve" in nmap_output.lower():
            logging.error("Nmap scan failed, target could not be resolved.")
            return
    except subprocess.CalledProcessError as e:
        logging.error(f"Error during nmap scan: {e.output.decode('utf-8')}")
        return
    except FileNotFoundError:
        logging.error("Failed to execute nmap. Ensure the nmap path is correct and accessible.")
        return

    # Process and log the nmap output
    lines = nmap_output.split("\n")
    found_report = False
    for line in lines:
        if "Nmap scan report" in line:
            logging.info(f"Found Nmap scan report: {line}")
            found_report = True
            break
    if not found_report:
        logging.warning("No Nmap scan report found.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.info("Usage: python scan_nmap.py <target>")
    else:
        scan(sys.argv[1])
