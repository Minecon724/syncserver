import asyncio
from websockets.server import serve
import time

op_client = None
blacklist = []
key = "ce475b24576910b6180c14f638492a75cba90ee9ff9ef60d4280ff75a666b857"

async def handler(websocket):

    ip = websocket.remote_address[0]
    if ip in blacklist:
        print(ip + " is blacklisted")
        return

    global op_client

    playing = False
    since = 0
    track = ""
    track_length = 0

    print(ip + " connected")

    async for message in websocket:
        if message == key:
            op_client = websocket
            print(ip + " is OP")
        else:
            prefix, *rest = message.split(' ')
            if prefix == "true" or prefix == "false":
                playing = (prefix == "true")
                end = float(rest[0])
                if op_client is not None:
                    await op_client.send(ip + ' end ' + str(end))
                    await op_client.send(ip + ' active ' + prefix)
            elif prefix.isnumeric():
                track_length = prefix
                track = ' - '.join(' '.join(rest).split(' :'))
                if op_client is not None:
                    await op_client.send(ip + ' total ' + str(track_length))
                    await op_client.send(ip + ' track ' + track)
            else:
                blacklist.append(ip)
                break

async def main():
    async with serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())