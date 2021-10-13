import websockets
import asyncio
import json
from redis import Redis

PORT_TO_LISTEN = 7890

print("Server listening on port:", PORT_TO_LISTEN)

connected_set = set()
connection_list = []
r = Redis()

class connection_object(object):
    def __init__(self, conn_id, websocket_conn):
        self.conn_id = conn_id
        self.websocket_conn = websocket_conn

    def get_object(self):
        return self.websocket_conn

def extract_info(message):
    message_parser = dict()
    message_parser['is_valid'] = False

    if message.get("register", None):
        message_parser['register'] = True
        message_parser['is_valid'] = True
        return message_parser

    message_parser['from_id'] = message['from_id']
    if not message.get('message', None):
        # No message param in message dictionary, nothing to do here
        return message_parser

    if message.get('is_group', None):
        message_parser['is_group'] = True
        message_parser['is_valid'] = True
        return message_parser
    else:
        message_parser['is_group'] = False
    if not message_parser['is_group']:
        if message.get('to_id', None):
            message_parser['to_id'] = message['to_id']
            message_parser['is_valid'] = True
        else:
            message_parser['is_valid'] = False
    return message_parser


async def check_dm_queue(connected_set, connection_list):
    try:
        if r_queue.exists("dm_messages") == 1:
            message = r_queue.lpop("dm_message")
            deserialized_message = json.loads(message)
            from_id = int(deserialized_message['from_id'])
            to_id = int(deserialized_message['to_id'])
            dm_message = deserialized_message['message']
            # Temporary Hack
            if len(connection_list) >= from_id and len(connected_list) >= to_id:
                from_conn_object = connection_list[from_id - 1]
                to_conn_object = connection_list[to_id - 1]
                to_conn_object.send("Message from " + str(from_id + 1) + ": " + dm_message)
            else:
                r_queue.lpush("dm_message", message)
    except Exception as e:
        print("exception raised in redis dm queue checker:", e)

async def echo(websocket, path):
    print("A client just connected")
    try:
        async for message in websocket:
            try:
                deserialized_message = json.loads(message)
                print("Message Log:", deserialized_message, "Type:", type(deserialized_message))
            except Exception as e:
                print("Message is not in a state where it could be deserialize the messgae. Skipping this message.")
                continue
            message_info = extract_info(deserialized_message)
            if not message_info.get('is_valid', False):
                print("Invalid message, nothing to do here")
                continue
            # Add Authentication Here
            if websocket not in connected_set:
                if message_info.get('register', False):
                    connected_set.add(websocket)
                    conn_id = len(connection_list) + 1
                    connection_list.append(connection_object(conn_id, websocket))
                    conn_obj = connection_list[-1]
                    await conn_obj.websocket_conn.send("Device Successfully Registered")
                else:
                    print("Must register the device first")
                print("Came Here.......")
                continue
            else:
                from_id = int(message_info['from_id']) - 1
                from_conn_obj = connection_list[from_id]
            print("Received message from client: " + message)
            ## for broadcasting to everyone; basically message from server
            #await websocket.send("Pong: " + "Thanks for the message. I will do the needful")
            if message_info.get('is_group', False):
                for conn in connected:
                    if conn != conn_obj:
                        await conn.send("Message from " + message_info['from_id'] + ": " + message)
            else:
                to_id = int(message_info['to_id']) - 1
                to_conn_object = connection_list[to_id]
                try:
                    to_conn_object.send("Message from " + message_info["to_id"] + ": " + message)
                except Exception as e:
                    dm_dict = dict()
                    dm_dict['from_id'] = str(from_id + 1)
                    dm_dict['to_id'] = str(to_id + 1)
                    r_queue.push("dm_messages", json.dumps(dm_dict))
                    print("dm message pushed to wait queue")
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, "localhost", PORT_TO_LISTEN)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
