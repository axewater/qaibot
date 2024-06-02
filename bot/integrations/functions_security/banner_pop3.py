import asyncio

async def grab_pop3_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        banner = await asyncio.wait_for(reader.readline(), timeout=banner_timeout)
        writer.write(b'QUIT\r\n')
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        return ''