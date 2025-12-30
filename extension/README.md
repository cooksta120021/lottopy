# Team Collaboration Extension (Prototype)

This folder contains a prototype for a custom over-the-internet collaboration extension (start/join/end session) intended for Windsurf/VS Code users. It now includes a basic WebSocket relay and live document sync (full real-time cursors/permissions/auth still TBD).

## Commands
- **Team Collaboration: Start Session** (`teamCollab.startSession`)
- **Team Collaboration: Join Session** (`teamCollab.joinSession`)
- **Team Collaboration: End Session** (`teamCollab.endSession`)

## Prereqs (do these once)
1) Python 3.9+  
   ```bash
   python -m pip install websockets  # or pip install -r requirements.txt
   ```
2) Node + npm (for the extension client)  
   ```bash
   npm install
   ```
3) VS Code or Windsurf (extension host is Node-based).

## Run it live (step-by-step, no packaging)
1) Start the relay on a publicly reachable host (envs optional):  
   ```bash
   # optional: RELAY_HOST=0.0.0.0 RELAY_PORT=8787 RELAY_PUBLIC_URL=ws://<public-ip>:8787
   python relay_py.py
   ```
   - Open port 8787 to the internet (or place behind a TLS reverse proxy).
   - In VS Code/Windsurf settings, set `teamCollab.relayUrl` to `ws://<public-ip>:8787` (or `wss://...` if proxied).
2) Open the `extension/` folder in VS Code/Windsurf.
3) Press F5 (or “Run Extension”) to launch the Extension Development Host.
4) In the Dev Host, Host A runs “Team Collaboration: Start Session” → copy invite.
5) Guest B runs “Team Collaboration: Join Session” → paste invite.
6) Both edit files; content syncs and the status bar shows which files others are on.
7) End with “Team Collaboration: End Session” (or close relay/instances).

## Notes / Next steps
- Current sync sends whole-document snapshots; improve to incremental ops + conflict handling.
- Status bar shows active files per collaborator; cursor sharing is optional and can be removed if not needed.
- Add permissions/auth/hosted relay/TLS per `team_plugin.md` for production use.
