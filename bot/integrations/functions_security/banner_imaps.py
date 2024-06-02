import asyncio
import ssl

async def grab_imaps_banner(ip, port, banner_timeout):
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port, ssl=ssl_context), timeout=banner_timeout)
        banner = await asyncio.wait_for(reader.readline(), timeout=banner_timeout)
        writer.write(b'a001 LOGOUT\r\n')
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        return ''