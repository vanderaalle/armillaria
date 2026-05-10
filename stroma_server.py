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

nodes = {}

async def broadcast_roster():
    roster = json.dumps({"type": "roster", "names": sorted(nodes.keys())})
    if nodes:
        await asyncio.gather(*[ws.send(roster) for ws in nodes.values()], return_exceptions=True)

async def handler(websocket):
    first = await websocket.recv()

    try:
        data = json.loads(first)
        name = data.get("name", "unknown")
    except json.JSONDecodeError:
        name = first

    nodes[name] = websocket
    print(f"Node connected: {name} ({len(nodes)} total)")
    log("node_connected", name=name)
    await broadcast_roster()

    try:
        async for message in websocket:
            print(f">> [{name}] {message}")
            log("message", **{"from": name, "data": message})
            envelope = json.dumps({"text": message, "from": name})
            await asyncio.gather(
                *[ws.send(envelope) for ws in nodes.values()], return_exceptions=True
            )
    finally:
        del nodes[name]
        print(f"Node disconnected: {name} ({len(nodes)} total)")
        log("node_disconnected", name=name)
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
                print(f"Stroma running on port 8765 (logging to {log_path})")
                await asyncio.Future()
        finally:
            log("session_end")

asyncio.run(main())
