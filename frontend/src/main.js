import { app, BrowserWindow, dialog, ipcMain } from 'electron';
import path from 'node:path';
import fs from 'node:fs';
import { spawn } from 'node:child_process';
import started from 'electron-squirrel-startup';

// Handle creating/removing shortcuts on Windows when installing/uninstalling.
if (started) {
  app.quit();
}

const BACKEND_HEALTH_URL = 'http://127.0.0.1:8000/health';
const BACKEND_STARTUP_TIMEOUT_MS = 15000;
const BACKEND_STARTUP_POLL_INTERVAL_MS = 300;

let backendProcess = null;

const sleep = (ms) => new Promise((resolve) => {
  setTimeout(resolve, ms);
});

const resolveBackendCwd = () => {
  const candidates = [
    path.resolve(process.cwd(), '..'),
    path.resolve(process.cwd()),
    path.resolve(__dirname, '../../..'),
    path.resolve(__dirname, '../../../..'),
  ];

  for (const candidate of candidates) {
    const apiPath = path.join(candidate, 'src', 'api.py');
    if (fs.existsSync(apiPath)) {
      return candidate;
    }
  }

  return path.resolve(process.cwd(), '..');
};

const stopBackend = () => {
  if (!backendProcess) {
    return;
  }

  backendProcess.kill('SIGTERM');
  backendProcess = null;
};

const waitForBackendReady = async () => {
  const start = Date.now();
  while (Date.now() - start < BACKEND_STARTUP_TIMEOUT_MS) {
    try {
      const response = await fetch(BACKEND_HEALTH_URL);
      if (response.ok) {
        return true;
      }
    } catch {
      // Ignore transient connection failures while backend starts.
    }

    await sleep(BACKEND_STARTUP_POLL_INTERVAL_MS);
  }

  return false;
};

const startBackend = async () => {
  if (backendProcess) {
    return true;
  }

  const backendCwd = resolveBackendCwd();
  const pythonCommand = process.env.BACKEND_PYTHON || (process.platform === 'win32' ? 'python' : 'python3');
  const backendArgs = ['-m', 'uvicorn', 'src.api:app', '--port', '8000'];

  backendProcess = spawn(pythonCommand, backendArgs, {
    cwd: backendCwd,
    env: process.env,
    stdio: ['ignore', 'pipe', 'pipe'],
  });

  backendProcess.stdout.on('data', (data) => {
    console.log(`[backend] ${String(data).trimEnd()}`);
  });

  backendProcess.stderr.on('data', (data) => {
    console.error(`[backend] ${String(data).trimEnd()}`);
  });

  backendProcess.on('exit', (code, signal) => {
    console.log(`[backend] exited with code=${code} signal=${signal}`);
    backendProcess = null;
  });

  const ready = await waitForBackendReady();
  if (!ready) {
    stopBackend();
    return false;
  }

  return true;
};

const createWindow = () => {
  // Create the browser window.
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
    },
  });

  // and load the index.html of the app.
  if (MAIN_WINDOW_VITE_DEV_SERVER_URL) {
    mainWindow.loadURL(MAIN_WINDOW_VITE_DEV_SERVER_URL);
  } else {
    mainWindow.loadFile(path.join(__dirname, `../renderer/${MAIN_WINDOW_VITE_NAME}/index.html`));
  }
};

ipcMain.handle('dialog:openProject', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile', 'openDirectory'],
    filters: [
      { name: 'Projects', extensions: ['zip'] },
    ],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }
  return result.filePaths[0];
});

ipcMain.handle('dialog:openThumbnail', async () => {
  const result = await dialog.showOpenDialog({
    properties: ['openFile'],
    filters: [
      { name: 'Images', extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'] },
    ],
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  return result.filePaths[0];
});

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(async () => {
  const backendReady = await startBackend();
  if (!backendReady) {
    dialog.showErrorBox(
      'Backend Startup Failed',
      'Unable to start the local API backend on http://127.0.0.1:8000.',
    );
    app.quit();
    return;
  }

  createWindow();

  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  stopBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  stopBackend();
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and import them here.
