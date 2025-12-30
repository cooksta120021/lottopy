# Team Collaboration Extension (Custom Live Share)

Goal: a custom extension that enables over-the-internet, real-time code collaboration (edit/navigate/debug) between teammates using Windsurf or VS Code—without relying on the existing Live Share extension. Host and guests use their own editors (Windsurf/VS Code) and should see each other’s cursors, selections, and edits live.

## What it should do
- Host a collaboration session and expose a join link/token.
- Allow guests to edit files, see each other’s cursors/selections, and optionally share terminals/debug sessions.
- Work over the internet with minimal setup (uses HTTPS/WSS).
- Provide role controls (host vs. guests) and session stop.

## High-level design
- **Host agent**: runs in the editor, opens a secure WSS channel, advertises a join token/link.
- **Guest agent**: connects via the link, mirrors workspace state, streams edits/selections.
- **Transport**: WSS via a relay service (or self-hosted relay) to avoid direct port forwarding.
- **Auth**: short-lived tokens scoped to the session; host can revoke.
- **Permissions**: host toggles guest edit/debug/terminal access.

## Usage flow (target)
1. Install the custom Team Collaboration extension in your own editor (Windsurf/VS Code).
2. Host starts a session (Command Palette → “Team Collaboration: Start Session”).
3. Extension spins up a WSS connection to the relay and shows an invite link/token.
4. Host shares the link with teammates.
5. Guests run “Team Collaboration: Join Session” and paste the link.
6. Guests see the workspace, can follow or edit (as permitted), and can watch each other’s cursor/selection movement live.
7. Host can stop the session anytime (“Team Collaboration: End Session”).

## Setup notes (for implementation)
- Provide a small relay service (Docker-ready) or allow configuring a hosted relay URL.
- Use HTTPS/WSS; avoid raw ws.
- Persist nothing server-side beyond ephemeral session routing.
- Expose minimal config in settings: relay URL, allow-edit default, allow-terminal default.

## Tips
- Use branches to keep changes organized while collaborating.
- Keep terminal sharing optional and locked to host by default.
- End sessions when done to invalidate tokens.
