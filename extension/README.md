# Team Collaboration Extension (Prototype)

This folder contains a prototype for a custom over-the-internet collaboration extension (start/join/end session) intended for Windsurf/VS Code users. It now includes a basic WebSocket relay and live document sync (full real-time cursors/permissions/auth still TBD).

## Commands
- **Team Collaboration: Start Session** (`teamCollab.startSession`)
- **Team Collaboration: Join Session** (`teamCollab.joinSession`)
- **Team Collaboration: End Session** (`teamCollab.endSession`)

## Prereqs
- Python 3.9+ with `websockets` for the relay.
- Node/npm to install the extension’s WebSocket client dependency (`ws`).
- VS Code or Windsurf to run the extension (extension host is Node-based).

## How to run (developer loop)
1) Start the Python relay:  
   ```bash
   python -m pip install websockets
   python relay_py.py  # listens on ws://localhost:8787
   ```
2) Install extension deps (once):  
   ```bash
   npm install
   ```
3) Open this folder in VS Code/Windsurf.
4) Launch the Extension Development Host (F5 in VS Code, or equivalent in Windsurf).
5) In the first editor instance (Host A): run “Team Collaboration: Start Session” → copy the invite.
6) In a second editor instance (Guest B): run “Team Collaboration: Join Session” → paste the invite.
7) Edit files; document content syncs, and the status bar shows which files others are working on.
8) To end: run “Team Collaboration: End Session” (or close the relay/instances).

## Notes / Next steps
- Current sync sends whole-document snapshots; improve to incremental ops + conflict handling.
- Status bar shows active files per collaborator; cursor sharing is optional and can be removed if not needed.
- Add permissions/auth/hosted relay/TLS per `team_plugin.md` for production use.
