import asyncio
import websockets
import json
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("sessions")

log_file = None

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def log(event, **kwargs):
    entry = {"ts": now_iso(), "event": event, **kwargs}
    log_file.write(json.dumps(entry) + "\n")
    log_file.flush()

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
        log("sender_connected")
        await broadcast_roster()
        try:
            async for message in websocket:
                print(f">> [{name}] {message}")
                log("message", data=message)
                envelope = json.dumps({"text": message, "from": name})
                if receivers:
                    await asyncio.gather(
                        *[ws.send(envelope) for ws in receivers.values()], return_exceptions=True
                    )
                    ack = json.dumps({"type": "ack", "text": message})
                else:
                    ack = json.dumps({"type": "ack", "text": message, "empty": True})
                await websocket.send(ack)
        finally:
            del senders[name]
            print(f"Sender disconnected: {name}")
            log("sender_disconnected")
            await broadcast_roster()

    else:
        receivers[name] = websocket
        print(f"Receiver connected: {name}")
        log("receiver_connected", name=name)
        await broadcast_roster()
        try:
            async for _ in websocket:
                pass
        finally:
            del receivers[name]
            print(f"Receiver disconnected: {name}")
            log("receiver_disconnected", name=name)
            await broadcast_roster()

async def main():
    global log_file
    LOG_DIR.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d_%H-%M-%S")
    log_path = LOG_DIR / f"{ts}.jsonl"
    with open(log_path, "w") as f:
        log_file = f
        log("session_start")
        try:
            async with websockets.serve(handler, "0.0.0.0", 8765):
                print(f"Armillaria server running on port 8765 (logging to {log_path})")
                await asyncio.Future()
        finally:
            log("session_end")

asyncio.run(main())
