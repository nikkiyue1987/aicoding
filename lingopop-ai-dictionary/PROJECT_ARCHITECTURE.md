# LingoPop AI Dictionary 项目架构详解

## 📋 项目概述

**LingoPop AI Dictionary** 是一个基于 AI 的智能语言学习词典应用，帮助用户学习外语单词和短语。

---

## 🛠️ 技术栈

### 前端框架
- **React 19.2.1** - 现代化的 UI 框架
- **TypeScript 5.8.2** - 类型安全的 JavaScript 超集
- **Vite 6.2.0** - 快速的前端构建工具

### UI 组件库
- **Lucide React** - 精美的图标库
- **原生 CSS** - 自定义样式，使用 Tailwind CSS 类名风格

### AI 服务
- **MiniMax API** - 国内 AI 服务提供商
  - 文本生成（对话、解释）
  - 图片生成
  - 语音合成（TTS）

---

## 📁 项目结构

\`\`\`
lingopop-ai-dictionary/
├── components/              # React 组件
│   ├── LanguageSetup.tsx   # 语言选择界面
│   ├── DictionaryView.tsx  # 词典查询界面
│   ├── NotebookView.tsx    # 笔记本界面
│   └── FlashcardView.tsx   # 闪卡学习界面
├── services/                # 服务层
│   ├── minimaxService.ts   # MiniMax API 调用
│   └── audioUtils.ts       # 音频播放工具
├── App.tsx                  # 主应用组件
├── types.ts                 # TypeScript 类型定义
├── constants.ts             # 常量配置
├── index.tsx                # 应用入口
├── index.html               # HTML 模板
├── vite.config.ts           # Vite 配置
└── .env.local               # 环境变量（API Key）
\`\`\`

---

## 🎯 核心模块功能

### 1️⃣ **App.tsx** - 主应用控制器

**职责：**
- 应用状态管理（模式切换、语言设置、笔记本数据）
- 本地存储管理（LocalStorage）
- 路由控制（4个视图模式）

**核心状态：**
\`\`\`typescript
mode: 'setup' | 'dictionary' | 'notebook' | 'flashcards'
nativeLang: Language        // 母语
targetLang: Language        // 目标语言
notebook: DictionaryEntry[] // 保存的单词
savedIds: Set<string>       // 已保存单词的 ID 集合
\`\`\`

**功能：**
- 底部导航栏（3个按钮：笔记本、搜索、学习）
- 数据持久化到 LocalStorage
- 视图切换逻辑

---

### 2️⃣ **components/** - 视图组件

#### **LanguageSetup.tsx** - 语言设置
- 首次使用时选择母语和目标语言
- 支持 10+ 种语言（英语、中文、西班牙语等）
- 选择后保存到 LocalStorage

#### **DictionaryView.tsx** - 词典查询（核心功能）
**功能：**
- 🔍 搜索单词/短语
- 📝 显示 AI 生成的解释
- 🖼️ 生成单词配图
- 🔊 语音朗读（TTS）
- 💬 AI 聊天对话
- 💾 保存到笔记本

**AI 功能调用：**
\`\`\`typescript
// 1. 查询单词解释
lookupWord(query, nativeLang, targetLang)
  → 返回：explanation, examples, casualNote, synonyms

// 2. 生成配图
generateImageForWord(query)
  → 返回：图片 URL 或 base64

// 3. 语音朗读
speakText(text)
  → 播放 MP3 音频

// 4. AI 聊天
createChatSession(word, targetLang, nativeLang)
  → 返回聊天会话对象
\`\`\`

#### **NotebookView.tsx** - 笔记本
**功能：**
- 📚 显示所有保存的单词
- 🎨 故事生成器（用保存的单词生成故事）
- 🔊 单词发音
- 🗑️ 删除单词

**AI 功能：**
\`\`\`typescript
generateStoryFromWords(words, targetLang, nativeLang)
  → 生成包含这些单词的创意故事
\`\`\`

#### **FlashcardView.tsx** - 闪卡学习
**功能：**
- 📇 卡片翻转效果
- ⏭️ 上一张/下一张
- 🔊 发音功能
- 正面：单词 + 配图
- 背面：解释 + 例句

---

### 3️⃣ **services/** - 服务层

#### **minimaxService.ts** - MiniMax API 集成

**核心函数：**

| 函数名 | 功能 | API 端点 | 模型 |
|--------|------|----------|------|
| `lookupWord` | 查询单词解释 | `/v1/text/chatcompletion_v2` | abab6.5s-chat |
| `generateImageForWord` | 生成配图 | `/v1/image_generation` | image-01 |
| `speakText` | 语音合成 | `/v1/t2a_v2` | speech-02-hd |
| `generateStoryFromWords` | 生成故事 | `/v1/text/chatcompletion_v2` | abab6.5s-chat |
| `ChatSession` | 聊天会话 | `/v1/text/chatcompletion_v2` | abab6.5s-chat |

**关键实现细节：**
\`\`\`typescript
// 1. 从 JWT Token 提取 GroupID
function getGroupId(): string {
  const payload = JSON.parse(atob(apiKey.split('.')[1]));
  return payload.GroupID;
}

// 2. API 请求格式
fetch(\`\${API_BASE_URL}/v1/text/chatcompletion_v2?GroupId=\${groupId}\`, {
  method: 'POST',
  headers: {
    'Authorization': \`Bearer \${apiKey}\`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    model: 'abab6.5s-chat',
    bot_setting: [{
      bot_name: 'AI Assistant',
      content: 'System prompt...'
    }],
    messages: [...],
    tokens_to_generate: 2048,
  }),
});
\`\`\`

#### **audioUtils.ts** - 音频播放工具

**功能：**
- `playPCMData()` - 播放 PCM 格式音频（原 Gemini TTS）
- `playMp3FromBase64()` - 播放 base64 编码的 MP3（MiniMax TTS）
- `playAudioFromUrl()` - 播放 URL 音频

---

### 4️⃣ **types.ts** - 类型定义

**核心类型：**

\`\`\`typescript
// 语言定义
interface Language {
  code: 'en' | 'zh' | 'es' | ...
  name: string
  flag: string  // Emoji 旗帜
}

// 词典条目
interface DictionaryEntry {
  id: string
  word: string
  explanation: string
  examples: ExampleSentence[]
  casualNote: string
  synonyms: string[]
  imageUrl?: string
  timestamp: number
}

// 例句
interface ExampleSentence {
  target: string   // 目标语言
  native: string   // 母语翻译
}
\`\`\`

---

## 🔄 数据流程

### 查询单词流程

\`\`\`mermaid
graph LR
    A[用户输入单词] --> B[DictionaryView]
    B --> C[minimaxService.lookupWord]
    C --> D[MiniMax API]
    D --> E[返回解释/例句/同义词]
    E --> B
    B --> F[显示结果]
    
    B --> G[minimaxService.generateImageForWord]
    G --> H[MiniMax Image API]
    H --> I[返回图片]
    I --> B
\`\`\`

### 数据持久化

\`\`\`mermaid
graph TD
    A[用户保存单词] --> B[App.handleSaveWord]
    B --> C[更新 notebook 状态]
    C --> D[useEffect 监听]
    D --> E[localStorage.setItem]
    
    F[应用启动] --> G[useEffect]
    G --> H[localStorage.getItem]
    H --> I[恢复 notebook 数据]
\`\`\`

---

## 🎨 UI 设计特点

1. **现代化设计**
   - 渐变背景
   - 卡片式布局
   - 圆角设计
   - 阴影效果

2. **交互动画**
   - 按钮 hover 效果
   - 卡片翻转动画
   - 页面切换过渡

3. **响应式布局**
   - 移动端优先
   - 底部导航栏
   - 固定搜索栏

---

## 🔧 配置文件

### **vite.config.ts**
\`\`\`typescript
export default defineConfig({
  server: { port: 3000 },
  plugins: [react()],
  define: {
    'process.env.API_KEY': JSON.stringify(env.MINIMAX_API_KEY),
  },
});
\`\`\`

### **.env.local**
\`\`\`
MINIMAX_API_KEY=your_jwt_token_here
\`\`\`

---

## 🚀 运行流程

1. **启动开发服务器**
   \`\`\`bash
   npm run dev
   \`\`\`

2. **首次使用**
   - 选择母语和目标语言
   - 数据保存到 LocalStorage

3. **查询单词**
   - 输入单词 → API 调用 → 显示结果
   - 可选：保存、发音、聊天

4. **学习模式**
   - 笔记本：查看保存的单词
   - 闪卡：翻卡学习

---

## 📊 总结

| 模块 | 职责 | 技术 |
|------|------|------|
| App.tsx | 状态管理、路由 | React Hooks, LocalStorage |
| Components | UI 渲染、用户交互 | React, TypeScript |
| Services | API 调用、数据处理 | Fetch API, MiniMax SDK |
| Types | 类型安全 | TypeScript Interfaces |

这是一个**单页应用（SPA）**，使用 **React + TypeScript + Vite** 构建，集成 **MiniMax AI** 提供智能语言学习功能。
