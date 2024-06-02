# scan_ip.py
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from .scan_port import scan_port
from .grab_banners import grab_banner

async def scan_ip(ip, services, max_threads, timeout, banner_timeout):
    num_ports = len(services)
    logging.info(f"Starting scan of {num_ports} ports on {ip}")
    results = {}
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        loop = asyncio.get_running_loop()
        tasks = []
        for i, (service, port, protocol) in enumerate(services, start=1):
            task = loop.run_in_executor(executor, asyncio.run, scan_port(ip, port, protocol, timeout))
            tasks.append(task)
            if i % 100 == 0 or i == num_ports:
                logging.info(f"Scanned {i}/{num_ports} ports...")
        for (service, port, protocol), result in zip(services, await asyncio.gather(*tasks)):
            if result == 'open':
                banner = await grab_banner(ip, port, protocol, banner_timeout)
            else:
                banner = ''
            results[port] = {'status': result, 'service': service, 'protocol': protocol, 'banner': banner}
    logging.info(f"Scan completed on {ip}")
    return results