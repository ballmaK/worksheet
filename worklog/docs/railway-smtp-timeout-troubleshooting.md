# Railway 上邮件服务器连接超时排查

## 一、最可能的原因：Railway 出站限制

**Railway 在 Free / Trial / Hobby 计划上会封锁 SMTP 出站端口 465 和 587**，直接连 `smtp.163.com:465` 会表现为连接超时。

- **Pro 及以上**：开放 465、587，SMTP 可用。
- **Free / Trial / Hobby**：只能走 HTTPS 发信（如 Resend、Brevo 等），不能直连 SMTP。

### 如何确认

1. **看当前计划**  
   Railway Dashboard → 你的项目 → **Settings** / **Billing**，确认是 Free / Trial / Hobby 还是 Pro。

2. **看部署日志**  
   Deployments → 选一次部署 → **View Logs**。发邮件时的报错通常是：
   - `Connection timeout` / `TimeoutError`
   - 或 `Connection refused`（端口被拦）

3. **在 Railway 运行环境里测出站**（可选）  
   必须在**已部署的容器内**执行，才能验证 Railway 出站是否放行 465。

   **步骤：**

   - 安装 [Railway CLI](https://docs.railway.app/develop/cli)（若未安装）：
     ```bash
     npm i -g @railway/cli
     # 或: corepack enable && corepack prepare railway@latest --activate
     ```
   - 在项目目录登录并链到当前项目：
     ```bash
     railway login
     railway link   # 按提示选择项目、环境、服务
     ```
   - 用 **SSH 进到部署中的容器**（不是本地 shell）：
     ```bash
     railway ssh
     ```
     进入容器后，执行：
     ```bash
     # 测试 465 是否可达（约 5 秒超时，避免长时间卡住）
     timeout 5 bash -c 'echo | openssl s_client -connect smtp.163.com:465 -servername smtp.163.com' 2>&1 || true
     ```
   - **结果含义**：
     - 若输出里有 `CONNECTED` 和证书信息 → 容器出站 465 通，问题多半在账号/配置或 163 限流。
     - 若超时、无输出或 `Connection timed out` → 说明 Railway 该计划下出站 465 被拦或不可达，需改用 API 发信或升级 Pro。
   - 若镜像里没有 `openssl`，可用 Python 测 TCP：
     ```bash
     python3 -c "
     import socket
     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     s.settimeout(5)
     try:
         s.connect(('smtp.163.com', 465))
         print('OK: 465 reachable')
     except Exception as e:
         print('FAIL:', e)
     s.close()
     "
     ```

---

## 二、排查步骤（按顺序做）

### 1. 确认环境变量

在 Railway 项目 → **Variables** 里确认已设且无误：

| 变量 | 说明 | 示例 |
|------|------|------|
| `SMTP_HOST` | SMTP 服务器 | `smtp.163.com` |
| `SMTP_PORT` | 端口（163 用 SSL 时多为 465） | `465` |
| `SMTP_USER` | 登录账号（163 为完整邮箱） | `your@163.com` |
| `SMTP_PASSWORD` | 授权码（不是登录密码） | 在 163 邮箱设置里开「SMTP」后获取 |
| `EMAILS_FROM_EMAIL` | 发件人邮箱 | 同 `SMTP_USER` |
| `SMTP_TLS` | 是否用 STARTTLS（**465 端口必须为 false**，见下） | `false` |

**重要**：163 的 **465 端口**是「一连接就 SSL」（隐式 SSL），**不是** STARTTLS。若误设 `SMTP_TLS=true`，客户端会按 STARTTLS 去连 465，和服务器对不上，表现为**一直连不上/超时**。代码已对 465 做强制：无论环境变量如何，465 都使用 SSL、不用 STARTTLS。若你之前设过 `SMTP_TLS=true`，可改为 `false` 或删掉该变量。

### 2. 看应用日志里的邮件配置

部署后触发一次「发邮件」（如忘记密码、邀请），在 **View Logs** 里应能看到类似：

```
[Mail] 生产环境邮件配置:
  SMTP_HOST: smtp.163.com
  SMTP_PORT: 465
  SMTP_USER: your@163.com
  ...
```

确认没有 `未配置邮箱用户` 等占位值，否则会认证失败（不一定是超时，但先排除配置错误）。

### 3. 确认是否为「连接阶段」超时

- **连接阶段超时**（连不上 `smtp.163.com:465`）：多半是 **Railway 出站封 465** 或 **163 封云 IP**。
- **连接上了但后面报错**：多半是认证或 TLS/SSL 配置（账号、授权码、端口、TLS 开关）。

日志里出现 `Connection timeout`、`TimeoutError`、`Connection refused` 等，优先按「连接阶段」处理。

---

## 三、解决方案

### 方案 A：升级到 Railway Pro（继续用 163 SMTP）

- 升级后 465/587 出站会放开，现有 `smtp.163.com:465` 配置可继续用。
- 适合：必须用 163 且可接受 Pro 费用。

### 方案 B：改用带 HTTPS API 的邮件服务（推荐，所有计划可用）

不经过 SMTP 端口，用 HTTP API 发信，不受 Railway 出站限制：

| 服务 | 说明 |
|------|------|
| **Resend** | 有免费额度，API 简单，需改代码用其 SDK 或 HTTP。 |
| **Brevo（原 Sendinblue）** | 有免费额度，提供 SMTP 和 API；在 Railway 上建议用 API。 |
| **SendGrid** | 常见 transactional 邮件服务，走 API。 |
| **阿里云 / 腾讯云邮件** | 国内服务，若有云账号可直接用其 API。 |

需要做的改动：

- 在配置里增加：发信方式（如 `MAIL_BACKEND=resend`）、API Key 等。
- 在 `worklog/app/core/email.py` 中：  
  - 当 `MAIL_BACKEND=resend`（或类似）时，走 Resend 的 HTTP 请求；  
  - 否则保持现有 FastAPI-Mail + SMTP 逻辑（本地或 Pro 上用）。

这样在 Railway Free/Trial/Hobby 上不会连 SMTP，自然不会有「连邮件服务器超时」的问题。

### 方案 C：163 或运营商封了云机房 IP

若已确认是 **Pro 计划** 且 465 在 Railway 上可用，仍超时，可能是：

- 163 对海外或云机房 IP 限流/拦截。
- 解决思路：
  - 换用 Resend/Brevo 等（走 HTTPS，且多为海外服务，不被 163 限制）；
  - 或换用支持 SMTP 的海外邮箱（如 Gmail 用 587 + STARTTLS），再在 Railway 上测试。

---

## 四、本地/自建环境可选的超时配置

若在**非 Railway**（如本地、自建 VPS）上只是「偶尔超时」，可适当加大 SMTP 连接超时（例如 30s → 60s）。  
当前项目使用 `fastapi-mail`（底层 aiosmtplib），若其 `ConnectionConfig` 支持 `timeout` 参数，可在配置中增加 `SMTP_TIMEOUT` 环境变量并传入。  
**注意**：在 Railway Free/Trial/Hobby 上，端口被拦时再大的超时也会超时，应先按上面方案 A/B 处理。

---

## 五、小结

| 现象 | 优先排查 | 建议 |
|------|----------|------|
| Railway 上连 163 超时 | 当前是否为 Free/Trial/Hobby | 是 → 改用 Resend/Brevo 等 API，或升级 Pro |
| 配置/日志里有「未配置」 | 环境变量是否在 Railway Variables 里正确设置 | 补全并重部署 |
| 已用 Pro 仍超时 | 163 是否封云 IP、端口是否真开放 | 换邮件服务或换 587+STARTTLS 邮箱测试 |

**最省事的做法**：在 Railway 非 Pro 计划上，直接选用 **Resend 或 Brevo** 的 HTTP API 发邮件，避免 SMTP 端口被拦导致的「连接邮件服务器超时」。
