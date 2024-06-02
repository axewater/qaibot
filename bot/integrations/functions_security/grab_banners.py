# grab_banners.py
import asyncio
import aiohttp
import ssl
import logging
import argparse
from datetime import datetime
import sys, os
# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from .banner_generic import grab_generic_banner
from .banner_ftp import grab_ftp_banner
from .banner_ssh import grab_ssh_banner
from .banner_telnet import grab_telnet_banner
from .banner_http import grab_http_banner
from .banner_time import grab_time_banner
from .banner_smtp import grab_smtp_banner
from .banner_smtps import grab_smtps_banner
from .banner_domain import grab_domain_banner
from .banner_https import grab_https_banner
from .banner_imap import grab_imap_banner
from .banner_pop3 import grab_pop3_banner
from .banner_ntp import grab_ntp_banner
from .banner_imaps import grab_imaps_banner
from .banner_msrdp import grab_msrdp_banner
from .banner_mysql import grab_mysql_banner
from .banner_mssqls import grab_mssqls_banner
from .banner_oracle import grab_oracle_banner
from .banner_pop3s import grab_pop3s_banner
from .banner_proxy import grab_proxy_banner

async def grab_banner(ip, port, protocol, banner_timeout=2):
    banner = ''
    logging.info(f"Grabbing banner for {ip}:{port}/{protocol}...")
    # protocol-specific methods
    if protocol == 'tcp':
        if port == 21:
            banner = await grab_ftp_banner(ip, port, banner_timeout)
        elif port == 80:
            banner = await grab_http_banner(ip, port, banner_timeout)
        elif port == 443:
            banner = await grab_https_banner(ip, port, banner_timeout)
        elif port == 22:
            banner = await grab_ssh_banner(ip, port, banner_timeout)
        elif port == 23:
            banner = await grab_telnet_banner(ip, port, banner_timeout)
        elif port == 25:
            banner = await grab_smtp_banner(ip, port, banner_timeout)
        elif port == 37:
            banner = await grab_time_banner(ip, port, banner_timeout)
        elif port == 53:
            banner = await grab_domain_banner(ip, port, banner_timeout)
        elif port == 110:
            banner = await grab_pop3_banner(ip, port, banner_timeout)
        elif port == 123:
            banner = await grab_ntp_banner(ip, port, banner_timeout)
        elif port == 143:
            banner = await grab_imap_banner(ip, port, banner_timeout)
        elif port == 465:
            banner = await grab_smtps_banner(ip, port, banner_timeout)
        elif port == 993:
            banner = await grab_imaps_banner(ip, port, banner_timeout)
        elif port == 995:
            banner = await grab_pop3s_banner(ip, port, banner_timeout)
        elif port == 3306:
            banner = await grab_mysql_banner(ip, port, banner_timeout)
        elif port == 3389:
            banner = await grab_msrdp_banner(ip, port, banner_timeout)
        elif port == 1433:
            banner = await grab_mssqls_banner(ip, port, banner_timeout)
        elif port == 1521:
            banner = await grab_oracle_banner(ip, port, banner_timeout)
        elif port in [8080, 3128, 1080]:
            banner = await grab_proxy_banner(ip, port, banner_timeout)
        else:
            # Generic method for unknown ports
            banner = await grab_generic_banner(ip, port, banner_timeout)
    else:
        # Implement UDP banner grabbing logic here if needed
        pass

    return banner


def main():
    parser = argparse.ArgumentParser(description='Grab service banners from IP/port combinations.')
    parser.add_argument('-i', '--ip', help='Target IP address')
    parser.add_argument('-p', '--port', type=int, help='Target port number')
    parser.add_argument('-s', '--service', help='Target service (e.g., ftp, ssh, telnet)')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Banner grab timeout in seconds (default: 5)')
    parser.add_argument('-a', '--all', action='store_true', help='Perform all banner checks')
    args = parser.parse_args()
    
    if not args.all and (not args.ip or not args.port or not args.service):
        parser.print_help()
        return

    banner_timeout = args.timeout

    if args.all:
        services = ['ftp', 'ssh', 'telnet', 'smtp', 'time', 'domain', 'http', 'https', 'pop3', 'ntp', 'imap', 'smtps',
                    'imaps', 'pop3s', 'mysql', 'msrdp', 'ms-sql-s', 'oracle', 'proxy']
        for service in services:
            banner = asyncio.run(grab_banner(args.ip, args.port, service, banner_timeout))
            print(f"Service: {service}, Banner: {banner}")
    else:
        banner = asyncio.run(grab_banner(args.ip, args.port, args.service, banner_timeout))
        print(f"Service: {args.service}, Banner: {banner}")

if __name__ == '__main__':
    main()