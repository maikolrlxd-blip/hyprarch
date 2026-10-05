'use strict';
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { Store } = require('./store');
const { PROVIDERS, chat } = require('./providers');
const brain = require('./brain');
const QRCode = require('qrcode');
const { NetServer } = require('./netserver');

const histories = new Map(); // agentId -> [{role, content}]
const MAX_HISTORY = 10;
let store;
let win;
const net = new NetServer({
  onChat: c => win && !win.isDestroyed() && win.webContents.send('net:chat', c),
  onClients: n => win && !win.isDestroyed() && win.webContents.send('net:clients', n),
});

function createWindow() {
  win = new BrowserWindow({
    width: 1280, height: 800, backgroundColor: '#0b0b14', title: 'AI World',
    webPreferences: { preload: path.join(__dirname, 'preload.js'), contextIsolation: true, nodeIntegration: false, sandbox: true },
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
}

app.whenReady().then(() => {
  store = new Store(app.getPath('userData'));

  ipcMain.handle('config:get', () => ({ ...store.load(), providers: PROVIDERS }));
  ipcMain.handle('config:save', (_e, cfg) => {
    store.save({ agents: cfg.agents, turnSeconds: cfg.turnSeconds });
    for (const id of [...histories.keys()]) if (!cfg.agents.some(a => a.id === id)) histories.delete(id);
    return true;
  });

  // La API key nunca sale del proceso principal: el renderer solo manda el id del agente.
  ipcMain.handle('brain:think', async (_e, { agentId, world }) => {
    const agent = store.load().agents.find(a => a.id === agentId);
    if (!agent) return { error: 'Agente no encontrado' };
    const history = histories.get(agentId) || [];
    const perception = brain.buildPerception(agent, world);
    try {
      const raw = await chat({
        agent,
        system: brain.buildSystem(agent),
        messages: brain.toMessages(history, perception),
      });
      const decision = brain.parseDecision(raw);
      history.push({ role: 'user', content: perception }, { role: 'assistant', content: JSON.stringify(decision) });
      histories.set(agentId, history.slice(-MAX_HISTORY));
      return { decision };
    } catch (err) {
      return { error: String(err.message || err) };
    }
  });

  ipcMain.handle('net:start', async () => {
    const info = await net.start();
    const url = info.urls[0] || info.localUrl;
    return { urls: info.urls, url, qr: await QRCode.toDataURL(url, { margin: 1, width: 240 }) };
  });
  ipcMain.handle('net:stop', () => net.stop());
  ipcMain.on('net:event', (_e, ev) => net.event(ev));
  ipcMain.on('net:state', (_e, st) => net.setState(st));

  createWindow();
  app.on('activate', () => { if (BrowserWindow.getAllWindows().length === 0) createWindow(); });
});

app.on('before-quit', () => { net.stop(); });
app.on('window-all-closed', () => { if (process.platform !== 'darwin') app.quit(); });
