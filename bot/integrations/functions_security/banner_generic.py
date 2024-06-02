import asyncio

async def grab_generic_banner(ip, port, banner_timeout):
    # Method 1: Connect and read a line
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        banner = await asyncio.wait_for(reader.readline(), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        pass

    # Method 2: Connect, send a newline character, and read the response
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        writer.write(b'\r\n')
        await writer.drain()
        banner = await asyncio.wait_for(reader.read(1024), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        return ''