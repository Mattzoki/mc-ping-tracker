#!/usr/bin/env python3
"""
Pings a Minecraft server and appends the result to data/pings.csv.

Usage:
    python scripts/ping_server.py <host[:port]>

Requires: mcstatus  (pip install mcstatus)
"""

import csv
import os
import sys
from datetime import datetime, timezone

from mcstatus import JavaServer

CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pings.csv")
CSV_HEADER = ["timestamp_utc", "host", "online", "latency_ms", "players_online", "players_max"]


def ping(address: str) -> dict:
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "host": address,
        "online": False,
        "latency_ms": "",
        "players_online": "",
        "players_max": "",
    }
    try:
        server = JavaServer.lookup(address)
        status = server.status()
        row["online"] = True
        row["latency_ms"] = round(status.latency, 2)
        row["players_online"] = status.players.online
        row["players_max"] = status.players.max
    except Exception as exc:  # server offline, DNS failure, timeout, etc.
        print(f"Ping failed for {address}: {exc}", file=sys.stderr)
    return row


def append_row(row: dict) -> None:
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    file_exists = os.path.isfile(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python ping_server.py <host[:port]>", file=sys.stderr)
        sys.exit(1)

    address = sys.argv[1]
    row = ping(address)
    append_row(row)
    print(row)


if __name__ == "__main__":
    main()
