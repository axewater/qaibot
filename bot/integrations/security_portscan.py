import argparse
import logging
import socket
import sys
import re
import json
from urllib.parse import urlparse

import select

def parse_port_argument(port_arg):
    ports = []
    parts = port_arg.split(',')
    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            ports.extend(range(start, end + 1))
        else:
            ports.append(int(part))
    return ports

def setup_logging(verbose):
    if verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_and_resolve_input(input, verbose):
    parsed_url = urlparse(input)
    hostname = parsed_url.netloc or parsed_url.path

    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname) and not hostname.endswith('.255'):
        return hostname
    elif '.' in hostname and not re.search(r'[^a-zA-Z0-9.-]', hostname):
        try:
            resolved_ip = socket.gethostbyname(hostname)
            if verbose:
                logging.debug(f"Resolved {input} to {resolved_ip}")
            return resolved_ip
        except socket.gaierror:
            if verbose:
                logging.debug(f"DNS resolution failed for {hostname}")
            return None
    else:
        if verbose:
            logging.debug(f"Invalid input: {hostname}")
        return None

def parse_services_file(filepath, verbose):
    services = []
    try:
        with open(filepath, 'r') as file:
            for line in file:
                if line.strip() and not line.startswith('#'):
                    parts = line.split()
                    service_name = parts[0]
                    port_protocol = parts[1].split('/')
                    port = int(port_protocol[0])
                    protocol = port_protocol[1]
                    services.append((service_name, port, protocol))
        if verbose:
            logging.debug(f"Loaded {len(services)} services from {filepath}")
    except Exception as e:
        if verbose:
            logging.debug(f"Failed to read or parse {filepath}: {e}")
    return services



def scan_port(ip, port, protocol, verbose):
    if verbose:
        logging.info(f"Scanning {ip}:{port}/{protocol}")
    try:
        socket_type = socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM
        with socket.socket(socket.AF_INET, socket_type) as sock:
            sock.settimeout(1)
            if protocol == 'tcp':
                result = sock.connect_ex((ip, port))
                if result == 0:
                    if verbose:
                        logging.debug(f"Port {port}/{protocol} on {ip} is open")
                    return True
                else:
                    if verbose:
                        logging.debug(f"Port {port}/{protocol} on {ip} is closed")
            else:
                sock.sendto(b'', (ip, port))
                try:
                    sock.recvfrom(1024)
                    if verbose:
                        logging.debug(f"Port {port}/{protocol} on {ip} is open")
                    return True
                except socket.timeout:
                    if verbose:
                        logging.debug(f"Port {port}/{protocol} on {ip} is closed/firewalled")
                    return False
    except socket.timeout:
        if verbose:
            logging.debug(f"Timeout occurred while scanning {ip}:{port}/{protocol}")
        return False
    except Exception as e:
        if verbose:
            logging.debug(f"Error scanning {ip}:{port}/{protocol}: {e}")
        if "forcibly closed" in str(e):
            if verbose:
                logging.debug(f"Port {port}/{protocol} on {ip} is filtered")
            return False
        else:
            if verbose:
                logging.debug(f"Port {port}/{protocol} on {ip} is closed/firewalled")
            return False
    return False

def perform_scan(ip, services, output_format='table', verbose=False):
    total_ports = len(services)
    scanned_ports = 0
    open_ports = 0
    closed_ports = 0
    filtered_ports = 0
    if not verbose:
        print(f"Starting scan of {total_ports} ports on {ip}")
    if verbose:
        logging.debug(f"Starting scan of {total_ports} ports on {ip}")
    results = {}
    if verbose:
        logging.debug(f"Starting port scan on {ip}")
    for service, port, protocol in services:
        scanned_ports += 1
        if verbose:
            logging.debug(f"Scanning port {scanned_ports} of {total_ports}: {port}/{protocol}")
        open = scan_port(ip, port, protocol, verbose)
        status = 'open' if open else 'closed/firewalled'
        if status == 'open':
            if not verbose:
                print(f"Port {port}/{protocol} on {ip} is open")
            open_ports += 1
        elif "firewalled" in status:
            filtered_ports += 1
        else:
            closed_ports += 1
        results[port] = {'status': status, 'service': service, 'protocol': protocol}
    if output_format == 'json':
        print(json.dumps(results, indent=4))
    else:
        if verbose:
            logging.debug("Scan Results:")
        for port, info in results.items():
            print(f"Port {port}/{info['protocol']} ({info['service']}) is {info['status']}")
    if verbose:
        logging.debug(f"Scan completed. Total: {total_ports}, Open: {open_ports}, Closed: {closed_ports}, Filtered: {filtered_ports}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Perform a port scan on a specified IP or domain.')
    parser.add_argument('address', type=str, help='IP address or domain to scan')
    parser.add_argument('--port', type=str, help='Specify custom ports or ranges (e.g., 80,100-110)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--format', type=str, choices=['table', 'json'], default='table', help='Output format')
    args = parser.parse_args()

    setup_logging(args.verbose)
    ip_address = args.address
    output_format = args.format
    custom_ports = parse_port_argument(args.port) if args.port else None
    if custom_ports:
        services = [(f"Custom-{port}", port, 'tcp') for port in custom_ports]
    else:
        services = parse_services_file('bot/integrations/services.txt', args.verbose)
    resolved_ip = validate_and_resolve_input(ip_address, args.verbose)
    if resolved_ip:
        perform_scan(resolved_ip, services, output_format, args.verbose)
    else:
        print("Scanning aborted due to invalid input.")
