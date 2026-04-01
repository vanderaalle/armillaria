#!/usr/bin/env python3
"""Replay a session log through the running Armillaria server.

The script connects as a sender and replays all messages with the original
timing. Press Ctrl+C to stop at any time — the server keeps running and
a human sender can take over.

Usage:
    python3 replay.py sessions/YYYY-MM-DD_HH-MM-SS.jsonl [--speed 1.0]

Options:
    --speed   Playback speed multiplier (default 1.0, use 2.0 for double speed)
"""

import asyncio
import json
import sys
from datetime import datetime, timezone

SERVER_URI = "ws://localhost:8765"

def load_messages(path):
    """Extract only message events with their timestamps."""
    with open(path) as f:
        entries = [json.loads(l) for l in f if l.strip()]
    return [e for e in entries if e["event"] == "message"]

async def replay(path, speed=1.0):
    messages = load_messages(path)
    if not messages:
        print("No messages found in log.")
        return

    print(f"Replaying {len(messages)} messages from {path} at {speed}x speed")
    print("Press Ctrl+C to stop.\n")

    async with __import__("websockets").connect(SERVER_URI) as ws:
        await ws.send("sender")  # identify as sender

        t0_log = datetime.fromisoformat(messages[0]["ts"]).timestamp()
        t0_now = asyncio.get_event_loop().time()

        for entry in messages:
            t_log = datetime.fromisoformat(entry["ts"]).timestamp()
            elapsed_log = t_log - t0_log
            elapsed_real = (asyncio.get_event_loop().time() - t0_now) * speed
            wait = (elapsed_log - elapsed_real) / speed

            if wait > 0:
                await asyncio.sleep(wait)

            await ws.send(entry["data"])
            print(f">> {entry['data']}")

    print("\nReplay complete.")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    path = args[0]
    speed = 1.0
    if "--speed" in args:
        i = args.index("--speed")
        speed = float(args[i + 1])

    try:
        asyncio.run(replay(path, speed))
    except KeyboardInterrupt:
        print("\nReplay stopped.")
