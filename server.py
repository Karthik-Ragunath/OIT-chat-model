import websockets
import asyncio

PORT_TO_LISTEN = 7890

print("Server listening on port:", PORT_TO_LISTEN)

connected = set()

async def echo(websocket, path):
    print("A client just connected")
    connected.add(websocket)
    try:
        async for message in websocket:
            print("Received message from client: " + message)
            ## for broadcasting to everyone
            #await websocket.send("Pong: " + "Thanks for the message. I will do the needful")
            for conn in connected:
                if conn != websocket:
                    await conn.send("Someone sent a  message to server")
    except websockets.exceptions.ConnectionClosed as e:
        print("A client just disconnected")

start_server = websockets.serve(echo, "localhost", PORT_TO_LISTEN)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
