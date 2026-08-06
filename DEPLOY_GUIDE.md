---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'a1c54fbc-997c-436f-8d95-fee79f754d31'
  PropagateID: 'a1c54fbc-997c-436f-8d95-fee79f754d31'
  ReservedCode1: '55df207f-e101-4d98-a972-1d5c4f2ab2f3'
  ReservedCode2: '55df207f-e101-4d98-a972-1d5c4f2ab2f3'
---

# 蛋仔作业大闯关 PWA - 部署与配置指南

## 一、Firebase 云同步配置（必须）

当前 PWA 版的 Firebase 配置为占位符，需要替换为你的真实 Firebase 项目信息。

### 步骤 1：创建 Firebase 项目

1. 访问 [Firebase Console](https://console.firebase.google.com/)
2. 点击"添加项目"，输入项目名称（如 `egg-homework`）
3. 按提示完成创建（可关闭 Google Analytics）

### 步骤 2：注册 Web 应用

1. 在项目概览页点击 `</>` 图标（添加 Web 应用）
2. 输入应用昵称（如 `egg-homework-web`）
3. 勾选"同时设置 Firebase Hosting"
4. 点击注册

### 步骤 3：获取配置信息

注册完成后，Firebase 会显示类似如下配置：

```js
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "egg-homework.firebaseapp.com",
  projectId: "egg-homework",
  storageBucket: "egg-homework.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

### 步骤 4：启用 Firestore 数据库

1. 在 Firebase Console 左侧菜单 → Firestore Database
2. 点击"创建数据库"
3. 选择"以测试模式启动"（开发阶段用，上线前需改为正式规则）
4. 选择地区（推荐 `asia-east1` 香港 或 `asia-northeast1` 东京）

### 步骤 5：替换配置

打开 `index.html`，搜索 `FIREBASE_CONFIG`，将占位符替换为你的真实配置：

```js
const FIREBASE_CONFIG = {
  apiKey: "你的真实apiKey",
  authDomain: "你的真实authDomain",
  projectId: "你的真实projectId",
  storageBucket: "你的真实storageBucket",
  messagingSenderId: "你的真实messagingSenderId",
  appId: "你的真实appId"
};
```

### 步骤 6：设置 Firestore 安全规则（上线前必做）

在 Firebase Console → Firestore Database → 规则，替换为：

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /families/{doc} {
      allow read, write: if true; // 开发阶段允许全部访问
      // 上线后改为需要认证：
      // allow read, write: if request.auth != null;
    }
  }
}
```

---

## 二、部署方案

### 方案 A：Firebase Hosting（推荐，免费额度充足）

```bash
# 1. 安装 Firebase CLI
npm install -g firebase-tools

# 2. 登录 Firebase
firebase login

# 3. 初始化（在 egg-homework-pwa 目录下）
firebase init
# 选择 Hosting，选择你刚创建的项目
# 公共目录填 .（当前目录）
# 单页应用选 Yes
# 不用 GitHub Actions

# 4. 部署
firebase deploy
```

部署成功后会获得一个 `https://你的项目.web.app` 的 URL。

### 方案 B：其他静态托管

将 `egg-homework-pwa` 目录下所有文件上传到任意静态托管服务：
- Vercel
- Netlify
- GitHub Pages
- 阿里云 OSS / 腾讯云 COS（配置静态网站托管）

---

## 三、手机安装为 App

### iPhone (Safari)
1. 用 Safari 打开部署后的 URL
2. 点击底部分享按钮 `⬆️`
3. 选择"添加到主屏幕"
4. 点击"添加"即可在桌面看到蛋仔闯关图标

### Android (Chrome)
1. 用 Chrome 打开部署后的 URL
2. 浏览器会弹出"添加到主屏幕"提示，点击即可
3. 如未提示，点击菜单 `⋮` → "安装应用"

---

## 四、文件结构

```
egg-homework-pwa/
├── index.html          # 主应用（含Firebase SDK + 响应式CSS）
├── manifest.json       # PWA 清单
├── sw.js               # Service Worker 离线缓存
├── icons/
│   ├── icon-192x192.png
│   └── icon-512x512.png
└── DEPLOY_GUIDE.md     # 本文件
```

---

## 五、功能说明

- **云端同步**：配置 Firebase 后，数据自动云端备份，多设备同步
- **离线可用**：Service Worker 缓存核心文件，离线也能使用
- **本地优先**：即使 Firebase 未配置，应用仍可正常使用（本地 localStorage 模式）
- **同步指示器**：页面右上角显示 `☁️ 已同步` 或 `☁️ 本地模式`
- **响应式**：自适应手机、平板、桌面（769px 以上居中显示，最大宽度 600px）

---

## 六、常见问题

**Q: Firebase 连接失败怎么办？**
A: 检查配置信息是否正确替换，确认 Firestore 数据库已启用。应用会自动降级为本地模式，不影响使用。

**Q: 数据存在哪里？**
A: 优先云端（Firestore），本地也有 localStorage 缓存。云端数据按家庭文档ID隔离。

**Q: 如何清除本地数据？**
A: 浏览器开发者工具 → Application → Local Storage → 删除 `egg_homework_v4` 键。

**Q: 多个孩子数据会混淆吗？**
A: 不会。每个学生有独立 ID，所有数据（任务、星星、经验、解锁角色等）完全隔离。

> AI生成