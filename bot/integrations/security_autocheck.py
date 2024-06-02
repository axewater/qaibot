import json
from security_portscan import PortScanner
from security_sshlogin import test_ssh_login, load_credentials, DEFAULT_CREDENTIALS_FILE
from security_dirbuster import dirbuster
import argparse
import asyncio
import json
import logging
import aiohttp
import ssl
import datetime
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_address
from urllib.parse import urlparse
import socket


# Configuration
DEFAULT_TIMEOUT = 1
DEFAULT_BANNER_TIMEOUT = 1
DEFAULT_MAX_THREADS = 100
DEFAULT_SERVICES_FILE = 'bot/integrations/default_ports.json'
DEFAULT_OUTPUT_FORMAT = 'table'
DEFAULT_LOGGING_LEVEL = logging.INFO


def security_autocheck(target_host):
    # Step 1: Run the port scanner
    scanner = PortScanner(DEFAULT_SERVICES_FILE, DEFAULT_TIMEOUT, DEFAULT_BANNER_TIMEOUT, DEFAULT_MAX_THREADS)
    port_scan_results = asyncio.run(scanner.scan_ip(target_host))

    open_ports = [port for port, info in port_scan_results.items() if info['status'] == 'open']

    # Step 2: Check for open ports and run respective tools
    report = {
        'target_host': target_host,
        'port_scan': port_scan_results,
        'ssh_login_attempts': [],
        'dirbuster_results': []
    }

    # Check for SSH (port 22)
    if 22 in open_ports:
        credentials, error = load_credentials(DEFAULT_CREDENTIALS_FILE)
        if error:
            report['ssh_login_attempts'].append({'error': error})
        elif credentials:
            for username, password in credentials:
                success, error = test_ssh_login(target_host, 22, username, password)
                report['ssh_login_attempts'].append({
                    'username': username,
                    'password': password,
                    'success': success,
                    'error': error
                })

    # Check for HTTP/HTTPS (port 80/443)
    if 80 in open_ports or 443 in open_ports:
        port = 443 if 443 in open_ports else 80
        dirbuster_results = dirbuster(target_host, port, 'bot/integrations/default_directories.json')
        report['dirbuster_results'] = json.loads(dirbuster_results)

    # Step 3: Generate the final report
    return json.dumps(report, indent=2)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run security autocheck on a target host")
    parser.add_argument("target_host", help="Target host to scan")
    args = parser.parse_args()

    final_report = security_autocheck(args.target_host)
    print(final_report)
