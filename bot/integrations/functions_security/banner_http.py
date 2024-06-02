# banner_http.py
import asyncio
import aiohttp
import logging
import argparse

async def grab_http_banner(ip, port, banner_timeout):
    try:
        logging.info(f"Running service specific banner grabber for HTTP on {ip}:{port}")
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{ip}:{port}', timeout=banner_timeout, ssl=False) as response:
                version = f"HTTP {response.version.major}.{response.version.minor}"
                status = f"{response.status} {response.reason}"
                server = response.headers.get('Server', '')
                return f"{version} {status}\nServer: {server}"
    except:
        return ''

async def main(ip, port, banner_timeout):
    banner = await grab_http_banner(ip, port, banner_timeout)
    print(f"HTTP Banner: {banner}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grab HTTP banner from IP/port combination.')
    parser.add_argument('-i', '--ip', required=True, help='Target IP address')
    parser.add_argument('-p', '--port', type=int, required=True, help='Target port number')
    parser.add_argument('-t', '--timeout', type=int, default=5, help='Banner grab timeout in seconds (default: 5)')
    args = parser.parse_args()

    ip = args.ip
    port = args.port
    banner_timeout = args.timeout

    asyncio.run(main(ip, port, banner_timeout))