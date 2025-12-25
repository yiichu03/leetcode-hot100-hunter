LeetCode-Hot100-Hunter
=====================

一个轻量的 LeetCode 刷题仪表盘，主打随机抽题、进度跟踪、解法归档、笔记沉淀和轻量 AI 思路助手。

功能亮点
--------
- 随机抽题：可重复抽到已完成题（权重更低）
- 题目展示：标题直达 LeetCode、难度、标签、算法锦囊
- 解法归档：默认保存为带时间戳文件，不覆盖历史；可标记 best
- 复习模式：侧边栏可选择已完成题目，重新做题不预填
- 历史笔记：以文件形式追加记录，页面右侧可只读查看
- 相关题目：基于相同标签快速跳转
- Git 集成：提交时自动 add/commit，Push 按钮单独触发
- AI 思路助手：支持 OpenAI 兼容接口（DeepSeek 默认）

快速运行
--------
1. 安装依赖（如有 requirements.txt 可自行补充）：
   pip install streamlit
2. 启动：
   streamlit run app.py

Windows 快捷启动（可选）
-----------------------
创建 `start_hunter.bat`：
```
@echo off
cd /d D:\AA_NUS\projects\LeetCode-Hot100-Hunter
call conda activate pytorch
streamlit run app.py
pause
```
双击即可启动。

页面使用说明
------------
- 左侧：进度条、复习已完成题目、Push 按钮、清零功能
- 中间：题目内容、算法锦囊、代码/笔记输入、提交
- 右侧：相关题目、历史笔记（只读）、AI 思路助手

提交逻辑
--------
- 解法保存：`solutions/{id}_{slug}_{timestamp}.py`
- best 解法：`solutions/best/{id}_{slug}.py`（同题覆盖）
- 笔记保存：`notes/{id}_{slug}.md`（追加，首行时间戳）
- 提交时自动 `git add/commit`，Push 需手动点击

AI 配置（可选）
--------------
在项目根目录创建 `ai_config.txt`（已加入 .gitignore）：
```
AI_API_KEY=你的密钥
AI_BASE_URL=https://api.deepseek.com/v1
AI_MODEL=deepseek-chat
```
也可改用环境变量 `AI_API_KEY/AI_BASE_URL/AI_MODEL`。

目录结构（简版）
--------------
- `app.py`：Streamlit 主界面
- `data/problems.json`：题库数据
- `solutions/`：解法输出（含 `best/`）
- `notes/`：笔记输出
- `utils/`：数据、Git、AI 相关工具
