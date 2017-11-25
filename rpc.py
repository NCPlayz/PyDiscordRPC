import asyncio
import json
import os
import struct
import time


class DiscordRPC:
    def __init__(self):
        ipc_path = os.environ.get('XDG_RUNTIME_DIR', None) or os.environ.get('TMPDIR', None) or os.environ.get('TMP', None) or os.environ.get('TEMP', None) or '/tmp'
        self.ipc_path = f'{ipc_path}/discord-ipc-0'
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.sock_reader: asyncio.StreamReader = None
        self.sock_writer: asyncio.StreamWriter = None

    async def read_output(self):
        while True:
            data = await self.sock_reader.read(1024)
            print(f'OP Code: {struct.unpack("i", data[:4])[0]}; Length: {struct.unpack("i", data[4:8])[0]}\nResponse:\n{json.loads(data[8:].decode("utf-8"))}\n')
            await asyncio.sleep(1)

    def send_data(self, op: int, payload: dict):
        payload = json.dumps(payload)
        self.sock_writer.write(struct.pack('i', op) + struct.pack('i', len(payload)) + payload.encode('utf-8'))

    async def handshake(self):
        self.sock_reader, self.sock_writer = await asyncio.open_unix_connection(self.ipc_path, loop=self.loop)
        self.send_data(0, {'v': 1, 'client_id': '121678432504512512'})
        data = await self.sock_reader.read(1024)
        print(f'OP Code: {struct.unpack("i", data[:4])[0]}; Length: {struct.unpack("i", data[4:8])[0]}\nResponse:\n{json.loads(data[8:].decode("utf-8"))}\n')

    def send_rich_presence(self):
        current_time = time.time()
        payload = {
            "cmd": "SET_ACTIVITY",
            "args": {
                "activity": {
                    "state": "am sad",
                    "details": ":(",
                    "timestamps": {
                        "start": int(current_time)
                    },
                    "assets": {
                        "small_text": ":^(",
                        "small_image": "gio",
                        "large_text": ">tfw no gf",
                        "large_image": "feels"
                    },
                    "party": {
                        "size": [21, 42]
                    }
                },
                "pid": os.getpid()
            },
            "nonce": f'{current_time:.20f}'
        }
        self.send_data(1, payload)

    def close(self):
        self.sock_writer.close()
        self.loop.close()


if __name__ == '__main__':
    discord_rpc = DiscordRPC()
    try:
        discord_rpc.loop.run_until_complete(discord_rpc.handshake())
        discord_rpc.send_rich_presence()
        discord_rpc.loop.run_until_complete(discord_rpc.read_output())
    except KeyboardInterrupt:
        discord_rpc.close()
