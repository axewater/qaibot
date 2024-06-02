import json
import logging

def load_services(services_file):
    try:
        with open(services_file, 'r') as file:
            data = json.load(file)
            return [(service['name'], service['port'], service['protocol']) for service in data['services']]
    except Exception as e:
        logging.error(f"Failed to read or parse services file: {e}")
        return []