import asyncio

async def grab_ssh_banner(ip, port, banner_timeout):
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(ip, port), timeout=banner_timeout)
        writer.write(b'SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.8\r\n')
        await writer.drain()
        banner = await asyncio.wait_for(reader.read(1024), timeout=banner_timeout)
        writer.close()
        await writer.wait_closed()
        return banner.decode(errors='ignore').strip()
    except:
        return ''