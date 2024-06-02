import argparse
import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from ipaddress import ip_address
from urllib.parse import urlparse
import socket
import aiohttp

# Configuration
DEFAULT_TIMEOUT = 1
DEFAULT_MAX_THREADS = 100
DEFAULT_SERVICES_FILE = 'bot/integrations/default_ports.json'
DEFAULT_OUTPUT_FORMAT = 'table'
DEFAULT_LOGGING_LEVEL = logging.INFO

class PortScanner:
    def __init__(self, services_file, timeout, max_threads):
        self.services_file = services_file
        self.timeout = timeout
        self.max_threads = max_threads
        self.services = self.load_services()

    def load_services(self):
        try:
            with open(self.services_file, 'r') as file:
                data = json.load(file)
                return [(service['name'], service['port'], service['protocol']) for service in data['services']]
        except Exception as e:
            logging.error(f"Failed to read or parse services file: {e}")
            return []

    async def scan_port(self, ip, port, protocol):
        try:
            if protocol == 'tcp':
                connector = aiohttp.TCPConnector(limit=1, enable_cleanup_closed=True)
                async with aiohttp.ClientSession(connector=connector) as session:
                    try:
                        async with session.get(f'http://{ip}:{port}', timeout=self.timeout) as response:
                            return 'open'
                    except (aiohttp.ClientError, asyncio.TimeoutError):
                        return 'closed'
            else:
                # Implement UDP scanning logic here
                pass
        except Exception as e:
            logging.error(f"Error scanning {ip}:{port}/{protocol}: {e}")
            return 'error'

    async def scan_ip(self, ip):
        num_ports = len(self.services)
        logging.info(f"Starting scan of {num_ports} ports on {ip}")
        results = {}
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            loop = asyncio.get_running_loop()
            tasks = []
            for i, (service, port, protocol) in enumerate(self.services, start=1):
                task = loop.run_in_executor(executor, asyncio.run, self.scan_port(ip, port, protocol))
                tasks.append(task)
                if i % 100 == 0 or i == num_ports:
                    logging.info(f"Scanned {i}/{num_ports} ports...")
            for (service, port, protocol), result in zip(self.services, await asyncio.gather(*tasks)):
                results[port] = {'status': result, 'service': service, 'protocol': protocol}
        logging.info(f"Scan completed on {ip}")
        return results

def parse_ports(port_range):
    return [port for start, end in (map(int, part.split('-')) for part in port_range.split(',')) for port in range(start, end+1)]

def main():
    parser = argparse.ArgumentParser(description='Perform a port scan on specified IP addresses or domains.')
    parser.add_argument('addresses', nargs='+', help='IP addresses or domains to scan')
    parser.add_argument('--port', type=str, help='Specify custom ports or ranges (e.g., 80,100-110)')
    parser.add_argument('--timeout', type=float, default=DEFAULT_TIMEOUT, help='Timeout for each port scan (default: 1)')
    parser.add_argument('--max-threads', type=int, default=DEFAULT_MAX_THREADS, help='Maximum number of threads to use (default: 100)')
    parser.add_argument('--services-file', type=str, default=DEFAULT_SERVICES_FILE, help='JSON file containing services and ports (default: default_ports.json)')
    parser.add_argument('--format', choices=['table', 'json'], default=DEFAULT_OUTPUT_FORMAT, help='Output format (default: table)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else DEFAULT_LOGGING_LEVEL, format='%(asctime)s - %(levelname)s - %(message)s')

    scanner = PortScanner(args.services_file, args.timeout, args.max_threads)

    for address in args.addresses:
        try:
            ip = str(ip_address(address))
        except ValueError:
            parsed_url = urlparse(address)
            hostname = parsed_url.netloc or parsed_url.path
            try:
                ip = socket.gethostbyname(hostname)
            except socket.gaierror:
                logging.error(f"Failed to resolve {address}")
                continue

        if args.port:
            services = [(f"Custom-{port}", port, 'tcp') for port in parse_ports(args.port)]
        else:
            services = scanner.services

        results = asyncio.run(scanner.scan_ip(ip))

        if args.format == 'json':
            print(json.dumps(results, indent=4))
        else:
            print(f"Scan Results for {ip}:")
            for port, info in results.items():
                print(f"  {port}/{info['protocol']} ({info['service']}): {info['status']}")

            open_ports = [str(port) for port, info in results.items() if info['status'] == 'open']
            num_open_ports = len(open_ports)
            if num_open_ports > 0:
                print(f"QAI's drones found ({num_open_ports}) open ports on host {ip}: {','.join(open_ports)}")
            else:
                print(f"QAI's drones found no open ports on host {ip}.")

if __name__ == "__main__":
    main()