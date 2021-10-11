import websockets
import asyncio

PORT_TO_LISTEN = 7890

print("Server listening on port:", PORT_TO_LISTEN)

async def echo(websocket, path):
    print("A client just connected")
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            await websocket.send("Pong: " + message)
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, "localhost", PORT_TO_LISTEN)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
