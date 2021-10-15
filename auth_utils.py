import random, string
from redis import Redis

redis_host = "auth-data.44nnpy.ng.0001.use1.cache.amazonaws.com"
r_auth_checker = Redis(host=redis_host, port=6379)

# Util function to generate hash
def generate_hash(hash_len=20):
    auth = ''.join(random.choices(string.ascii_letters + string.digits, k=hash_len))
    return auth

# Checking distributed key store to get authentication info
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

# Generating Auth token hashed for new clients
def set_auth_token_hash(device_mapping, auth_key_len=16, auth_hash_len=32):
    auth_key = generate_hash(hash_len=auth_key_len)
    auth_hash = generate_hash(hash_len=auth_hash_len)
    auth_tuple = (auth_key, auth_hash)
    r_auth_checker.hset('auth_hash', auth_key, auth_hash)
    r_auth_checker.hset('device_mapping', auth_hash, device_mapping)
    r_auth_checker.hset('reverse_device_mapping', device_mapping, auth_hash)
    return auth_tuple

# Cleaning up on deletion of websocket connection
def handle_disconnection(message_info, message_info, connection_dict):
    r_auth_checker.hdel('auth_hash', message_info['auth_key'])
    r_auth_checker.hdel('device_mapping', message_info['auth_hash'])
    r_auth_checker.hdel('reverse_device_mapping', message_info['device_mapping'])
    connected_set.remove(connection_dict[message_info['device_mapping']].websocket_conn)
    connection_dict.pop(message_info['device_mapping'], None)
