# WorkLog Pro Electron版本管理方案

## 1. 版本管理策略

### 1.1 版本号规范
- **语义化版本控制**: `主版本.次版本.修订版本` (如 `1.2.3`)
- **预发布版本**: `1.2.3-beta.1`, `1.2.3-rc.1`
- **构建号**: `1.2.3+20241201.001`

### 1.2 分支策略
- `main`: 稳定版本，用于生产发布
- `develop`: 开发版本，用于测试
- `feature/*`: 功能分支
- `hotfix/*`: 热修复分支

### 1.3 发布类型
- `stable`: 稳定版本
- `beta`: 测试版本
- `alpha`: 内测版本

## 2. 构建和打包流程

### 2.1 自动化构建 (CI/CD)
**GitHub Actions 配置示例:**
```yaml
name: Build and Release
on:
  push:
    tags:
      - 'v*'
  workflow_dispatch:

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [windows-latest, macos-latest, ubuntu-latest]
        node-version: [18.x]
    
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
    
    - name: Install dependencies
      run: npm ci
    
    - name: Build application
      run: npm run build
    
    - name: Build Electron app
      run: npm run electron:build
    
    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: ${{ matrix.os }}-build
        path: dist_electron/
```

### 2.2 构建产物
- **Windows**: `.exe` 安装包 + `.zip` 便携版
- **macOS**: `.dmg` 安装包 + `.zip` 便携版
- **Linux**: `.AppImage` + `.deb` + `.rpm`

### 2.3 构建配置
**electron-builder 配置:**
```json
{
  "appId": "com.worklogpro.app",
  "productName": "WorkLog Pro",
  "directories": {
    "output": "dist_electron"
  },
  "files": [
    "dist/**/*",
    "electron/**/*"
  ],
  "mac": {
    "category": "public.app-category.productivity",
    "target": [
      {
        "target": "dmg",
        "arch": ["x64", "arm64"]
      },
      {
        "target": "zip",
        "arch": ["x64", "arm64"]
      }
    ]
  },
  "win": {
    "target": [
      {
        "target": "nsis",
        "arch": ["x64"]
      },
      {
        "target": "zip",
        "arch": ["x64"]
      }
    ]
  },
  "linux": {
    "target": [
      {
        "target": "AppImage",
        "arch": ["x64"]
      },
      {
        "target": "deb",
        "arch": ["x64"]
      }
    ]
  }
}
```

## 3. 数据库设计

### 3.1 版本信息表
```sql
CREATE TABLE app_versions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version VARCHAR(50) NOT NULL,           -- 版本号
    build_number VARCHAR(50),               -- 构建号
    platform ENUM('windows', 'macos', 'linux') NOT NULL,
    architecture ENUM('x64', 'arm64') DEFAULT 'x64',
    release_type ENUM('stable', 'beta', 'alpha') DEFAULT 'stable',
    download_url VARCHAR(500) NOT NULL,     -- 下载链接
    file_size BIGINT NOT NULL,              -- 文件大小(字节)
    checksum_sha256 VARCHAR(64) NOT NULL,   -- SHA256校验和
    min_system_version VARCHAR(50),         -- 最低系统要求
    release_notes TEXT,                     -- 发布说明
    is_force_update BOOLEAN DEFAULT FALSE,  -- 是否强制更新
    is_active BOOLEAN DEFAULT TRUE,         -- 是否可用
    download_count INT DEFAULT 0,           -- 下载次数
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    released_at TIMESTAMP NULL,             -- 发布时间
    INDEX idx_version_platform (version, platform),
    INDEX idx_active (is_active, platform),
    INDEX idx_release_type (release_type, platform)
);
```

### 3.2 更新日志表
```sql
CREATE TABLE version_changelog (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version_id INT NOT NULL,
    change_type ENUM('feature', 'bugfix', 'security', 'breaking') NOT NULL,
    description TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE
);
```

### 3.3 下载统计表
```sql
CREATE TABLE download_stats (
    id INT PRIMARY KEY AUTO_INCREMENT,
    version_id INT NOT NULL,
    platform ENUM('windows', 'macos', 'linux') NOT NULL,
    user_agent TEXT,
    ip_address VARCHAR(45),
    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (version_id) REFERENCES app_versions(id) ON DELETE CASCADE,
    INDEX idx_download_date (download_date),
    INDEX idx_platform (platform)
);
```

## 4. API设计

### 4.1 版本管理API
```python
# 获取最新版本
@router.get("/versions/latest")
async def get_latest_version(platform: str = None):
    """获取最新版本信息"""
    pass

# 获取特定平台最新版本
@router.get("/versions/{platform}/latest")
async def get_platform_latest_version(platform: str):
    """获取特定平台的最新版本"""
    pass

# 获取版本列表
@router.get("/versions")
async def get_versions(
    platform: str = None,
    release_type: str = None,
    page: int = 1,
    page_size: int = 20
):
    """获取版本列表"""
    pass

# 检查更新
@router.post("/versions/check-update")
async def check_update(
    current_version: str,
    platform: str,
    architecture: str = "x64"
):
    """客户端检查更新"""
    pass

# 记录下载
@router.post("/versions/{version_id}/download")
async def record_download(
    version_id: int,
    platform: str,
    user_agent: str = None,
    ip_address: str = None
):
    """记录下载统计"""
    pass

# 管理员API
@router.post("/admin/versions")
async def create_version(version_data: dict):
    """创建新版本"""
    pass

@router.put("/admin/versions/{version_id}")
async def update_version(version_id: int, version_data: dict):
    """更新版本信息"""
    pass

@router.delete("/admin/versions/{version_id}")
async def delete_version(version_id: int):
    """删除版本"""
    pass
```

## 5. 发布流程

### 5.1 自动化发布流程
1. **代码合并到main分支**
2. **创建版本标签**: `git tag v1.2.3`
3. **推送标签**: `git push origin v1.2.3`
4. **自动触发构建**
   - 更新版本号
   - 生成changelog
   - 构建多平台安装包
   - 上传到CDN/对象存储
5. **自动发布**
   - 更新数据库版本信息
   - 发送通知邮件
   - 更新下载页面

### 5.2 手动发布流程
1. **准备发布**
   - 确认版本号
   - 编写发布说明
   - 测试安装包
2. **上传文件**
   - 上传到CDN
   - 计算校验和
   - 记录版本信息
3. **发布**
   - 更新数据库
   - 发送通知

## 6. 客户端更新机制

### 6.1 自动更新检查
- 应用启动时检查更新
- 定时检查 (如每天一次)
- 手动检查更新

### 6.2 更新策略
- **静默更新**: 后台下载，下次启动时安装
- **提示更新**: 用户确认后下载安装
- **强制更新**: 必须更新才能继续使用

### 6.3 回滚机制
- 保留最近几个版本
- 支持版本回滚
- 紧急修复发布

## 7. 存储和CDN方案

### 7.1 文件存储
- **对象存储**: AWS S3, 阿里云OSS, 腾讯云COS
- **CDN加速**: CloudFlare, 阿里云CDN
- **备用存储**: 本地服务器备份

### 7.2 文件组织
```
downloads/
├── windows/
│   ├── x64/
│   │   ├── WorkLogPro-1.2.3.exe
│   │   └── WorkLogPro-1.2.3.zip
│   └── arm64/
├── macos/
│   ├── x64/
│   │   ├── WorkLogPro-1.2.3.dmg
│   │   └── WorkLogPro-1.2.3.zip
│   └── arm64/
└── linux/
    ├── x64/
    │   ├── WorkLogPro-1.2.3.AppImage
    │   └── WorkLogPro-1.2.3.deb
    └── arm64/
```

## 8. 监控和分析

### 8.1 下载统计
- 实时下载量
- 平台分布
- 版本使用情况
- 更新成功率

### 8.2 错误监控
- 下载失败率
- 安装失败率
- 更新错误日志

## 9. 安全考虑

### 9.1 文件安全
- 数字签名
- 校验和验证
- 防篡改检测

### 9.2 访问控制
- API访问限制
- 下载频率限制
- 地理位置限制

## 10. 实施计划

### 10.1 第一阶段: 基础架构
- [ ] 数据库表设计
- [ ] API接口开发
- [ ] 基础版本管理功能

### 10.2 第二阶段: 构建自动化
- [ ] CI/CD流水线配置
- [ ] 自动化构建脚本
- [ ] 多平台打包配置

### 10.3 第三阶段: 客户端集成
- [ ] 客户端更新检查
- [ ] 自动更新机制
- [ ] 用户界面优化

### 10.4 第四阶段: 监控和优化
- [ ] 下载统计
- [ ] 错误监控
- [ ] 性能优化

## 11. 技术栈

### 11.1 后端
- **框架**: FastAPI
- **数据库**: MySQL/PostgreSQL
- **缓存**: Redis
- **文件存储**: 对象存储 + CDN

### 11.2 前端
- **框架**: Vue 3 + TypeScript
- **UI库**: Element Plus
- **构建工具**: Vite

### 11.3 Electron
- **打包工具**: electron-builder
- **自动更新**: electron-updater
- **签名**: 数字证书

### 11.4 DevOps
- **CI/CD**: GitHub Actions
- **容器化**: Docker
- **监控**: 日志系统 + 错误追踪

## 12. 注意事项

### 12.1 版本兼容性
- 确保新版本向后兼容
- 提供迁移指南
- 支持版本回滚

### 12.2 用户体验
- 更新过程透明化
- 提供更新进度
- 错误处理友好

### 12.3 性能考虑
- 增量更新
- 断点续传
- 后台下载

---

**文档版本**: 1.0  
**创建时间**: 2024-12-01  
**最后更新**: 2024-12-01  
**维护者**: 开发团队
