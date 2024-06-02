import asyncio

async def grab_time_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        banner = await asyncio.wait_for(reader.read(4), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return str(int.from_bytes(banner, byteorder='big'))
    except:
        return ''