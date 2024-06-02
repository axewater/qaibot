import asyncio

async def grab_ntp_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        writer.write(b'\x1b' + 47 * b'\0')
        await writer.drain()
        banner = await asyncio.wait_for(reader.read(1024), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.hex()
    except:
        return ''