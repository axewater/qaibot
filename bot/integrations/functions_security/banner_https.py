import asyncio
import aiohttp
import ssl
import argparse
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import logging

async def grab_https_banner(ip, port, banner_timeout):
    banner = ''
    try:
        logging.info(f"Attempting to retrieve HTTPS certificate for {ip}:{port}")
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        conn = aiohttp.TCPConnector(ssl=ctx)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                logging.info(f"Sending GET request to https://{ip}:{port}")
                async with session.get(f'https://{ip}:{port}', timeout=banner_timeout) as response:
                    logging.info(f"Received response from https://{ip}:{port}")
                    version = f"HTTP {response.version.major}.{response.version.minor}"
                    status = f"{response.status} {response.reason}"
                    server = response.headers.get('Server', '')
                    banner = f"{version} {status}\nServer: {server}"

                    logging.info(f"HTTP version: {version}")
                    logging.info(f"HTTP status: {status}")
                    logging.info(f"Server header: {server}")

                    # Retrieve certificate information
                    # Retrieve certificate information
                    cert_info = ''
                    cert_pem = ssl.get_server_certificate((ip, port))
                    if cert_pem:
                        cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
                        issuer = cert.issuer.rfc4514_string()
                        subject = cert.subject.rfc4514_string()
                        not_before = cert.not_valid_before_utc  # Use not_valid_before_utc
                        not_after = cert.not_valid_after_utc    # Use not_valid_after_utc

                        logging.info(f"Issuer: {issuer}")
                        logging.info(f"Subject: {subject}")
                        logging.info(f"Valid From: {not_before}")
                        logging.info(f"Valid To: {not_after}")

                        cert_info = f"\nCertificate Information:\n"
                        cert_info += f"  Issuer: {issuer}\n"
                        cert_info += f"  Subject: {subject}\n"
                        cert_info += f"  Valid From: {not_before}\n"
                        cert_info += f"  Valid To: {not_after}\n"
                    else:
                        logging.info("No certificate found")

                    banner += cert_info
            except aiohttp.ClientConnectionError as e:
                logging.error(f"ClientConnectionError occurred while grabbing banner for {ip}:{port}/https")
                if e.os_error:
                    logging.error(f"OS Error: {e.os_error}")
                    if e.os_error.errno == 10054:
                        logging.error(f"Connection reset by remote host while grabbing banner for {ip}:{port}/https")
                    else:
                        raise
                else:
                    raise
            except aiohttp.ClientResponseError as e:
                logging.error(f"HTTP error occurred while grabbing banner for {ip}:{port}/https")
                logging.error(f"Status: {e.status}")
                logging.error(f"Message: {e.message}")
            except aiohttp.ClientError as e:
                logging.error(f"An error occurred while grabbing banner for {ip}:{port}/https: {str(e)}")
            except Exception as e:
                logging.error(f"An unexpected error occurred while grabbing banner for {ip}:{port}/https: {str(e)}")
    except Exception as e:
        logging.error(f"An error occurred while retrieving HTTPS certificate for {ip}:{port}: {str(e)}")

    return banner

async def main(ip, port, banner_timeout):
    banner = await grab_https_banner(ip, port, banner_timeout)
    print(f"HTTPS Banner: {banner}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab HTTPS banner from IP/port combination.')
    parser.add_argument('-i', '--ip', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Target port number')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Banner grab timeout in seconds (default: 5)')
    args = parser.parse_args()

    ip = args.ip
    port = args.port
    banner_timeout = args.timeout

    asyncio.run(main(ip, port, banner_timeout))
