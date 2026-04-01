import asyncio
import websockets
import json
import os
from datetime import datetime, timezone

sender = None
receivers = {}
log_file = None

def log(entry):
    entry["ts"] = datetime.now(timezone.utc).isoformat()
    print(json.dumps(entry))
    if log_file:
        log_file.write(json.dumps(entry) + "\n")
        log_file.flush()

async def handler(websocket):
    global sender

    role = await websocket.recv()

    if role == "sender":
        sender = websocket
        log({"event": "sender_connected"})
        try:
            async for message in websocket:
                log({"event": "message", "data": message})
                if receivers:
                    await asyncio.gather(
                        *[ws.send(message) for ws in receivers.values()]
                    )
        finally:
            sender = None
            log({"event": "sender_disconnected"})
    else:
        name = role  # role is the musician's name
        receivers[name] = websocket
        log({"event": "receiver_connected", "name": name})
        try:
            async for _ in websocket:
                pass  # receivers don't send anything
        finally:
            del receivers[name]
            log({"event": "receiver_disconnected", "name": name})

async def main():
    global log_file
    os.makedirs("sessions", exist_ok=True)
    session_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_path = f"sessions/{session_name}.jsonl"
    log_file = open(log_path, "w")
    log({"event": "session_start"})
    print(f"Logging to {log_path}")

    try:
        async with websockets.serve(handler, "0.0.0.0", 8765):
            print("Armillaria server running on port 8765")
            await asyncio.Future()
    except asyncio.CancelledError:
        pass
    finally:
        log({"event": "session_end"})
        log_file.close()

asyncio.run(main())
