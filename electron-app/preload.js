const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  generateIdeas: (prompt) => ipcRenderer.invoke('generate-ideas', prompt)
});
