const vscode = require("vscode");
const WebSocket = require("ws");

let session = {
  active: false,
  role: null, // "host" | "guest"
  invite: null,
  socket: null,
  userId: null,
  applying: false,
};

const remoteSelections = new Map(); // uri -> Map<userId, ranges>
let selectionDecoration = null;
let activityStatus = null;
const remoteActivity = new Map(); // userId -> uri

const DEFAULT_RELAY = "ws://localhost:8787";

function ensureDecoration() {
  if (!selectionDecoration) {
    selectionDecoration = vscode.window.createTextEditorDecorationType({
      backgroundColor: "rgba(0, 150, 255, 0.15)",
      border: "1px solid rgba(0, 150, 255, 0.4)",
    });
  }
  if (!activityStatus) {
    activityStatus = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 100);
    activityStatus.text = "Collab: idle";
    activityStatus.show();
  }
}

function connect(invite, role, context) {
  if (session.socket) {
    session.socket.close();
  }

  const userId = `u-${Math.random().toString(36).slice(2, 8)}`;
  const relayUrl = vscode.workspace
    .getConfiguration("teamCollab")
    .get("relayUrl", DEFAULT_RELAY);

  const socket = new WebSocket(relayUrl);
  session = { active: true, role, invite, socket, userId, applying: false };

  socket.on("open", () => {
    socket.send(
      JSON.stringify({ type: "join", invite, role, userId, ts: Date.now() })
    );
    vscode.window.showInformationMessage(
      `Connected to relay as ${role}. Invite: ${invite}`
    );
    if (role === "host") {
      broadcastAllOpenDocs(socket, userId);
    }
  });

  socket.on("message", (data) => {
    try {
      const msg = JSON.parse(data.toString());
      handleMessage(msg, userId);
    } catch (e) {
      console.error("Bad message", e);
    }
  });

  socket.on("close", () => {
    vscode.window.showInformationMessage("Connection closed.");
    session = {
      active: false,
      role: null,
      invite: null,
      socket: null,
      userId: null,
      applying: false,
    };
    remoteSelections.clear();
    refreshSelections();
    remoteActivity.clear();
    refreshActivity();
  });

  socket.on("error", (err) => {
    vscode.window.showErrorMessage(`Collab error: ${err.message}`);
  });

  const changeSub = vscode.workspace.onDidChangeTextDocument((event) => {
    if (session.applying) return;
    if (!session.socket || session.socket.readyState !== WebSocket.OPEN) return;
    const uri = event.document.uri.toString();
    const content = event.document.getText();
    session.socket.send(
      JSON.stringify({
        type: "docChange",
        invite,
        uri,
        content,
        version: event.document.version,
        userId,
      })
    );
    session.socket.send(
      JSON.stringify({
        type: "activity",
        invite,
        uri,
        userId,
      })
    );
  });

  const selectionSub = vscode.window.onDidChangeTextEditorSelection((event) => {
    if (!session.socket || session.socket.readyState !== WebSocket.OPEN) return;
    const ranges = event.selections.map((s) => ({
      start: { line: s.start.line, character: s.start.character },
      end: { line: s.end.line, character: s.end.character },
    }));
    session.socket.send(
      JSON.stringify({
        type: "selection",
        invite,
        uri: event.textEditor.document.uri.toString(),
        ranges,
        userId,
      })
    );
  });

  const activeEditorSub = vscode.window.onDidChangeActiveTextEditor((editor) => {
    if (!editor) return;
    if (!session.socket || session.socket.readyState !== WebSocket.OPEN) return;
    session.socket.send(
      JSON.stringify({
        type: "activity",
        invite,
        uri: editor.document.uri.toString(),
        userId,
      })
    );
  });

  context.subscriptions.push(changeSub, selectionSub, activeEditorSub);
}

function handleMessage(msg, userId) {
  if (msg.userId && msg.userId === userId) return; // ignore own messages
  if (msg.type === "docChange" && msg.uri && typeof msg.content === "string") {
    const uri = vscode.Uri.parse(msg.uri);
    vscode.workspace.openTextDocument(uri).then(
      (doc) => applyContent(doc, msg.content),
      () => {
        vscode.workspace.openTextDocument({ content: msg.content, language: "plaintext" }).then((doc) => {
          vscode.window.showTextDocument(doc, { preview: false });
        });
      }
    );
  } else if (msg.type === "selection" && msg.uri && Array.isArray(msg.ranges)) {
    const uri = msg.uri;
    if (!remoteSelections.has(uri)) {
      remoteSelections.set(uri, new Map());
    }
    remoteSelections.get(uri).set(msg.userId || "guest", msg.ranges);
    refreshSelections();
  } else if (msg.type === "activity" && msg.uri) {
    remoteActivity.set(msg.userId || "guest", msg.uri);
    refreshActivity();
  }
}

function applyContent(doc, content) {
  session.applying = true;
  const edit = new vscode.WorkspaceEdit();
  const fullRange = new vscode.Range(
    doc.positionAt(0),
    doc.positionAt(doc.getText().length)
  );
  edit.replace(doc.uri, fullRange, content);
  vscode.workspace.applyEdit(edit).finally(() => {
    session.applying = false;
  });
}

function refreshSelections() {
  ensureDecoration();
  vscode.window.visibleTextEditors.forEach((editor) => {
    const uri = editor.document.uri.toString();
    const entries = remoteSelections.get(uri);
    if (!entries) {
      editor.setDecorations(selectionDecoration, []);
      return;
    }
    const ranges = [];
    entries.forEach((rs) => {
      rs.forEach((r) => {
        ranges.push(
          new vscode.Range(
            new vscode.Position(r.start.line, r.start.character),
            new vscode.Position(r.end.line, r.end.character)
          )
        );
      });
    });
    editor.setDecorations(selectionDecoration, ranges);
  });
}

function refreshActivity() {
  if (!activityStatus) return;
  if (remoteActivity.size === 0) {
    activityStatus.text = "Collab: idle";
    return;
  }
  const parts = [];
  remoteActivity.forEach((uri, user) => {
    try {
      const path = vscode.Uri.parse(uri).path.split("/").pop();
      parts.push(`${user}: ${path || uri}`);
    } catch {
      parts.push(`${user}: ${uri}`);
    }
  });
  activityStatus.text = `Collab: ${parts.join(" | ")}`;
}

function broadcastAllOpenDocs(socket, userId) {
  vscode.workspace.textDocuments.forEach((doc) => {
    socket.send(
      JSON.stringify({
        type: "docChange",
        invite: session.invite,
        uri: doc.uri.toString(),
        content: doc.getText(),
        version: doc.version,
        userId,
      })
    );
  });
}

function activate(context) {
  const start = vscode.commands.registerCommand("teamCollab.startSession", () => {
    const invite = `tc-${Math.random().toString(36).slice(2, 10)}`;
    vscode.window.showInformationMessage(`Session started. Invite: ${invite}`);
    connect(invite, "host", context);
  });

  const join = vscode.commands.registerCommand("teamCollab.joinSession", async () => {
    const input = await vscode.window.showInputBox({
      prompt: "Enter invite token/link",
      placeHolder: "tc-xxxxxxx",
    });
    if (!input) {
      return;
    }
    connect(input.trim(), "guest", context);
  });

  const end = vscode.commands.registerCommand("teamCollab.endSession", () => {
    if (!session.active) {
      vscode.window.showInformationMessage("No active session to end.");
      return;
    }
    if (session.socket) {
      session.socket.close();
    }
    session = { active: false, role: null, invite: null, socket: null, userId: null };
    vscode.window.showInformationMessage("Session ended.");
  });

  context.subscriptions.push(start, join, end);
}

function deactivate() {
  if (session.socket) {
    session.socket.close();
  }
  session = { active: false, role: null, invite: null, socket: null, userId: null };
}

module.exports = {
  activate,
  deactivate,
};
