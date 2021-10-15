import websockets
import asyncio
import json
from redis import Redis
import random, string
import pickle
import requests

PORT_TO_LISTEN = 7890

print("Server listening on port:", PORT_TO_LISTEN)

connected_set = set()
r_queue = Redis()
redis_host = "auth-data.44nnpy.ng.0001.use1.cache.amazonaws.com"

r_auth_checker = Redis(host=redis_host, port=6379)
connection_dict = dict()
connecton_list = []

solr_ip = "54.227.45.228"
PORT = "8983"
CORENAME = "oit_help_desk"

class connection_object(object):
    def __init__(self, device_name, websocket_conn):
        self.device_name = device_name
        self.websocket_conn = websocket_conn

    def get_object(self):
        return self.websocket_conn


# Just an illustration of backend infraset to make search queries work
# Very few data is indexed in Solr at the moment. Just for illustration purpose
def handle_search_queries(query):
    solr_url = "http://" + solr_ip + ':' + PORT + "/solr/" + CORENAME + "/select"
    fq_query = 'question:' + query
    print("fq_query:", fq_query)
    r = requests.get(solr_url, params={"fq":fq_query, "q":"*:*"})
    try:
        response = r.json()
        solr_docs = response['docs']
        if solr_docs:
            top_result = solr_docs[0]
            top_response = top_result['answer'] + " " + top_result['http_link']
            return top_response
        return "Our representative will get in-touch with you"
    except Exception as e:
        # default exception return message
        return "Our representative will get in-touch with you"

def generate_hash(hash_len=20):
    auth = ''.join(random.choices(string.ascii_letters + string.digits, k=hash_len))
    return auth


def get_device_mappings(auth_key, websocket):
    auth_hash = None
    device_mapping = None
    if auth_key and r_auth_checker.hexists('auth_hash', auth_key):
        auth_hash = (r_auth_checker.hget("auth_hash", auth_key)).decode()
    if auth_hash and r_auth_checker.hexists('device_mapping', auth_hash):
        device_mapping = (r_auth_checker.hget("device_mapping", auth_hash)).decode()
    if auth_hash and device_mapping:
        return auth_hash, device_mapping
    return None, None


def get_reverse_device_mapping(device_mapping):
    if r_auth_checker.hexists('reverse_device_mapping', device_mapping):
        return (r_auth_checker.hget('reverse_device_mapping', device_mapping)).decode()
    else:
        return None


def set_auth_token_hash(device_mapping):
    auth_key = generate_hash(hash_len=16)
    auth_hash = generate_hash(hash_len=32)
    auth_tuple = (auth_key, auth_hash)
    r_auth_checker.hset('auth_hash', auth_key, auth_hash)
    r_auth_checker.hset('device_mapping', auth_hash, device_mapping)
    r_auth_checker.hset('reverse_device_mapping', device_mapping, auth_hash)
    return auth_tuple


def extract_info(message, websocket):
    message_parser = dict()
    message_parser['is_valid'] = False
    auth_key = message.get('auth_key', None)
    auth_hash = None
    device_mapping = None

    if auth_key:
        auth_hash, device_mapping = get_device_mappings(auth_key, websocket)
        if auth_hash and device_mapping:
            message_parser['auth_key'] = auth_key
            message_parser['auth_hash'] = auth_hash
            message_parser['device_mapping'] = device_mapping

    elif message.get("register", None):
        message_parser['register'] = True
        message_parser['device_mapping'] = message['device_name']
        auth_tuple = set_auth_token_hash(message_parser['device_mapping'])
        if auth_tuple and auth_tuple[0] and auth_tuple[1] and message_parser['device_mapping']:
            auth_hash, device_mapping = get_device_mappings(auth_tuple[0], websocket)
            if auth_hash:
                message_parser['auth_key'] = auth_tuple[0]
                message_parser['auth_hash'] = auth_hash
                message_parser['device_mapping'] = device_mapping
                message_parser['is_valid'] = True
        return message_parser

    else:
        print("Cannot authenticate")

    if message.get('disconnect', False):
        message_parser['disconnect'] = True
        message_parser['is_valid'] = True
        return message_parser

    message_parser['from_id'] = device_mapping

    if message.get('question', False):
        message_parser['question'] = message['question']
        message_parser['is_valid'] = True
        return message_parser

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


# Cleanup on deletion
def handle_disconnection(message_info):
    r_auth_checker.hdel('auth_hash', message_info['auth_key'])
    r_auth_checker.hdel('device_mapping', message_info['auth_hash'])
    r_auth_checker.hdel('reverse_device_mapping', message_info['device_mapping'])
    connected_set.remove(connection_dict[message_info['device_mapping']].websocket_conn)
    connection_dict.pop(message_info['device_mapping'], None)


async def check_dm_queue():
    while True:
        try:
            if r_queue.exists("dm_messages") == 1:
                message = r_queue.lpop("dm_messages")
                if message:
                    deserialized_message = json.loads(message)
                    from_id = deserialized_message['from_id']
                    to_id = deserialized_message['to_id']
                    dm_message = deserialized_message['message']
                    if from_id in connection_dict and to_id in connection_dict:
                        from_conn_object = connection_dict[from_id]
                        to_conn_object = connection_dict[to_id]
                        await to_conn_object.websocket_conn.send("Message from " + from_id + ": " + dm_message)
                        await from_conn_object.websocket_conn.send("Message: " + dm_message + " delivered to " + to_id)
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
            message_info = extract_info(deserialized_message, websocket)
            print("Message Info:", message_info)

            # Add Authentication Here
            if websocket not in connected_set:
                if message_info.get('register', False):
                    if message_info.get('is_valid', False):
                        connected_set.add(websocket)
                        conn_obj = connection_object(message_info['device_mapping'], websocket)
                        connection_dict[message_info['device_mapping']] = conn_obj
                        await conn_obj.websocket_conn.send("Device Successfully Registered. Note down your api_key: " + message_info['auth_key'])
                    else:
                        await websocket.send("Could Not Register Your Device Successfully")
                else:
                     await websocket.send("Must Register Your Device First")
                continue

            if not message_info.get('is_valid', False):
                print("Invalid message, nothing to do here")
                continue

            if message_info.get('disconnect', False):
                print("Handling disconnection")
                handle_disconnection(message_info)
                continue

            from_id = message_info['from_id']
            from_conn_obj = connection_dict[from_id]

            if message_info.get('question', False):
                question_response = handle_search_queries(message_info['question'])
                await from_conn_obj.websocket_conn.send(question_response)
                continue

            print("Received message from client: " + message)
            ## for broadcasting to everyone; basically message from server
            #await websocket.send("Pong: " + "Thanks for the message. I will do the needful")
            if message_info.get('is_group', False):
                for conn in connected:
                    if conn != from_conn_obj:
                        await conn.send("Message from " + message_info['from_id'] + ": " + message)
                print("group message sent successfully")
            else:
                try:
                    to_id = message_info['to_id']
                    to_conn_object = connection_dict[to_id]
                    await to_conn_object.websocket_conn.send("Message from " + from_id + ": " + message_info['message'])
                    print("dm message sent successfully")
                except Exception as e:
                    print("Exception is:", e)
                    dm_dict = dict()
                    dm_dict['from_id'] = from_id
                    dm_dict['to_id'] = to_id
                    dm_dict['message'] = message_info['message']
                    r_queue.lpush("dm_messages", json.dumps(dm_dict))
                    print("dm message pushed to wait queue")
                    await from_conn_obj.websocket_conn.send(to_id + " is not online yet")
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")
    # except Exception as e:
    #     print("Unhandled Exception has occured:", e)


start_server = websockets.serve(echo, "0.0.0.0", PORT_TO_LISTEN, reuse_port=True)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(check_dm_queue())
asyncio.get_event_loop().run_forever()
