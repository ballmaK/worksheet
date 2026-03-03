const { app, BrowserWindow, Menu, ipcMain, shell, Notification, Tray, nativeImage, globalShortcut, dialog } = require('electron')
const path = require('path')
const fs = require('fs')
const isDev = process.env.NODE_ENV === 'development'

// Windows 下开发时常见缓存目录沙箱权限问题，开发环境关闭沙箱可避免 "拒绝访问"
if (isDev && process.platform === 'win32') {
  app.commandLine.appendSwitch('no-sandbox')
}

let mainWindow = null
let taskBarWindow = null
let widgetWindow = null // 桌面待办列表小部件（汇总窗口）
const taskCardWindows = {} // 每个任务独立小窗： taskId -> BrowserWindow
let tray = null
let isWorkMode = false
let mainToken = null // 保存主窗口的token
let widgetPinned = false

const WIDGET_STATE_FILE = path.join(app.getPath('userData'), 'desktop-widget-state.json')
const TASK_CARD_OFFSET = 30 // 多任务小窗层叠偏移（像素）
const TASK_CARD_OPACITY = 0.32 // 任务便签窗口透明度（0~1），略透明减少遮挡桌面

// 应用配置
const APP_CONFIG = {
  name: 'WorkLog',
  version: '1.0.0',
  apiUrl: isDev ? 'http://localhost:8000' : 'https://your-api-domain.com',
  webUrl: isDev ? 'http://localhost:5173' : 'https://your-web-domain.com'
}

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev
    },
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    frame: process.platform !== 'darwin',
    backgroundColor: '#ffffff',
    show: false, // 初始不显示主窗口
    icon: path.join(__dirname, '../public/favicon.ico')
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  }

  mainWindow.once('ready-to-show', () => {
    if (!isWorkMode) {
      mainWindow.show()
    }
  })

  mainWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault()
      mainWindow.hide()
    }
  })

  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  createMenu()
}

function createTaskBarWindow() {
  taskBarWindow = new BrowserWindow({
    width: 400,
    height: 600,
    resizable: true,
    minimizable: false, // 禁用最小化，避免焦点问题
    maximizable: false, // 禁用最大化
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev
    },
    show: false,
    frame: false,
    transparent: false,
    alwaysOnTop: isWorkMode,
    skipTaskbar: isWorkMode,
    closable: false,
    title: '工作任务栏',
    backgroundColor: '#ffffff',
    icon: path.join(__dirname, '../public/favicon.ico'),
    focusable: true,
    acceptFirstMouse: true,
    webSecurity: !isDev,
    // 添加更多窗口属性来改善焦点处理
    fullscreenable: false,
    autoHideMenuBar: true,
    // 改善焦点处理
    focusable: true,
    acceptFirstMouse: true,
    // 减少闪烁
    show: false,
    skipTaskbar: isWorkMode
  })

  if (isDev) {
    taskBarWindow.loadURL('http://localhost:5173/floating-task-bar-demo')
    if (!isWorkMode) {
      taskBarWindow.webContents.openDevTools()
    }
  } else {
    taskBarWindow.loadFile(path.join(__dirname, '../dist/index.html'), {
      hash: '/floating-task-bar-demo'
    })
  }

  taskBarWindow.setMovable(true)

  taskBarWindow.once('ready-to-show', () => {
    if (isWorkMode) {
      taskBarWindow.show()
      taskBarWindow.focus()
    }
  })

  taskBarWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault()
      taskBarWindow.hide()
    }
  })

  taskBarWindow.on('focus', () => {
    console.log('任务栏窗口获得焦点')
    // 防止焦点事件导致的闪烁
    if (isWorkMode) {
      // 延迟设置，避免快速切换
      setTimeout(() => {
        if (taskBarWindow && !taskBarWindow.isDestroyed()) {
          taskBarWindow.setAlwaysOnTop(true)
        }
      }, 50)
    }
  })

  taskBarWindow.on('blur', () => {
    console.log('任务栏窗口失去焦点')
    // 在工作模式下，失去焦点时不要隐藏窗口，也不立即重新设置焦点
    if (isWorkMode) {
      // 延迟检查，避免快速切换导致的闪烁
      setTimeout(() => {
        if (taskBarWindow && !taskBarWindow.isDestroyed()) {
          // 不重新设置焦点，避免闪烁
          // taskBarWindow.setAlwaysOnTop(true)
        }
      }, 200)
    }
  })

  // 窗口加载完成后注入token
  taskBarWindow.webContents.on('did-finish-load', () => {
    if (mainToken) {
      console.log('向任务栏窗口注入token')
      taskBarWindow.webContents.executeJavaScript(
        `localStorage.setItem("token", "${mainToken}"); console.log("Token已注入到任务栏窗口");`
      ).catch((error) => {
        console.error('注入token失败:', error)
      })
    } else {
      console.log('主窗口token为空，跳过注入')
    }
  })
}

function loadWidgetState() {
  try {
    if (fs.existsSync(WIDGET_STATE_FILE)) {
      const data = fs.readFileSync(WIDGET_STATE_FILE, 'utf8')
      const state = JSON.parse(data)
      widgetPinned = state.pinned === true
      return state
    }
  } catch (e) {
    console.warn('读取桌面小部件状态失败:', e)
  }
  return null
}

function saveWidgetState() {
  if (!widgetWindow || widgetWindow.isDestroyed()) return
  try {
    const [x, y] = widgetWindow.getPosition()
    const [w, h] = widgetWindow.getSize()
    const state = { x, y, width: w, height: h, pinned: widgetPinned }
    fs.writeFileSync(WIDGET_STATE_FILE, JSON.stringify(state, null, 2), 'utf8')
  } catch (e) {
    console.warn('保存桌面小部件状态失败:', e)
  }
}

function createWidgetWindow() {
  const state = loadWidgetState()
  const defaultWidth = 320
  const defaultHeight = 420
  const { screen } = require('electron')
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize
  const x = state ? state.x : Math.round((screenWidth - defaultWidth) / 2)
  const y = state ? state.y : Math.round((screenHeight - defaultHeight) / 2)
  const width = state?.width || defaultWidth
  const height = state?.height || defaultHeight

  widgetWindow = new BrowserWindow({
    width,
    height,
    x,
    y,
    resizable: true,
    minimizable: true,
    maximizable: false,
    frame: false,
    transparent: false,
    alwaysOnTop: state?.pinned === true,
    skipTaskbar: true,
    closable: true,
    title: '当日待办',
    backgroundColor: '#f5f7fa',
    icon: path.join(__dirname, '../public/favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev
    },
    fullscreenable: false,
    autoHideMenuBar: true,
    show: false
  })

  widgetPinned = state?.pinned === true

  if (isDev) {
    widgetWindow.loadURL('http://localhost:5173/desktop-widget')
  } else {
    widgetWindow.loadFile(path.join(__dirname, '../dist/index.html'), {
      hash: '/desktop-widget'
    })
  }

  widgetWindow.setMovable(true)

  widgetWindow.once('ready-to-show', () => {
    // 不自动显示，由用户从托盘/菜单打开
  })

  widgetWindow.on('close', (event) => {
    if (!app.isQuiting) {
      event.preventDefault()
      widgetWindow.hide()
    }
  })

  widgetWindow.on('closed', () => {
    widgetWindow = null
  })

  widgetWindow.on('move', () => {
    saveWidgetState()
  })
  widgetWindow.on('resize', () => {
    saveWidgetState()
  })

  // 注入 token
  widgetWindow.webContents.on('did-finish-load', () => {
    if (mainToken) {
      widgetWindow.webContents.executeJavaScript(
        `localStorage.setItem("token", "${mainToken}");`
      ).catch(() => {})
    }
  })
}

/** 创建单个任务卡片小窗（每个任务独立窗口） */
function createTaskCardWindow(taskId, index = 0) {
  if (taskCardWindows[taskId] && !taskCardWindows[taskId].isDestroyed()) {
    taskCardWindows[taskId].show()
    taskCardWindows[taskId].focus()
    return
  }
  const { screen } = require('electron')
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize
  const cardWidth = 280
  const cardHeight = 200
  const x = Math.min(80 + index * TASK_CARD_OFFSET, screenWidth - cardWidth - 20)
  const y = Math.min(80 + index * TASK_CARD_OFFSET, screenHeight - cardHeight - 20)

  const win = new BrowserWindow({
    width: cardWidth,
    height: cardHeight,
    x,
    y,
    resizable: true,
    minimizable: true,
    maximizable: false,
    frame: false,
    transparent: false,
    alwaysOnTop: false,
    skipTaskbar: true,
    closable: true,
    title: `任务-${taskId}`,
    backgroundColor: '#fef08a',
    icon: path.join(__dirname, '../public/favicon.ico'),
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      webSecurity: !isDev
    },
    fullscreenable: false,
    autoHideMenuBar: true,
    show: false
  })

  taskCardWindows[taskId] = win
  win.setOpacity(TASK_CARD_OPACITY)

  if (isDev) {
    win.loadURL(`http://localhost:5173/desktop-widget-task?taskId=${taskId}`)
  } else {
    win.loadFile(path.join(__dirname, '../dist/index.html'), {
      hash: `/desktop-widget-task?taskId=${taskId}`
    })
  }

  win.setMovable(true)

  win.once('ready-to-show', () => {
    win.show()
  })

  win.on('closed', () => {
    delete taskCardWindows[taskId]
  })

  win.webContents.on('did-finish-load', () => {
    if (mainToken) {
      win.webContents.executeJavaScript(
        `localStorage.setItem("token", "${mainToken}");`
      ).catch(() => {})
    }
  })
}

function createTray() {
  const iconPath = path.join(__dirname, '../public/favicon.ico')
  const icon = nativeImage.createFromPath(iconPath)
  
  tray = new Tray(icon)
  tray.setToolTip('WorkLog 桌面客户端')
  
  const contextMenu = Menu.buildFromTemplate([
    {
      label: isWorkMode ? '退出工作模式' : '进入工作模式',
      click: () => {
        toggleWorkMode()
      }
    },
    {
      label: '显示主窗口',
      click: () => {
        if (mainWindow) {
          mainWindow.show()
          mainWindow.focus()
        }
      }
    },
    {
      label: '显示任务栏',
      click: () => {
        if (taskBarWindow) {
          taskBarWindow.show()
          taskBarWindow.focus()
        }
      }
    },
    {
      label: '显示待办桌面卡片',
      click: () => {
        if (widgetWindow) {
          widgetWindow.show()
          widgetWindow.focus()
        }
      }
    },
    { type: 'separator' },
    {
      label: '退出',
      click: () => {
        app.quit()
      }
    }
  ])
  
  tray.setContextMenu(contextMenu)
  
  tray.on('click', () => {
    if (isWorkMode) {
      if (taskBarWindow) {
        taskBarWindow.show()
        taskBarWindow.focus()
      }
    } else {
      if (mainWindow) {
        mainWindow.show()
        mainWindow.focus()
      }
    }
  })
}

function createMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '切换工作模式',
          accelerator: 'Ctrl+Shift+W',
          click: () => {
            toggleWorkMode()
          }
        },
        {
          label: '显示任务栏',
          accelerator: 'Ctrl+T',
          click: () => {
            if (taskBarWindow) {
              taskBarWindow.show()
            }
          }
        },
        {
          label: '隐藏任务栏',
          accelerator: 'Ctrl+H',
          click: () => {
            if (taskBarWindow) {
              taskBarWindow.hide()
            }
          }
        },
        {
          label: '显示待办桌面卡片',
          accelerator: 'Ctrl+Shift+D',
          click: () => {
            if (widgetWindow) {
              widgetWindow.show()
              widgetWindow.focus()
            }
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Command+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' }
      ]
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新加载' },
        { role: 'forceReload', label: '强制重新加载' },
        { role: 'toggleDevTools', label: '开发者工具' },
        { type: 'separator' },
        { role: 'resetZoom', label: '重置缩放' },
        { role: 'zoomIn', label: '放大' },
        { role: 'zoomOut', label: '缩小' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '全屏' }
      ]
    },
    {
      label: '工具',
      submenu: [
        {
          label: '设置',
          accelerator: 'CmdOrCtrl+,',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.send('open-settings')
            }
          }
        },
        {
          label: '管理后台',
          click: () => {
            shell.openExternal(`${APP_CONFIG.apiUrl}/docs`)
          }
        },
        { type: 'separator' },
        {
          label: '检查更新',
          click: () => {
            checkForUpdates()
          }
        }
      ]
    },
    {
      label: '帮助',
      submenu: [
        {
          label: '关于',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: '关于',
              message: APP_CONFIG.name,
              detail: `版本: ${APP_CONFIG.version}\n一个高效的工作日志管理工具`
            })
          }
        }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

function registerGlobalShortcuts() {
  // 注册全局快捷键
  globalShortcut.register('CmdOrCtrl+Shift+W', () => {
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
      mainWindow.webContents.send('new-worklog')
    }
  })

  globalShortcut.register('CmdOrCtrl+Shift+T', () => {
    if (taskBarWindow) {
      taskBarWindow.show()
      taskBarWindow.focus()
    }
  })
}

function checkForUpdates() {
  // 检查更新逻辑
  console.log('检查更新...')
  // 这里可以集成自动更新服务
}

function toggleWorkMode() {
  isWorkMode = !isWorkMode
  
  if (isWorkMode) {
    // 进入工作模式
    if (mainWindow) {
      mainWindow.hide()
    }
    if (taskBarWindow) {
      taskBarWindow.setAlwaysOnTop(true)
      taskBarWindow.setSkipTaskbar(true)
      taskBarWindow.show()
      taskBarWindow.focus()
    }
    
    // 更新托盘菜单
    if (tray) {
      const contextMenu = Menu.buildFromTemplate([
        {
          label: '退出工作模式',
          click: () => {
            toggleWorkMode()
          }
        },
        {
          label: '显示主窗口',
          click: () => {
            if (mainWindow) {
              mainWindow.show()
              mainWindow.focus()
            }
          }
        },
        {
          label: '显示任务栏',
          click: () => {
            if (taskBarWindow) {
              taskBarWindow.show()
              taskBarWindow.focus()
            }
          }
        },
        {
          label: '显示待办桌面卡片',
          click: () => {
            if (widgetWindow) {
              widgetWindow.show()
              widgetWindow.focus()
            }
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          click: () => {
            app.quit()
          }
        }
      ])
      tray.setContextMenu(contextMenu)
    }

    // 发送通知
    new Notification({
      title: '工作模式已开启',
      body: '现在只显示悬浮任务栏，主窗口已隐藏',
      icon: path.join(__dirname, '../public/favicon.ico')
    }).show()
    
  } else {
    // 退出工作模式
    if (taskBarWindow) {
      taskBarWindow.setAlwaysOnTop(false)
      taskBarWindow.setSkipTaskbar(false)
      taskBarWindow.hide()
    }
    if (mainWindow) {
      mainWindow.show()
      mainWindow.focus()
    }
    
    // 更新托盘菜单
    if (tray) {
      const contextMenu = Menu.buildFromTemplate([
        {
          label: '进入工作模式',
          click: () => {
            toggleWorkMode()
          }
        },
        {
          label: '显示主窗口',
          click: () => {
            if (mainWindow) {
              mainWindow.show()
              mainWindow.focus()
            }
          }
        },
        {
          label: '显示任务栏',
          click: () => {
            if (taskBarWindow) {
              taskBarWindow.show()
              taskBarWindow.focus()
            }
          }
        },
        {
          label: '显示待办桌面卡片',
          click: () => {
            if (widgetWindow) {
              widgetWindow.show()
              widgetWindow.focus()
            }
          }
        },
        { type: 'separator' },
        {
          label: '退出',
          click: () => {
            app.quit()
          }
        }
      ])
      tray.setContextMenu(contextMenu)
    }

    // 发送通知
    new Notification({
      title: '工作模式已关闭',
      body: '已恢复正常模式',
      icon: path.join(__dirname, '../public/favicon.ico')
    }).show()
  }
}

// IPC 处理器
ipcMain.handle('show-main-window', () => {
  if (mainWindow) {
    mainWindow.show()
    mainWindow.focus()
  }
})

ipcMain.handle('hide-task-bar', () => {
  if (taskBarWindow) {
    taskBarWindow.hide()
  }
})

ipcMain.handle('show-task-bar', () => {
  if (taskBarWindow) {
    taskBarWindow.show()
    taskBarWindow.focus()
  }
})

ipcMain.handle('toggle-work-mode', () => {
  toggleWorkMode()
  return isWorkMode
})

ipcMain.handle('get-work-mode', () => {
  return isWorkMode
})

// 监听token更新
ipcMain.on('update-token', (event, token) => {
  console.log('收到token更新:', token ? '有token' : '无token')
  mainToken = token
})

ipcMain.handle('resize-window', (event, width, height) => {
  if (taskBarWindow) {
    // 确保参数是数字类型
    const windowWidth = typeof width === 'number' ? width : parseInt(width) || 400
    const windowHeight = typeof height === 'number' ? height : parseInt(height) || 600
    
    taskBarWindow.setSize(windowWidth, windowHeight)
    const { screen } = require('electron')
    const primaryDisplay = screen.getPrimaryDisplay()
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize
    const x = Math.round((screenWidth - windowWidth) / 2)
    const y = Math.round((screenHeight - windowHeight) / 2)
    
    console.log(`调整窗口大小: ${windowWidth}x${windowHeight}, 位置: (${x}, ${y})`)
    taskBarWindow.setPosition(x, y)
  }
})

ipcMain.handle('move-window-to', (event, x, y) => {
  if (taskBarWindow) {
    // 确保参数是数字类型
    const posX = typeof x === 'number' ? x : parseInt(x) || 0
    const posY = typeof y === 'number' ? y : parseInt(y) || 0
    
    const { screen } = require('electron')
    const primaryDisplay = screen.getPrimaryDisplay()
    const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize
    const [windowWidth, windowHeight] = taskBarWindow.getSize()
    
    // 确保窗口不会移出屏幕边界
    const clampedX = Math.max(0, Math.min(screenWidth - windowWidth, posX))
    const clampedY = Math.max(0, Math.min(screenHeight - windowHeight, posY))
    
    console.log(`移动窗口到位置: (${clampedX}, ${clampedY})`)
    taskBarWindow.setPosition(Math.round(clampedX), Math.round(clampedY))
  }
})

ipcMain.handle('get-window-position', () => {
  if (taskBarWindow) {
    return taskBarWindow.getPosition()
  }
  return [0, 0]
})

// 桌面待办小部件 IPC（列表窗与每个任务独立小窗共用，通过 event.sender 区分）
function getWidgetWin(event) {
  const win = BrowserWindow.fromWebContents(event.sender)
  return win && !win.isDestroyed() ? win : null
}

ipcMain.handle('widget-get-position', (event) => {
  const win = getWidgetWin(event)
  return win ? win.getPosition() : [0, 0]
})

ipcMain.handle('widget-move-to', (event, x, y) => {
  const win = getWidgetWin(event)
  if (!win) return
  const { screen } = require('electron')
  const primaryDisplay = screen.getPrimaryDisplay()
  const { width: screenWidth, height: screenHeight } = primaryDisplay.workAreaSize
  const [w, h] = win.getSize()
  const clampedX = Math.max(0, Math.min(screenWidth - w, typeof x === 'number' ? x : parseInt(x) || 0))
  const clampedY = Math.max(0, Math.min(screenHeight - h, typeof y === 'number' ? y : parseInt(y) || 0))
  win.setPosition(Math.round(clampedX), Math.round(clampedY))
})

ipcMain.handle('widget-set-always-on-top', (event, onTop) => {
  const win = getWidgetWin(event)
  if (!win) return false
  win.setAlwaysOnTop(!!onTop)
  if (win === widgetWindow) {
    widgetPinned = !!onTop
    saveWidgetState()
  }
  return !!onTop
})

ipcMain.handle('widget-get-pinned', (event) => {
  const win = getWidgetWin(event)
  return win ? win.isAlwaysOnTop() : false
})

ipcMain.handle('widget-resize', (event, width, height) => {
  const win = getWidgetWin(event)
  if (!win) return
  const w = typeof width === 'number' ? width : parseInt(width) || 320
  const h = typeof height === 'number' ? height : parseInt(height) || 420
  win.setSize(w, h)
})

ipcMain.handle('widget-hide', (event) => {
  const win = getWidgetWin(event)
  if (win) win.hide()
})

ipcMain.handle('create-task-card-window', (event, taskId, index) => {
  createTaskCardWindow(taskId, index ?? 0)
})

ipcMain.handle('open-external', (event, url) => {
  shell.openExternal(url)
})

ipcMain.handle('show-notification', (event, options) => {
  const notification = new Notification({
    title: options.title || 'WorkLog 通知',
    body: options.body || '',
    icon: options.icon || path.join(__dirname, '../public/favicon.ico'),
    silent: options.silent || false
  })
  
  notification.show()
  
  if (options.onClick) {
    notification.on('click', () => {
      if (mainWindow) {
        mainWindow.show()
        mainWindow.focus()
      }
    })
  }
})

// 应用生命周期
app.whenReady().then(() => {
  createMainWindow()
  createTaskBarWindow()
  createWidgetWindow()
  createTray()
  registerGlobalShortcuts()
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('before-quit', () => {
  app.isQuiting = true
}) 