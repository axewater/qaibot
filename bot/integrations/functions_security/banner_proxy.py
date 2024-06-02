import asyncio
import aiohttp

async def grab_proxy_banner(ip, port, banner_timeout):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://{ip}:{port}', timeout=banner_timeout) as response:
                banner = f"HTTP {response.version} {response.status} {response.reason}\r\n"
                banner += "\r\n".join([f"{key}: {value}" for key, value in response.headers.items()])
                return banner
    except:
        return ''