import websockets
import asyncio
import json
from redis import Redis
import random, string

PORT_TO_LISTEN = 7890

print("Server listening on port:", PORT_TO_LISTEN)

connected_set = set()
connection_list = []
r_queue = Redis()
redis_host = "auth-data.44nnpy.ng.0001.use1.cache.amazonaws.com"

r_auth_checker = Redis(host=redis_host, port=6379)


class connection_object(object):
    def __init__(self, conn_id, websocket_conn):
        self.conn_id = conn_id
        self.websocket_conn = websocket_conn

    def get_object(self):
        return self.websocket_conn

def generate_hash(hash_len=20):
    auth = ''.join(random.choices(string.ascii_letters + string.digits, k=hash_len))
    return auth

def set_auth_token_hash():
    auth = generate_hash(hash_len=16)
    auth_hash = generate_hash(hash_len=32)
    auth_tuple = (auth, auth_hash)
    return auth_tuple

def authentication(auth_token):
    r_auth_token = r_auth_checker.hexists("auth_token", auth_token)
    if r_auth_token:
        message_token_hash = r_auth_checker.hget("auth_token", auth_token)
        return message_token_hash
    else:
        return False


def extract_info(message):
    message_parser = dict()
    message_parser['is_valid'] = False

    if message.get("register", None):
        message_parser['register'] = True
        message_parser['device_name'] = message['device_name']
        message_parser['is_valid'] = True
        auth_tuple = set_auth_token_hash()
        if auth_tuple:
            message_parser['auth_key'] = auth_tuple[0]
            message_parser['auth_hash'] = auth_tuple[1]
        return message_parser

    auth_key = messgae_parser.get('auth_key', None)
    auth_token = authentication(auth_key)
    if not auth_token:
        return message_parser

    message_parser['from_id'] = message['from_id']
    if not message.get('message', None):
        # No message param in message dictionary, nothing to do here
        return message_parser
    else:
        message_parser['message'] = message['message']

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


async def check_dm_queue():
    while True:
        try:
            if r_queue.exists("dm_messages") == 1:
                message = r_queue.lpop("dm_messages")
                if message:
                    deserialized_message = json.loads(message)
                    from_id = int(deserialized_message['from_id'])
                    to_id = int(deserialized_message['to_id'])
                    dm_message = deserialized_message['message']
                    # Temporary Hack
                    if len(connection_list) >= from_id and len(connection_list) >= to_id:
                        from_conn_object = connection_list[from_id - 1]
                        to_conn_object = connection_list[to_id - 1]
                        from_str = str(from_id - 1)
                        await to_conn_object.websocket_conn.send("Message from " + from_str + ": " + dm_message)
                        print("One less message in dm queue, pheww")
                    else:
                        r_queue.lpush("dm_messages", message)
        except Exception as e:
            print("exception raised in redis dm queue checker:", e)
        await asyncio.sleep(1)


async def echo(websocket, path):
    print("A client just connected")
    try:
        async for message in websocket:
            try:
                deserialized_message = json.loads(message)
            except Exception as e:
                print("Message is not in a state where it could be deserialize the messgae. Skipping this message.")
                continue
            message_info = extract_info(deserialized_message)
            print("Message Info:", message_info)
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
                    r_auth_checker.hset("auth_token", message_info[0], message_info[1])
                    r_auth_checker.hset("device_mapping", message_info['device_name'], mesage_info['auth_hash'])
                    r_session = r_auth_checker.hset("session_table", message_info['device_name'], websokcet)
:                else:
                    print("Must register the device first")
                continue
            else:
                from_id = int(message_info['from_id']) - 1
                from_conn_obj = connection_list[from_id]
            print("Received message from client: " + message)
            ## for broadcasting to everyone; basically message from server
            #await websocket.send("Pong: " + "Thanks for the message. I will do the needful")
            if message_info.get('is_group', False):
                for conn in connected:
                    if conn != from_conn_obj:
                        await conn.send("Message from " + message_info['from_id'] + ": " + message)
            else:
                try:
                    to_id = int(message_info['to_id']) - 1
                    to_conn_object = connection_list[to_id]
                    await to_conn_object.websocket_conn.send("Message from " + message_info["to_id"] + ": " + message_info['message'])
                except Exception as e:
                    print("Exception is:", e)
                    dm_dict = dict()
                    dm_dict['from_id'] = str(from_id + 1)
                    dm_dict['to_id'] = str(to_id + 1)
                    dm_dict['message'] = message_info['message']
                    r_queue.lpush("dm_messages", json.dumps(dm_dict))
                    print("dm message pushed to wait queue")
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, "0.0.0.0", PORT_TO_LISTEN, reuse_port=True)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(check_dm_queue())
asyncio.get_event_loop().run_forever()
