'use strict';
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('aiWorld', {
  getConfig: () => ipcRenderer.invoke('config:get'),
  saveConfig: cfg => ipcRenderer.invoke('config:save', cfg),
  netStart: () => ipcRenderer.invoke('net:start'),
  netStop: () => ipcRenderer.invoke('net:stop'),
  netEvent: ev => ipcRenderer.send('net:event', ev),
  netState: st => ipcRenderer.send('net:state', st),
  onNetChat: cb => ipcRenderer.on('net:chat', (_e, c) => cb(c)),
  onNetClients: cb => ipcRenderer.on('net:clients', (_e, n) => cb(n)),
  think: payload => ipcRenderer.invoke('brain:think', payload),
});
