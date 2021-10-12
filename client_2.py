import websockets
import asyncio
import json

def create_dm_message_content():
    msg_dict = {"from_id":"2", "to_id":"1", "message":"Hello there!!! Hope you are doing?!!!"}
    msg_dict_dump = json.dumps(msg_dict)
    return msg_dict_dump

def register_message_content():
    msg_dict = {"register": True}
    msg_dict_dump = json.dumps(msg_dict)
    return msg_dict_dump

def create_group_message():
    msg_dict = {"from_id":"1", "group_message":"Hello there!!! lets talk right?"}
    msg_dict_dump = json.dumps(msg_dict)
    return msg_dict_dump

async def listen():
    url = "ws://127.0.0.1:7890"
    async with websockets.connect(url) as ws:
        register_content = register_message_content()
        await ws.send(register_content)
        msg = await ws.recv()
        print(msg)

        message_content = create_dm_message_content()
        await ws.send(message_content)
        while True:
            msg = await ws.recv()
            print(msg)

asyncio.get_event_loop().run_until_complete(listen())
