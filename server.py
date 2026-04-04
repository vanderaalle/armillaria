import asyncio
import websockets
import json

senders = {}
receivers = {}

async def handler(websocket):
    first = await websocket.recv()

    try:
        data = json.loads(first)
        role = data.get("role")
        name = data.get("name", "unknown")
    except json.JSONDecodeError:
        # fallback: plain "sender" or receiver name (backward compat)
        role = "sender" if first == "sender" else "receiver"
        name = first if role == "receiver" else "unknown"

    if role == "sender":
        senders[name] = websocket
        print(f"Sender connected: {name}")
        try:
            async for message in websocket:
                print(f">> [{name}] {message}")
                envelope = json.dumps({"text": message, "from": name})
                if receivers:
                    await asyncio.gather(
                        *[ws.send(envelope) for ws in receivers.values()]
                    )
        finally:
            del senders[name]
            print(f"Sender disconnected: {name}")

    else:
        receivers[name] = websocket
        print(f"Receiver connected: {name}")
        try:
            async for _ in websocket:
                pass
        finally:
            del receivers[name]
            print(f"Receiver disconnected: {name}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Armillaria server running on port 8765")
        await asyncio.Future()

asyncio.run(main())
