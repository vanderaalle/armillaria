#!/usr/bin/env python3
"""Convert a session .jsonl log to readable text."""

import json
import sys
from datetime import datetime, timezone

def format_ts(ts):
    dt = datetime.fromisoformat(ts)
    return dt.strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

def convert(path):
    with open(path) as f:
        lines = [json.loads(l) for l in f if l.strip()]

    for entry in lines:
        ts = format_ts(entry["ts"])
        event = entry["event"]

        if event == "session_start":
            print(f"[{ts}] --- session start ---")
        elif event == "session_end":
            print(f"[{ts}] --- session end ---")
        elif event == "sender_connected":
            print(f"[{ts}] sender connected")
        elif event == "sender_disconnected":
            print(f"[{ts}] sender disconnected")
        elif event == "receiver_connected":
            print(f"[{ts}] {entry['name']} connected")
        elif event == "receiver_disconnected":
            print(f"[{ts}] {entry['name']} disconnected")
        elif event == "message":
            print(f"[{ts}] >> {entry['data']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 log_to_text.py sessions/YYYY-MM-DD_HH-MM-SS.jsonl")
        sys.exit(1)
    convert(sys.argv[1])
