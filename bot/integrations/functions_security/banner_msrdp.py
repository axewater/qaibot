import asyncio

async def grab_msrdp_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        writer.write(b'\x03\x00\x00\x13\x0e\xe0\x00\x00\x00\x00\x00\x01\x00\x08\x00\x03\x00\x00\x00')
        await writer.drain()
        banner = await asyncio.wait_for(reader.read(1024), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.hex()
    except:
        return ''