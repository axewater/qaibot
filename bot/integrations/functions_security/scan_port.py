# scan_port.py
import aiohttp
import asyncio
import logging

async def scan_port(ip, port, protocol, timeout):
    logging.debug(f"Scanning {ip}:{port}/{protocol} with timeout {timeout}")
    try:
        if protocol == 'tcp':
            connector = aiohttp.TCPConnector(limit=1, enable_cleanup_closed=True)
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.get(f'http://{ip}:{port}', timeout=timeout) as response:
                        return 'open'
                except (aiohttp.ClientError, asyncio.TimeoutError):
                    return 'closed'
        else:
            # Implement UDP scanning logic here
            pass
    except Exception as e:
        logging.error(f"Error scanning {ip}:{port}/{protocol}: {e}")
        return 'error'