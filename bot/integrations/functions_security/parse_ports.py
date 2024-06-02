import logging

def parse_ports(port_input):
    ports = []
    if ',' in port_input:
        logging.info("Parsing port list...")
        port_ranges = port_input.split(',')
        for port_range in port_ranges:
            ports.extend(parse_ports(port_range))
    elif '-' in port_input:
        logging.info("Parsing port range...")
        start_port, end_port = port_input.split('-')
        ports.extend(list(range(int(start_port), int(end_port) + 1)))
    else:
        logging.info("Parsing single port...")
        ports.append(int(port_input))
    
    return ports