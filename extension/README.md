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
3) Windsurf (extension host is Node-based; instructions below assume Windsurf).

## Run it live (step-by-step, no packaging)
1) Start the relay on a publicly reachable host (envs optional):  
   ```bash
   # optional: RELAY_HOST=0.0.0.0 RELAY_PORT=8787 RELAY_PUBLIC_URL=ws://<public-ip>:8787
   python relay_py.py
   ```
   - Open port 8787 to the internet (or place behind a TLS reverse proxy).
   - The relay will prompt HOST/GUEST and print the relay URL to set (`teamCollab.relayUrl`) plus your next steps (start/join session). If no .env is present, it creates share.env with defaults.
2) Open the `extension/` folder in Windsurf.
3) (Optional helper) From `extension/`, run:
   ```bash
   python run_collab.py
   ```
   This will pip+npm install deps (if possible) and launch the interactive relay.
4) Launch the Extension Development Host (Windsurf) without F5:
   ```bash
   npm run dev:windsurf
   ```
5) In the Dev Host, Host A runs “Team Collaboration: Start Session” → copy invite.
6) Guest B runs “Team Collaboration: Join Session” → paste invite.
7) Both edit files; content syncs and the status bar shows which files others are on.
8) End with “Team Collaboration: End Session” (or close relay/instances).

## Notes / Next steps
- Current sync sends whole-document snapshots; improve to incremental ops + conflict handling.
- Status bar shows active files per collaborator; cursor sharing is optional and can be removed if not needed.
- Add permissions/auth/hosted relay/TLS per `team_plugin.md` for production use.
