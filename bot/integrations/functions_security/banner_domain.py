import asyncio

async def grab_domain_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        writer.write(b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03www\x06google\x03com\x00\x00\x01\x00\x01')
        await writer.drain()
        banner = await asyncio.wait_for(reader.read(1024), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.hex()
    except:
        return ''