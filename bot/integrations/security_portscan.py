# bot/integrations/security_portscan.py

import logging
import socket
import sys
import re
from urllib.parse import urlparse

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
            else:  # UDP is connectionless, so we just send a dummy packet
                sock.sendto(b'', (ip, port))
                sock.recvfrom(1024)
                logging.info(f"Port {port}/{protocol} on {ip} is open")
                return True
    except socket.timeout:
        logging.warning(f"Timeout occurred while scanning {ip}:{port}/{protocol}")
        return False
    except Exception as e:
        logging.warning(f"security_portscan: Error scanning {ip}:{port}/{protocol}: {e}")
    return False

def perform_scan(ip, services):
    logging.info(f"Starting scan of {len(services)} ports on {ip}")
    results = {}
    logging.info(f"security_portscan: Starting port scan on {ip}")
    for service, port, protocol in services:
        open = scan_port(ip, port, protocol)
        status = 'open' if open else 'closed'
        if status == 'open' or status == 'filtered':  # Assuming filtered status can be determined elsewhere
            results[port] = {'status': status, 'service': service, 'protocol': protocol}
    logging.info("security_portscan: Scan Results:")
    for port, info in results.items():
        logging.info(f"Port {port}/{info['protocol']} ({info['service']}) is {info['status']}")

def validate_and_resolve_input(input):
    # Strip off protocol if present
    parsed_url = urlparse(input)
    hostname = parsed_url.netloc or parsed_url.path

    # Check if it's an IP address or needs DNS resolution
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python security_portscan.py <IP or Domain>")
        sys.exit(1)
    ip_address = sys.argv[1]
    services = parse_services_file('bot/integrations/services.txt')
    resolved_ip = validate_and_resolve_input(ip_address)
    if resolved_ip:
        perform_scan(resolved_ip, services)
    else:
        print("Scanning aborted due to invalid input.")
