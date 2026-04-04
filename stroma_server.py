import asyncio
import websockets
import json

nodes = {}

async def handler(websocket):
    first = await websocket.recv()

    try:
        data = json.loads(first)
        name = data.get("name", "unknown")
    except json.JSONDecodeError:
        name = first

    nodes[name] = websocket
    print(f"Node connected: {name} ({len(nodes)} total)")

    try:
        async for message in websocket:
            print(f">> [{name}] {message}")
            envelope = json.dumps({"text": message, "from": name})
            # broadcast to all nodes including sender
            await asyncio.gather(
                *[ws.send(envelope) for ws in nodes.values()]
            )
    finally:
        del nodes[name]
        print(f"Node disconnected: {name} ({len(nodes)} total)")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Stroma running on port 8765")
        await asyncio.Future()

asyncio.run(main())
