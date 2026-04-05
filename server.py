import asyncio
import websockets
import json

senders = {}
receivers = {}

def all_clients():
    return list(senders.values()) + list(receivers.values())

async def broadcast_roster():
    roster = json.dumps({"type": "roster", "names": sorted(receivers.keys())})
    targets = all_clients()
    if targets:
        await asyncio.gather(*[ws.send(roster) for ws in targets], return_exceptions=True)

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
        await broadcast_roster()
        try:
            async for message in websocket:
                print(f">> [{name}] {message}")
                envelope = json.dumps({"text": message, "from": name})
                if receivers:
                    await asyncio.gather(
                        *[ws.send(envelope) for ws in receivers.values()], return_exceptions=True
                    )
        finally:
            del senders[name]
            print(f"Sender disconnected: {name}")
            await broadcast_roster()

    else:
        receivers[name] = websocket
        print(f"Receiver connected: {name}")
        await broadcast_roster()
        try:
            async for _ in websocket:
                pass
        finally:
            del receivers[name]
            print(f"Receiver disconnected: {name}")
            await broadcast_roster()

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        print("Armillaria server running on port 8765")
        await asyncio.Future()

asyncio.run(main())
