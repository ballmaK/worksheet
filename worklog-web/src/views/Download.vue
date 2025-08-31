<template>
  <div class="download-container">
    <div class="download-content">
      <!-- 页面标题 -->
      <div class="download-header">
        <h1>下载桌面客户端</h1>
        <p>享受更好的工作体验，下载WorkLog Pro桌面客户端</p>
      </div>

      <!-- 系统检测提示 -->
      <div v-if="detectedOS" class="os-detection">
        <el-alert
          :title="`检测到您的系统: ${detectedOS}`"
          type="info"
          :closable="false"
          show-icon
        >
          <template #default>
            <p>我们为您推荐最适合的版本</p>
          </template>
        </el-alert>
      </div>

      <!-- 下载卡片 -->
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else class="download-cards">
        <!-- Windows版本 -->
        <div class="download-card" :class="{ 'recommended': detectedOS === 'Windows' }">
          <div class="card-header">
            <el-icon class="platform-icon"><Monitor /></el-icon>
            <h3>Windows</h3>
            <span class="version">{{ downloadInfo?.windows?.version || 'v1.0.0' }}</span>
            <el-tag v-if="detectedOS === 'Windows'" type="success" size="small">推荐</el-tag>
          </div>
          <div class="card-content">
            <p>{{ downloadInfo?.windows?.requirements || '支持 Windows 10/11' }}</p>
            <ul>
              <li v-for="feature in downloadInfo?.windows?.features || ['✅ 系统托盘运行', '✅ 全局快捷键', '✅ 自动同步数据', '✅ 离线工作模式']" :key="feature">
                {{ feature }}
              </li>
            </ul>
          </div>
          <div class="card-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="downloadWindows"
              :loading="downloadingWindows"
              :disabled="downloadingWindows"
            >
              <el-icon><Download /></el-icon>
              {{ downloadingWindows ? '下载中...' : '下载 Windows 版本' }}
            </el-button>
            <div class="file-info">
              <span>文件大小: {{ downloadInfo?.windows?.size || '45.2 MB' }}</span>
              <span>更新时间: {{ downloadInfo?.windows?.updated_at || '2025-08-31' }}</span>
            </div>
          </div>
        </div>

        <!-- macOS版本 -->
        <div class="download-card" :class="{ 'recommended': detectedOS === 'macOS' }">
          <div class="card-header">
            <el-icon class="platform-icon"><Apple /></el-icon>
            <h3>macOS</h3>
            <span class="version">{{ downloadInfo?.macos?.version || 'v1.0.0' }}</span>
            <el-tag v-if="detectedOS === 'macOS'" type="success" size="small">推荐</el-tag>
          </div>
          <div class="card-content">
            <p>{{ downloadInfo?.macos?.requirements || '支持 macOS 11.0+' }}</p>
            <ul>
              <li v-for="feature in downloadInfo?.macos?.features || ['✅ 菜单栏集成', '✅ Touch Bar支持', '✅ 自动同步数据', '✅ 离线工作模式']" :key="feature">
                {{ feature }}
              </li>
            </ul>
          </div>
          <div class="card-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="downloadMacOS"
              :loading="downloadingMacOS"
              :disabled="downloadingMacOS"
            >
              <el-icon><Download /></el-icon>
              {{ downloadingMacOS ? '下载中...' : '下载 macOS 版本' }}
            </el-button>
            <div class="file-info">
              <span>文件大小: {{ downloadInfo?.macos?.size || '52.8 MB' }}</span>
              <span>更新时间: {{ downloadInfo?.macos?.updated_at || '2025-08-31' }}</span>
            </div>
          </div>
        </div>

        <!-- Linux版本 -->
        <div class="download-card" :class="{ 'recommended': detectedOS === 'Linux' }">
          <div class="card-header">
            <el-icon class="platform-icon"><Platform /></el-icon>
            <h3>Linux</h3>
            <span class="version">{{ downloadInfo?.linux?.version || 'v1.0.0' }}</span>
            <el-tag v-if="detectedOS === 'Linux'" type="success" size="small">推荐</el-tag>
          </div>
          <div class="card-content">
            <p>{{ downloadInfo?.linux?.requirements || '支持 Ubuntu 20.04+' }}</p>
            <ul>
              <li v-for="feature in downloadInfo?.linux?.features || ['✅ 系统托盘运行', '✅ 全局快捷键', '✅ 自动同步数据', '✅ 离线工作模式']" :key="feature">
                {{ feature }}
              </li>
            </ul>
          </div>
          <div class="card-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="downloadLinux"
              :loading="downloadingLinux"
              :disabled="downloadingLinux"
            >
              <el-icon><Download /></el-icon>
              {{ downloadingLinux ? '下载中...' : '下载 Linux 版本' }}
            </el-button>
            <div class="file-info">
              <span>文件大小: {{ downloadInfo?.linux?.size || '38.5 MB' }}</span>
              <span>更新时间: {{ downloadInfo?.linux?.updated_at || '2025-08-31' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 功能特性 -->
      <div class="features-section">
        <h2>桌面客户端特性</h2>
        <div class="features-grid">
          <div class="feature-item">
            <el-icon class="feature-icon"><Timer /></el-icon>
            <h4>系统托盘运行</h4>
            <p>在系统托盘运行，不占用任务栏空间，随时访问</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Key /></el-icon>
            <h4>全局快捷键</h4>
            <p>支持全局快捷键，快速开始/暂停工作，提高效率</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Refresh /></el-icon>
            <h4>自动同步</h4>
            <p>数据自动同步到云端，多设备无缝切换</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Connection /></el-icon>
            <h4>离线工作</h4>
            <p>支持离线工作模式，网络恢复后自动同步</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Bell /></el-icon>
            <h4>系统通知</h4>
            <p>集成系统通知，重要消息及时提醒</p>
          </div>
          <div class="feature-item">
            <el-icon class="feature-icon"><Setting /></el-icon>
            <h4>个性化设置</h4>
            <p>丰富的个性化设置，满足不同使用习惯</p>
          </div>
        </div>
      </div>

      <!-- 安装说明 -->
      <div class="installation-section">
        <h2>安装说明</h2>
        <div class="installation-steps">
          <div class="step">
            <div class="step-number">1</div>
            <div class="step-content">
              <h4>下载安装包</h4>
              <p>选择对应操作系统的版本下载</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">2</div>
            <div class="step-content">
              <h4>运行安装程序</h4>
              <p>双击安装包，按照提示完成安装</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">3</div>
            <div class="step-content">
              <h4>登录账号</h4>
              <p>使用您的WorkLog Pro账号登录</p>
            </div>
          </div>
          <div class="step">
            <div class="step-number">4</div>
            <div class="step-content">
              <h4>开始使用</h4>
              <p>享受更便捷的工作体验</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 常见问题 -->
      <div class="faq-section">
        <h2>常见问题</h2>
        <el-collapse v-model="activeNames">
          <el-collapse-item title="桌面客户端与网页版有什么区别？" name="1">
            <p>桌面客户端提供更好的系统集成体验，包括系统托盘运行、全局快捷键、系统通知等功能，同时支持离线工作模式。</p>
          </el-collapse-item>
          <el-collapse-item title="数据会同步吗？" name="2">
            <p>是的，桌面客户端会自动同步您的所有数据，包括任务、工作日志、团队信息等，确保多设备数据一致。</p>
          </el-collapse-item>
          <el-collapse-item title="支持哪些操作系统？" name="3">
            <p>目前支持 Windows 10/11、macOS 11.0+ 和 Ubuntu 20.04+ 等主流操作系统。</p>
          </el-collapse-item>
          <el-collapse-item title="如何卸载桌面客户端？" name="4">
            <p>在控制面板（Windows）或应用程序文件夹（macOS）中卸载，卸载不会影响您的云端数据。</p>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Monitor, 
  Apple, 
  Platform, 
  Download, 
  Timer, 
  Key, 
  Refresh, 
  Connection, 
  Bell, 
  Setting 
} from '@element-plus/icons-vue'
import { getDownloads, downloadClient, type DownloadInfo } from '@/api/download'

const activeNames = ref(['1'])
const detectedOS = ref('')
const downloadingWindows = ref(false)
const downloadingMacOS = ref(false)
const downloadingLinux = ref(false)
const downloadInfo = ref<{
  windows: DownloadInfo
  macos: DownloadInfo
  linux: DownloadInfo
} | null>(null)
const loading = ref(false)

// 检测操作系统
const detectOS = () => {
  const userAgent = navigator.userAgent
  if (userAgent.indexOf('Win') !== -1) {
    detectedOS.value = 'Windows'
  } else if (userAgent.indexOf('Mac') !== -1) {
    detectedOS.value = 'macOS'
  } else if (userAgent.indexOf('Linux') !== -1) {
    detectedOS.value = 'Linux'
  }
}

// 模拟下载进度
const simulateDownload = async (platform: string) => {
  return new Promise<void>((resolve) => {
    setTimeout(() => {
      resolve()
    }, 2000)
  })
}

// 下载函数
const downloadWindows = async () => {
  try {
    downloadingWindows.value = true
    
    if (!downloadInfo.value) {
      ElMessage.error('下载信息未加载')
      return
    }
    
    const info = downloadInfo.value.windows
    
    // 显示下载确认对话框
    await ElMessageBox.confirm(
      `即将下载 ${info.name} (${info.size})`,
      '确认下载',
      {
        confirmButtonText: '开始下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    // 模拟下载过程
    await simulateDownload('Windows')
    
    // 使用API下载
    try {
      await downloadClient('windows')
      ElMessage.success('Windows版本下载完成！')
    } catch (error) {
      // 如果API下载失败，使用备用链接
      const link = document.createElement('a')
      link.href = info.url
      link.download = info.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('Windows版本下载完成！')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('下载失败，请稍后重试')
    }
  } finally {
    downloadingWindows.value = false
  }
}

const downloadMacOS = async () => {
  try {
    downloadingMacOS.value = true
    
    if (!downloadInfo.value) {
      ElMessage.error('下载信息未加载')
      return
    }
    
    const info = downloadInfo.value.macos
    
    await ElMessageBox.confirm(
      `即将下载 ${info.name} (${info.size})`,
      '确认下载',
      {
        confirmButtonText: '开始下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    await simulateDownload('macOS')
    
    try {
      await downloadClient('macos')
      ElMessage.success('macOS版本下载完成！')
    } catch (error) {
      const link = document.createElement('a')
      link.href = info.url
      link.download = info.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('macOS版本下载完成！')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('下载失败，请稍后重试')
    }
  } finally {
    downloadingMacOS.value = false
  }
}

const downloadLinux = async () => {
  try {
    downloadingLinux.value = true
    
    if (!downloadInfo.value) {
      ElMessage.error('下载信息未加载')
      return
    }
    
    const info = downloadInfo.value.linux
    
    await ElMessageBox.confirm(
      `即将下载 ${info.name} (${info.size})`,
      '确认下载',
      {
        confirmButtonText: '开始下载',
        cancelButtonText: '取消',
        type: 'info'
      }
    )
    
    await simulateDownload('Linux')
    
    try {
      await downloadClient('linux')
      ElMessage.success('Linux版本下载完成！')
    } catch (error) {
      const link = document.createElement('a')
      link.href = info.url
      link.download = info.filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      ElMessage.success('Linux版本下载完成！')
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('下载失败，请稍后重试')
    }
  } finally {
    downloadingLinux.value = false
  }
}

// 获取下载信息
const fetchDownloadInfo = async () => {
  try {
    loading.value = true
    const response = await getDownloads()
    downloadInfo.value = response.data
  } catch (error) {
    console.error('获取下载信息失败:', error)
    ElMessage.error('获取下载信息失败')
  } finally {
    loading.value = false
  }
}

// 组件挂载时检测操作系统并获取下载信息
onMounted(() => {
  detectOS()
  fetchDownloadInfo()
})
</script>

<style scoped>
.download-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 40px 20px;
}

.download-content {
  max-width: 1200px;
  margin: 0 auto;
}

.download-header {
  text-align: center;
  color: white;
  margin-bottom: 60px;
}

.download-header h1 {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.download-header p {
  font-size: 20px;
  opacity: 0.9;
  margin: 0;
}

.os-detection {
  margin-bottom: 40px;
}

.loading-container {
  margin-bottom: 80px;
}

.download-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
  margin-bottom: 80px;
}

.download-card {
  background: white;
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.download-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.download-card.recommended {
  border: 2px solid #67c23a;
  box-shadow: 0 10px 30px rgba(103, 194, 58, 0.3);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.platform-icon {
  font-size: 32px;
  color: #409eff;
}

.card-header h3 {
  font-size: 24px;
  font-weight: 600;
  margin: 0;
  color: #303133;
}

.version {
  background: #e6f7ff;
  color: #1890ff;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.card-content {
  margin-bottom: 30px;
}

.card-content p {
  color: #606266;
  margin-bottom: 16px;
}

.card-content ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.card-content li {
  color: #606266;
  margin-bottom: 8px;
  font-size: 14px;
}

.card-actions {
  text-align: center;
}

.file-info {
  margin-top: 16px;
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.features-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.features-section h2 {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 40px;
  color: #303133;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-item {
  text-align: center;
  padding: 20px;
}

.feature-icon {
  font-size: 48px;
  color: #409eff;
  margin-bottom: 16px;
}

.feature-item h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #303133;
}

.feature-item p {
  color: #606266;
  line-height: 1.6;
  margin: 0;
}

.installation-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  margin-bottom: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.installation-section h2 {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 40px;
  color: #303133;
}

.installation-steps {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.step-number {
  width: 40px;
  height: 40px;
  background: #409eff;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  flex-shrink: 0;
}

.step-content h4 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #303133;
}

.step-content p {
  color: #606266;
  margin: 0;
  line-height: 1.6;
}

.faq-section {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.faq-section h2 {
  text-align: center;
  font-size: 32px;
  font-weight: 600;
  margin-bottom: 40px;
  color: #303133;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .download-header h1 {
    font-size: 32px;
  }

  .download-header p {
    font-size: 16px;
  }

  .download-cards {
    grid-template-columns: 1fr;
  }

  .features-grid {
    grid-template-columns: 1fr;
  }

  .installation-steps {
    grid-template-columns: 1fr;
  }

  .download-card,
  .features-section,
  .installation-section,
  .faq-section {
    padding: 20px;
  }

  .file-info {
    flex-direction: column;
    gap: 4px;
    text-align: center;
  }
}
</style>
