# 桌宠开发进度

## 已完成

- [x] Day 1 Phase 0: 猫咪 PNG 素材生成（Pillow 绘制，idle/click/talk + tray_icon）
- [x] Day 2 Phase 1: 基础框架（透明窗口、拖拽、系统托盘）
- [x] Day 2.5: 修复透明边框（QPainter alpha 遮罩）和尺寸（64x64）
- [x] Day 3 Phase 2: 动画系统（状态机、帧动画、AssetManager 独立素材模块）
- [x] Day 4 Phase 3: AI 接入（Kimi API 封装、流式输出）
- [x] Day 5 Phase 4: 气泡对话框（输入、显示、Markdown）

## 待完成

- [ ] Day 6 Phase 5: 数据持久化（SQLite、配置读写）
- [ ] Day 7 Phase 6: 设置面板（API Key、宠物性格、尺寸等）
- [ ] Day 8 Phase 7: 打包分发（PyInstaller .exe）

## 关键技术信息

- API: `https://api.kimi.com/coding`
- 模型: `kimi-for-coding`
- 用户持有 API Key，需配置在 `.env` 中
- 素材模块 `core/asset_manager.py` 已独立，后期替换素材不影响其他代码

## Git 提交历史

```
0f7e6ee fix: 使用 QPainter 从 alpha 通道生成遮罩，彻底去除窗口白边
e7116ef init: 桌宠基础框架 + 猫咪素材生成 + 透明窗口 + 系统托盘
```
