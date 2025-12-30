"""Minimal Python WSS relay for the collaboration prototype.
Run with:
  python -m pip install websockets
  python relay_py.py
Listens on ws://localhost:8787
"""

import os
import asyncio
import websockets

rooms = {}  # invite -> set of websockets


async def handler(ws):
    invite = None
    try:
        async for raw in ws:
            try:
                msg = raw
                if isinstance(raw, bytes):
                    msg = raw.decode()
                data = websockets.utils.json.loads(msg)
            except Exception:
                continue

            if data.get("type") == "join" and data.get("invite"):
                invite = data["invite"]
                rooms.setdefault(invite, set()).add(ws)
                await ws.send(websockets.utils.json.dumps({"type": "joined", "invite": invite}))
                continue

            if invite and invite in rooms:
                # broadcast to room except sender
                for client in list(rooms[invite]):
                    if client is ws:
                        continue
                    if client.closed:
                        rooms[invite].discard(client)
                        continue
                    await client.send(msg)
    finally:
        if invite and invite in rooms:
            rooms[invite].discard(ws)
            if not rooms[invite]:
                rooms.pop(invite, None)


async def main():
    host = os.environ.get("RELAY_HOST", "0.0.0.0")
    port = int(os.environ.get("RELAY_PORT", "8787"))
    advertised = os.environ.get("RELAY_PUBLIC_URL", f"ws://{host}:{port}")

    async with websockets.serve(handler, host, port):
        print(f"Relay listening on ws://{host}:{port} (Python)")
        print(f"Set teamCollab.relayUrl to: {advertised}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
