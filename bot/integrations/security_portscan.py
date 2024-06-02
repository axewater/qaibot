# security_portscan.py
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

# Import functions from the functions_security subfolder
from functions_security.load_services import load_services
from functions_security.scan_port import scan_port
from functions_security.grab_banners import grab_banner
from functions_security.scan_ip import scan_ip
from functions_security.parse_ports import parse_ports

class PortScanner:
    def __init__(self, services_file, timeout, banner_timeout, max_threads):
        self.services_file = services_file
        self.timeout = timeout
        self.banner_timeout = banner_timeout
        self.max_threads = max_threads
        self.services = load_services(self.services_file)

    async def scan_ip(self, ip, services=None):
        if services is None:
            services = self.services
        return await scan_ip(ip, services, self.max_threads, self.timeout, self.banner_timeout)

def main():
    parser = argparse.ArgumentParser(description='Perform a port scan on specified IP addresses or domains.')
    parser.add_argument('addresses', nargs='+', help='IP addresses or domains to scan')
    parser.add_argument('--port', type=str, help='Specify custom ports or ranges (e.g., 80,100-110)')    
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help='Timeout for each port scan (default: 1)')
    parser.add_argument('--banner-timeout', type=float, default=DEFAULT_BANNER_TIMEOUT, help='Timeout for banner grabbing (default: 2)')
    parser.add_argument('--max-threads', type=int, default=DEFAULT_MAX_THREADS, help='Maximum number of threads to use (default: 100)')
    parser.add_argument('--services-file', type=str, default=DEFAULT_SERVICES_FILE, help='JSON file containing services and ports (default: default_ports.json)')
    parser.add_argument('--format', choices=['table', 'json'], default=DEFAULT_OUTPUT_FORMAT, help='Output format (default: table)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else DEFAULT_LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

    scanner = PortScanner(args.services_file, args.timeout, args.banner_timeout, args.max_threads)
    logging.info(f"Loading services from {args.services_file}")
    for address in args.addresses:
        try:
            logging.info(f"Checking what is {address}")
            ip = str(ip_address(address))
        except ValueError:
            parsed_url = urlparse(address)
            logging.info(f"Resolving {parsed_url.netloc or parsed_url.path}")
            hostname = parsed_url.netloc or parsed_url.path
            try:
                logging.info(f"Resolving hostname {hostname}")
                ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                logging.error(f"Failed to resolve {address}")
                continue

        if args.port:
            logging.info(f"Custom port(s) specified: {args.port}")
            custom_services = [(f"Custom-{port}", port, 'tcp') for port in parse_ports(args.port)]
            logging.info(f"Starting scan of custom ports on {ip}")
            results = asyncio.run(scanner.scan_ip(ip, custom_services))
        else:
            services = scanner.services
            logging.info(f"Starting scan of {len(services)} ports on {ip}")
            results = asyncio.run(scanner.scan_ip(ip))
        

        if args.format == 'json':
            print(json.dumps(results, indent=4))
        else:
            print(f"Scan Results for {ip}:")
            for port, info in results.items():
                print(f"  {port}/{info['protocol']} ({info['service']}): {info['status']}")
                if info['banner']:
                    print(f"    Banner: {info['banner']}")

            print(f"\nQAI's drones found the following open ports on host {ip}:")
            for port, info in results.items():
                if info['status'] == 'open':
                    banner = f" - Banner: {info['banner']}" if info['banner'] else ""
                    print(f"  {port}/{info['protocol']} ({info['service']}){banner}")

if __name__ == "__main__":
    main()
