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


def load_env_defaults():
    """
    Load env vars from .env or share.env (simple KEY=VALUE lines).
    If none exists, create share.env with defaults.
    """
    candidates = [".env", "share.env"]
    env_file = None
    for candidate in candidates:
        if os.path.exists(candidate):
            env_file = candidate
            break
    if env_file is None:
        env_file = "share.env"
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("RELAY_HOST=0.0.0.0\nRELAY_PORT=8787\nRELAY_PUBLIC_URL=\n")
        print(f"Created {env_file} with defaults. Edit it to change relay host/port/public URL.")

    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip()
                if k and v and k not in os.environ:
                    os.environ[k] = v
    except Exception as e:
        print(f"Warning: failed to read {env_file}: {e}")


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
    load_env_defaults()
    host = os.environ.get("RELAY_HOST", "0.0.0.0")
    port = int(os.environ.get("RELAY_PORT", "8787"))
    advertised = os.environ.get("RELAY_PUBLIC_URL", f"ws://{host}:{port}")

    print("=== Team Collab Relay ===")
    print("This will run until you press Ctrl+C.")
    print(f"Host: {host}:{port}")
    print(f"Advertised (set teamCollab.relayUrl to this): {advertised}")
    role = input("Are you HOST or GUEST? [HOST/GUEST]: ").strip().lower()

    if role == "host":
        print("\nAs HOST:")
        print("1) In VS Code/Windsurf settings, set teamCollab.relayUrl to:", advertised)
        print("2) Launch the extension dev host (F5 or npm run dev:code/dev:windsurf).")
        print("3) Run 'Team Collaboration: Start Session' and copy the invite.")
        print("4) Share the invite with your guests.")
    elif role == "guest":
        print("\nAs GUEST:")
        print("1) In VS Code/Windsurf settings, set teamCollab.relayUrl to:", advertised)
        print("2) Launch the extension dev host (F5 or npm run dev:code/dev:windsurf).")
        print("3) Run 'Team Collaboration: Join Session' and paste the invite you received.")
    else:
        print("\nUnknown choice; continuing as relay only. Set teamCollab.relayUrl to:", advertised)

    async with websockets.serve(handler, host, port):
        print(f"Relay listening on ws://{host}:{port} (Python)")
        print(f"Set teamCollab.relayUrl to: {advertised}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
