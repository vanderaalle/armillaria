import asyncio
import websockets
import json

sender = None
receivers = {}

async def handler(websocket):
    global sender

    role = await websocket.recv()

    if role == "sender":
        sender = websocket
        print("Sender connected")
        try:
            async for message in websocket:
                print(f">> {message}")
                if receivers:
                    await asyncio.gather(
                        *[ws.send(message) for ws in receivers.values()]
                    )
        finally:
            sender = None
            print("Sender disconnected")
    else:
        name = role  # role is the musician's name
        receivers[name] = websocket
        print(f"Receiver connected: {name}")
        try:
            async for _ in websocket:
                pass  # receivers don't send anything
        finally:
            del receivers[name]
            print(f"Receiver disconnected: {name}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Armillaria server running on port 8765")
        await asyncio.Future()  # run forever

asyncio.run(main())
