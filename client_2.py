import websockets
import asyncio
import json

def create_message_content():
    msg_dict = {"from":"client_2", "to":"client_1"}
    msg_dict_dump = json.dumps(msg_dict)
    return msg_dict_dump

async def listen():
    url = "ws://127.0.0.1:7890"
    async with websockets.connect(url) as ws:
        message_content = create_message_content()
        await ws.send(message_content)
        while True:
            msg = await ws.recv()
            print(msg)
asyncio.get_event_loop().run_until_complete(listen())
