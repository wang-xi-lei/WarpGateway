# WarpGateway

基于 mitmproxy 的 Warp.dev 请求拦截代理网关。

## 功能特性

- 🔍 拦截 Warp.dev 相关请求
- ✅ 可配置的请求放行/拦截规则
- 📝 请求日志记录（JSON Lines 格式）
- 📊 实时请求统计分析
- 🔗 拦截器链架构，易于扩展
- 🎯 支持多种规则匹配方式（精确/包含/正则/通配符）
- ⚙️ 灵活的配置管理
- 🖥️ GUI 桌面应用
- 🔐 自动证书管理和安装
- 🚀 一键启动（证书检查、代理启动、Warp 启动）
- 💾 配置备份与恢复

## 安装

### 依赖安装

**macOS/Linux（推荐使用虚拟环境）：**

由于 macOS 和部分 Linux 发行版的 Python 环境受系统管理，建议使用虚拟环境：

```bash
# 方式 1: 使用安装脚本（推荐）
./安装依赖.sh

# 方式 2: 手动创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -e .
```

**Windows：**

```bash
# 使用虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate
pip install -e .

# 或直接安装（如果系统允许）
pip install -e .
```

**安装开发依赖：**

```bash
# 激活虚拟环境后
pip install -e ".[dev]"
```

### 证书安装

mitmproxy 需要安装 CA 证书才能拦截 HTTPS 请求。

**自动安装（推荐）：**

- **Windows**: 双击运行 `scripts\安装证书.bat`
- **macOS/Linux**: 命令行运行：
```bash
python3 -m src.utils.cert_manager
```

或在 GUI 中直接点击"一键启动"，会自动检查并安装证书。

**手动安装：**

- **Windows**:
  1. 证书位置：`%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.cer`
  2. 双击证书文件
  3. 选择"安装证书"
  4. 选择"将所有的证书放入下列存储"
  5. 浏览并选择"受信任的根证书颁发机构"
  6. 点击"完成"

- **macOS**:
  1. 证书位置：`~/.mitmproxy/mitmproxy-ca-cert.pem`
  2. 双击证书文件，或运行：
     ```bash
     open ~/.mitmproxy/mitmproxy-ca-cert.pem
     ```
  3. 在"钥匙串访问"中，将证书添加到"系统"钥匙串
  4. 双击证书，展开"信任"，将"使用此证书时"设置为"始终信任"

## 使用方法

### 启动 GUI

**macOS/Linux：**

```bash
# 方式 1: 使用启动脚本（自动处理虚拟环境）
./启动WarpGateway.sh

# 方式 2: 手动启动（需要先激活虚拟环境）
source .venv/bin/activate
python run_gui.py
```

**Windows：**

```bash
# 方式 1: 双击启动脚本
启动WarpGateway.bat

# 方式 2: 命令行启动
.venv\Scripts\activate
python run_gui.py
```

### 操作步骤

1. 打开 GUI 窗口
2. 点击“一键启动”按钮
3. 程序会自动：
   - 检查并安装 mitmproxy 证书
   - 启动代理服务
   - 启动 Warp 应用
4. 使用 Warp.dev

### GUI 功能说明

- **一键启动/停止服务**：自动完成证书检查、代理启动、Warp 启动
- **Warp 路径选择**：自定义 Warp 应用路径
- **配置备份/恢复**：备份和恢复 `config.yaml` 配置文件
- **实时日志**：查看代理运行日志和状态信息

### 配置 Warp 客户端

将 Warp 客户端代理设置为：
- 主机: `localhost`
- 端口: `8080`（默认）

## 配置文件

在 `config.yaml` 中配置拦截规则：

```yaml
proxy:
  host: "0.0.0.0"      # 监听地址
  port: 8080           # 监听端口
  ssl_insecure: false  # SSL 验证

rules:
  # 拦截规则（返回 403）
  block:
    - "o540343.ingest.sentry.io"        # Warp Sentry 错误上报
    - "dataplane.rudderstack.com"       # Warp 数据分析
    - "app.warp.dev/analytics/block"    # Warp 应用内分析
    - "app.warp.dev/proxy/sentry"       # Warp 代理 Sentry
  
  # 放行规则
  allow: []
  
  # 仅记录日志不拦截
  log_only: []

# 流式响应配置
streaming:
  paths:
    - "/ai/multi-agent"  # Warp AI 多智能体对话

logging:
  level: "INFO"                  # 日志级别
  file: "warp_gateway.log"       # 日志文件
  console: true                  # 控制台输出
```

## 项目结构

```
WarpGateway/
├── src/
│   ├── __init__.py
│   ├── __main__.py        # 模块入口
│   ├── core/              # 核心功能
│   │   ├── __init__.py
│   │   ├── config.py      # 配置管理
│   │   ├── interceptor.py # 拦截器基类和链
│   │   └── proxy.py       # 代理服务器
│   ├── handlers/          # 请求处理器
│   │   ├── __init__.py
│   │   ├── warp.py        # Warp 专用处理器
│   │   ├── logger.py      # 日志处理器
│   │   └── stats.py       # 统计处理器
│   ├── gui/               # GUI 界面
│   │   ├── __init__.py
│   │   ├── main.py        # GUI 入口
│   │   ├── window.py      # 主窗口
│   │   └── tray.py        # 系统托盘（保留）
│   └── utils/             # 工具模块
│       ├── __init__.py
│       ├── rules.py       # 规则匹配工具
│       ├── cert_manager.py # 证书管理和安装
│       └── warp_manager.py # Warp 应用管理
├── scripts/               # 脚本目录
│   └── 安装证书.bat   # Windows 证书安装脚本
├── plugins/               # 插件目录
│   └── README.md      # 插件开发说明
├── logs/                  # 日志目录
├── run_gui.py             # GUI 启动器
├── 启动WarpGateway.bat   # Windows 快捷启动
├── config.yaml            # 配置文件
├── pyproject.toml         # 项目配置
├── README.md              # 项目说明
├── IMPLEMENTATION.md      # 技术实现文档
└── LICENSE                # 许可证
```

## 开发

### 自定义处理器

继承 `BaseInterceptor` 类即可创建自定义处理器：

```python
from src.core.interceptor import BaseInterceptor
from mitmproxy import http

class MyHandler(BaseInterceptor):
    def __init__(self):
        super().__init__("MyHandler")
    
    def request(self, flow: http.HTTPFlow):
        # 处理请求
        return None
    
    def response(self, flow: http.HTTPFlow):
        # 处理响应
        return None
```

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 代码格式化

```bash
black .
ruff check .
```

## API 分析功能

WarpGateway 提供了强大的 API 分析功能，可以自动分析 Warp.dev 的 API 请求，识别认证方式、Token 位置等信息。

### 使用方法

1. **启动代理并记录日志：**
   ```bash
   # 启动代理（会自动记录日志到 logs/ 目录）
   python run_gui.py
   ```

2. **分析日志文件：**
   ```bash
   # 生成 Markdown 报告（默认）
   python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl
   
   # 生成 JSON 报告
   python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl --format json
   
   # 控制台输出
   python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl --format console
   
   # 指定输出文件
   python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl -o analysis.md
   ```

### 分析报告内容

分析报告包含以下信息：

- **请求摘要**：总请求数、方法分布、域名分布
- **API 端点列表**：所有发现的 API 端点，包括路径、方法、请求次数、状态码
- **认证 Header 分析**：自动识别 Authorization、X-API-Key 等认证 Header，识别认证格式
- **请求体分析**：提取 JSON Schema，识别常见字段（如 token、user_id 等）
- **AI 服务请求识别**：自动识别 AI 相关的请求（如 `/ai/`, `/multi-agent` 等）
- **Token 位置识别**：识别 Token 在 Header 和请求体中的位置

### 配置选项

在 `config.yaml` 中可以配置分析选项：

```yaml
analysis:
  enabled: true  # 是否启用详细分析日志
  domains:       # 只记录这些域名的请求
    - "api.warp.dev"
    - "app.warp.dev"
  max_body_size: 1048576  # 请求体最大记录大小（1MB）
  mask_sensitive: true     # 是否脱敏敏感信息
  sensitive_headers:       # 需要脱敏的 Header
    - "Authorization"
    - "X-API-Key"
```

## 命令行工具

### 证书管理

```bash
# 安装证书
python -m src.utils.cert_manager

# 卸载证书（Windows）
python -m src.utils.cert_manager uninstall
```

### Warp 应用管理

```bash
# 启动 Warp
python -m src.utils.warp_manager launch

# 关闭 Warp
python -m src.utils.warp_manager kill

# 重启 Warp
python -m src.utils.warp_manager restart

# 检查状态
python -m src.utils.warp_manager status
```

### 启动代理（命令行模式）

```bash
python -m src
```

### API 日志分析

```bash
# 分析日志文件，生成 Markdown 报告
python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl

# 生成 JSON 格式报告
python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl --format json

# 控制台输出
python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl --format console

# 指定输出文件
python -m src.utils.analyze_logs logs/requests_20231123_120000.jsonl -o analysis.md
```

## 常见问题

### 证书安装问题

**Q: 点击一键启动后提示证书安装失败？**

A: 可能需要管理员权限。请右键点击 `scripts\\安装证书.bat` 选择“以管理员身份运行”。

**Q: 证书已安装但仍无法拦截 HTTPS？**

A: 请确保：
1. 证书已安装到“受信任的根证书颁发机构”
2. 重启浏览器或 Warp 应用
3. 检查 Warp 是否配置了代理

### 代理连接问题

**Q: Warp 无法连接代理？**

A: 请检查：
1. 代理服务是否正常运行（GUI 窗口显示“运行中”）
2. Warp 客户端代理设置为 `127.0.0.1:8080`
3. 防火墙是否允许该端口

**Q: 如何查看拦截日志？**

A: 日志文件位于 `logs/` 目录，或在 GUI 窗口底部查看实时日志。

### Warp 应用问题

**Q: 找不到 Warp 应用？**

A: 点击 GUI 中的“选择...”按钮手动指定 Warp 可执行文件路径，或设置环境变量 `WARP_PATH`。

## 技术架构

### 核心组件

- **mitmproxy**: HTTPS 代理引擎
- **PySide6**: Qt 跨平台 GUI 框架
- **PyYAML**: 配置文件解析

### 拦截器链设计

项目采用责任链模式，每个拦截器处理特定类型的请求：

1. **WarpInterceptor**: 匹配 Warp.dev 域名的请求
2. **LoggerInterceptor**: 记录请求/响应信息
3. **StatsInterceptor**: 统计流量和请求数

每个拦截器可以：
- 修改请求/响应
- 阻止请求（返回自定义响应）
- 记录日志
- 传递给下一个拦截器

详细实现请查看 [IMPLEMENTATION.md](IMPLEMENTATION.md)。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 项目
2. 创建功能分支
3. 提交代码并添加测试
4. 确保代码格式符合规范（`black` + `ruff`）
5. 提交 Pull Request

### 插件开发

可以在 `plugins/` 目录创建自定义拦截器，查看 [plugins/README.md](plugins/README.md) 了解详情。

## 许可证

MIT License
