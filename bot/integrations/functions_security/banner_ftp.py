import asyncio

async def grab_ftp_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        banner = await asyncio.wait_for(reader.readline(), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        return ''