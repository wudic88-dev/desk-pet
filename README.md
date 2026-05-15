# 桌宠小橘

> 我的第一个 [Vibe Coding](https://x.com/karpathy/status/1886194369901175178) 练手项目。
>
> 代码写得比较随意，权当抛砖引玉，有需要的同学可以拿来学习、重构或魔改。

一只会陪你聊天的橘猫桌面宠物，支持 AI 对话、动画互动、系统托盘、设置面板等功能。

![pet](assets/pet/idle/idle_0.png)

## 功能

- **透明无边框窗口** — 猫咪悬浮在桌面，不影响正常工作
- **帧动画系统** — idle（待机）、click（点击）、talk（对话）三种状态
- **AI 对话** — 接入 DeepSeek/Moonshot 等兼容 OpenAI 格式的 API，流式输出
- **气泡对话框** — 支持 Markdown 渲染，实时显示 AI 回复
- **系统托盘** — 右键菜单可唤出设置、清空对话、退出
- **设置面板** — 修改 API Key、模型、宠物名字、尺寸、性格等
- **数据持久化** — SQLite 保存对话历史和窗口位置

## 技术栈

- Python 3.12
- PySide6（GUI）
- httpx（API 请求）
- SQLite（数据持久化）

## 运行

```bash
pip install -r requirements.txt
python main.py
```

## 配置

复制 `.env.example` 为 `.env`，填入你的 API Key：

```bash
cp .env.example .env
```

编辑 `.env`：

```
KIMI_API_KEY=your_api_key_here
KIMI_MODEL=deepseek-chat
KIMI_BASE_URL=https://api.deepseek.com
```

> 兼容任何 OpenAI 格式的 API，如 DeepSeek、Moonshot、OpenRouter 等。

也可以在运行后通过托盘菜单 → 设置面板中直接配置。

## 项目结构

```
.
├── assets/              # 猫咪素材（PNG 帧动画）
├── core/                # AI 客户端、素材管理、聊天工作线程
├── database/            # SQLite 数据库管理
├── ui/                  # 窗口、动画引擎、气泡对话框、托盘、设置面板
├── utils/               # 日志工具
├── tools/               # 素材生成脚本
├── main.py              # 入口
└── config.py            # 配置读取
```

## 许可证

MIT