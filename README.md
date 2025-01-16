# 智能助手

一个功能强大的智能助手，支持知识库、多角色切换、对话导出和语音交互等功能。

## 功能特点

1. **知识库支持**
   - 使用 ChromaDB 作为向量数据库
   - 支持文档上传和检索
   - 智能融合相关知识到对话中

2. **多角色切换**
   - 预设多个专业角色
   - 支持自定义新角色
   - 实时切换对话风格

3. **对话导出**
   - 支持 JSON 格式
   - 支持 Markdown 格式
   - 支持 Word 文档格式
   - 支持 HTML 格式

4. **语音交互**
   - 支持语音输入（需要麦克风）
   - 支持语音输出
   - 支持中文语音识别

5. **Web界面**
   - 现代化的响应式设计
   - 实时对话更新
   - 支持文件上传
   - 集成所有核心功能

## 系统要求

- Python 3.9 或更高版本
- macOS/Linux（Windows 待测试）
- 推荐 4GB 以上内存
- 可选：麦克风（用于语音输入）

## 快速开始

1. 克隆仓库：
   ```bash
   git clone [repository-url]
   cd 智能体
   ```

2. 设置环境变量：
   ```bash
   cp .env.example .env
   # 编辑 .env 文件，设置您的智谱AI API密钥
   ```

3. 运行启动脚本：
   ```bash
   # 添加执行权限
   chmod +x start.sh
   
   # 命令行模式
   ./start.sh
   
   # Web界面模式
   ./start.sh --web
   
   # 语音交互模式
   ./start.sh --voice
   ```

## 使用说明

### 命令行模式

在命令行模式下，您可以使用以下命令：

1. `quit`: 退出程序
2. `clear`: 清空对话历史
3. `export <format>`: 导出对话（支持 json/markdown/docx）
4. `role <role_id>`: 切换角色
5. `roles`: 查看所有可用角色

### Web界面

访问 `http://localhost:5000` 即可使用Web界面，支持：

- 发送消息
- 上传知识文档
- 切换角色
- 导出对话
- 语音输入（如果可用）

### 语音模式

语音模式支持：

- 语音输入（需要麦克风）
- 语音输出（使用系统TTS）
- 混合模式（键盘输入 + 语音输出）

## 文件结构

```
智能体/
├── main.py           # 主程序
├── agent.py          # 智能体核心
├── knowledge_base.py # 知识库管理
├── roles.py         # 角色管理
├── export.py        # 对话导出
├── voice.py         # 语音接口
├── web_server.py    # Web服务器
├── config.py        # 配置文件
├── requirements.txt # 依赖列表
├── .env            # 环境变量
├── templates/      # Web模板
│   └── index.html  # 主页面
├── exports/        # 导出文件目录
└── vector_store/   # 知识库存储
```

## 配置说明

1. 环境变量（.env）：
   ```
   ZHIPUAI_API_KEY=your_api_key_here
   ```

2. 配置文件（config.py）：
   - 模型参数
   - 系统提示词
   - 其他全局设置

## 常见问题

1. **没有检测到麦克风**
   - 程序会自动切换到混合模式（键盘输入 + 语音输出）
   - 检查系统音频设置和权限

2. **API 调用失败**
   - 确认 API 密钥设置正确
   - 检查网络连接
   - 查看错误信息

3. **Web界面无法访问**
   - 确认端口 5000 未被占用
   - 检查防火墙设置
   - 尝试使用不同的浏览器

## 更新日志

### v1.0.0 (2025-01-15)
- 初始版本发布
- 实现核心功能
- 添加Web界面
- 支持语音交互

## 许可证

MIT License

## 贡献指南

欢迎提交 Issue 和 Pull Request！
