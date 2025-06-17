const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { OpenAI } = require('openai');
require('dotenv').config();

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function generateIdeas(prompt) {
  const sys = '你是一个头脑风暴助手，针对用户的问题提供3到5个发散性的思考点，每个思考点一句话，以JSON数组返回。';
  const res = await openai.chat.completions.create({
    model: 'gpt-3.5-turbo',
    messages: [
      { role: 'system', content: sys },
      { role: 'user', content: prompt }
    ]
  });
  const text = res.choices[0].message.content.trim();
  try {
    return JSON.parse(text);
  } catch (_) {
    return text.split(/\n+/).map(l => l.replace(/^[\-\*\d\.\s]+/, '')).filter(Boolean);
  }
}

function createWindow() {
  const win = new BrowserWindow({
    width: 900,
    height: 700,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);

ipcMain.handle('generate-ideas', async (_e, prompt) => {
  try {
    const ideas = await generateIdeas(prompt);
    return ideas.slice(0, 5);
  } catch (err) {
    return { error: String(err) };
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});
