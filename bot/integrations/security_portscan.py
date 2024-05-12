import logging
import socket
import sys
import re
import json
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def validate_and_resolve_input(input):
    parsed_url = urlparse(input)
    hostname = parsed_url.netloc or parsed_url.path

    if re.match(r'^\d{1,3}(\.\d{1,3}){3}$', hostname) and not hostname.endswith('.255'):
        return hostname
    elif '.' in hostname and not re.search(r'[^a-zA-Z0-9.-]', hostname):
        try:
            resolved_ip = socket.gethostbyname(hostname)
            logging.info(f"Resolved {input} to {resolved_ip}")
            return resolved_ip
        except socket.gaierror:
            logging.warning(f"security_portscan: DNS resolution failed for {hostname}")
            return None
    else:
        logging.warning(f"security_portscan: Invalid input: {hostname}")
        return None

def parse_services_file(filepath):
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
        logging.info(f"Loaded {len(services)} services from {filepath}")
    except Exception as e:
        logging.warning(f"security_portscan: Failed to read or parse {filepath}: {e}")
    return services

def scan_port(ip, port, protocol):
    logging.info(f"Scanning {ip}:{port}/{protocol}")
    try:
        socket_type = socket.SOCK_STREAM if protocol == 'tcp' else socket.SOCK_DGRAM
        with socket.socket(socket.AF_INET, socket_type) as sock:
            sock.settimeout(1)
            if protocol == 'tcp':
                result = sock.connect_ex((ip, port))
                if result == 0:
                    logging.info(f"Port {port}/{protocol} on {ip} is open")
                    return True
                else:
                    logging.info(f"Port {port}/{protocol} on {ip} is closed")
            else:
                sock.sendto(b'', (ip, port))
                try:
                    sock.recvfrom(1024)
                    logging.info(f"Port {port}/{protocol} on {ip} is open")
                    return True
                except socket.timeout:
                    logging.info(f"Port {port}/{protocol} on {ip} is closed/firewalled")
                    return False
    except socket.timeout:
        logging.warning(f"Timeout occurred while scanning {ip}:{port}/{protocol}")
        return False
    except Exception as e:
        logging.warning(f"security_portscan: Error scanning {ip}:{port}/{protocol}: {e}")
        if "forcibly closed" in str(e):
            logging.info(f"Port {port}/{protocol} on {ip} is filtered")
            return False
        else:
            logging.info(f"Port {port}/{protocol} on {ip} is closed/firewalled")
            return False
    return False

def perform_scan(ip, services, output_format='table'):
    total_ports = len(services)
    scanned_ports = 0
    open_ports = 0
    closed_ports = 0
    filtered_ports = 0
    logging.info(f"Starting scan of {total_ports} ports on {ip}")
    results = {}
    logging.info(f"security_portscan: Starting port scan on {ip}")
    for service, port, protocol in services:
        scanned_ports += 1
        logging.info(f"Scanning port {scanned_ports} of {total_ports}: {port}/{protocol}")
        open = scan_port(ip, port, protocol)
        status = 'open' if open else 'closed/firewalled'
        if status == 'open':
            open_ports += 1
        elif "firewalled" in status:
            filtered_ports += 1
        else:
            closed_ports += 1
        results[port] = {'status': status, 'service': service, 'protocol': protocol}
    if output_format == 'json':
        print(json.dumps(results, indent=4))
    else:
        logging.info("security_portscan: Scan Results:")
        for port, info in results.items():
            print(f"Port {port}/{info['protocol']} ({info['service']}) is {info['status']}")
    logging.info(f"Scan completed. Total: {total_ports}, Open: {open_ports}, Closed: {closed_ports}, Filtered: {filtered_ports}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Perform a port scan on a specified IP or domain.')
    parser.add_argument('address', type=str, help='IP address or domain to scan')
    parser.add_argument('--format', type=str, choices=['table', 'json'], default='table', help='Output format')
    args = parser.parse_args()

    ip_address = args.address
    output_format = args.format
    services = parse_services_file('bot/integrations/services.txt')
    resolved_ip = validate_and_resolve_input(ip_address)
    if resolved_ip:
        perform_scan(resolved_ip, services, output_format)
    else:
        print("Scanning aborted due to invalid input.")
