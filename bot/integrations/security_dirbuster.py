import argparse
import json
import requests
import socket
import ssl
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_port_open(host, port):
    logging.info(f"Checking if port {port} is open on {host}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex((host, port))
    sock.close()
    if result == 0:
        logging.info(f"Port {port} is open on {host}")
    else:
        logging.info(f"Port {port} is not open on {host}")
    return result == 0

def is_ssl_required(host, port):
    logging.info(f"Checking if SSL is required for {host}:{port}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port)) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                logging.info(f"SSL is required for {host}:{port}")
                return True
    except ssl.SSLError:
        logging.info(f"SSL is not required for {host}:{port}")
        return False

def dirbuster(host, port, urls_file):
    protocol = "https" if is_ssl_required(host, port) else "http"
    base_url = f"{protocol}://{host}:{port}"
    logging.info(f"Using base URL: {base_url}")

    logging.info(f"Loading target directories from {urls_file}")
    with open(urls_file) as f:
        data = json.load(f)
        target_directories = data["targetdirectories"]
    logging.info(f"Loaded {len(target_directories)} target directories")

    results = []
    for directory in target_directories:
        url = base_url + directory
        logging.info(f"Sending GET request to {url}")
        try:
            response = requests.get(url)
            status_code = response.status_code
            if status_code != 404:
                logging.info(f"Received response with status code {status_code} for {url}")
            result = {
                "url": url,
                "status_code": status_code
            }
            results.append(result)
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while requesting {url}: {str(e)}")
            result = {
                "url": url,
                "error": str(e)
            }
            results.append(result)

    logging.info("Dirbuster scan completed")
    return json.dumps(results, indent=2)

def main():
    parser = argparse.ArgumentParser(description="Dirbuster-like script")
    parser.add_argument("host", help="Target host")
    parser.add_argument("port", type=int, help="Target port")
    parser.add_argument("urls_file", help="Path to the JSON file containing target directories")
    args = parser.parse_args()

    if not is_port_open(args.host, args.port):
        logging.error(f"Port {args.port} is not open on {args.host}. Exiting.")
        return

    results = dirbuster(args.host, args.port, args.urls_file)
    print(results)

if __name__ == "__main__":
    main()