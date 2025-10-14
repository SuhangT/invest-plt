# 股债仓位决策系统

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![React](https://img.shields.io/badge/react-18.2-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

**智能投资组合管理系统 - 基于股债性价比和估值分位数的资产配置决策工具**

[快速开始](#快速开始) • [功能特性](#核心功能) • [使用文档](USER_GUIDE.md) • [API文档](API_DOCUMENTATION.md) • [部署指南](DEPLOYMENT.md)

</div>

---

## 📋 目录

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [技术架构](#技术架构)
- [快速开始](#快速开始)
- [项目结构](#项目结构)
- [使用指南](#使用指南)
- [开发文档](#开发文档)
- [常见问题](#常见问题)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## 🎯 项目简介

股债仓位决策系统是一个基于**量化指标**的智能投资组合管理工具，帮助投资者：

- 📊 **科学决策**：基于股债性价比和估值分位数进行资产配置
- 🎯 **精准配置**：自动计算各指数基金的目标仓位
- 📈 **动态调整**：实时监控估值变化，提供加仓/减仓建议
- 🔄 **自动更新**：每交易日自动抓取最新数据并重新计算

### 核心理念

1. **股债性价比**：通过比较股票（中证800市盈率倒数）与债券（10年国债收益率）的相对吸引力，决定整体股票配置比例
2. **估值分位数**：将指数估值在历史数据中的位置量化，低估时增加配置，高估时减少配置
3. **ROE加权**：考虑企业盈利能力，ROE越高权重越大
4. **人为调整**：支持根据个人判断调整权重，灵活性与系统性结合

## ✨ 核心功能

### 1. 股债仓位决策系统

<table>
<tr>
<td width="50%">

**计算逻辑**
```
股债性价比 = 1/中证800PE - 10年国债收益率
分位数 = 当前值在近10年的排名百分比
股票配置 = 分位数%
```

</td>
<td width="50%">

**应用场景**
- 分位数 < 20%：大幅增配股票
- 分位数 20-40%：适度增配股票
- 分位数 40-60%：均衡配置
- 分位数 60-80%：适度减配股票
- 分位数 > 80%：大幅减配股票

</td>
</tr>
</table>

### 2. 指数基金筛选与权重分配

#### 估值分位区间评分

| 分位区间 | 初始分数 | 估值状态 | 操作建议 |
|---------|---------|---------|---------|
| 0%-10% | 40 | 极度低估 | 强烈买入 |
| 10%-20% | 35 | 严重低估 | 积极买入 |
| 20%-35% | 30 | 低估 | 可以买入 |
| 35%-50% | 25 | 合理偏低 | 适度买入 |
| 50%-65% | 20 | 合理偏高 | 谨慎买入 |
| 65%-80% | 15 | 高估 | 减少配置 |
| 80%-90% | 10 | 严重高估 | 考虑减仓 |
| 90%-100% | 5 | 极度高估 | 建议减仓 |

#### 综合权重计算

```
ROE权重 = 1.0 + (ROE - 10) × 0.1
综合权重 = ROE权重 × 人为权重
综合分数 = 初始分数 × 综合权重
目标仓位 = (综合分数 / 总分) × 股票配置比例
```

### 3. 动态操作提示

- ✅ **加仓信号**：估值向下突破区间下限且达到上一区间均值
- ⚠️ **减仓信号**：估值向上突破区间上限
- 📊 **可视化**：浅绿色背景（加仓）/ 浅红色背景（减仓）

## 🏗️ 技术架构

### 后端技术栈

| 技术 | 版本 | 用途 |
|-----|------|-----|
| Python | 3.8+ | 核心语言 |
| Flask | 3.0.0 | Web框架 |
| SQLAlchemy | 3.1.1 | ORM |
| SQLite | - | 数据库 |
| akshare | 1.13.0 | 数据源 |
| APScheduler | 3.10.4 | 定时任务 |
| pandas | 2.1.4 | 数据处理 |
| numpy | 1.26.2 | 数值计算 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|-----|------|-----|
| React | 18.2.0 | UI框架 |
| TailwindCSS | 3.3.6 | 样式框架 |
| Recharts | 2.10.3 | 图表库 |
| Lucide React | 0.294.0 | 图标库 |
| Axios | 1.6.2 | HTTP客户端 |

## 🚀 快速开始

### 前置要求

- Python 3.8 或更高版本
- Node.js 16 或更高版本
- pip 和 npm

### Windows 一键启动

```bash
# 双击运行启动脚本
start.bat
```

脚本会自动：
1. 创建Python虚拟环境
2. 安装后端依赖
3. 初始化数据库
4. 安装前端依赖
5. 启动后端服务（端口5000）
6. 启动前端服务（端口3000）

### 手动启动

#### 步骤1：安装后端依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 步骤2：初始化数据库

```bash
python backend/init_db.py
```

#### 步骤3：启动后端

```bash
python backend/app.py
```

后端服务将在 http://localhost:5000 启动

#### 步骤4：安装前端依赖

```bash
cd frontend
npm install
```

#### 步骤5：启动前端

```bash
npm start
```

前端服务将在 http://localhost:3000 启动，浏览器会自动打开

### 首次使用

1. 访问 http://localhost:3000
2. 点击"开始初始化"按钮
3. 等待数据抓取完成（约5-10分钟）
4. 点击"管理自选"添加感兴趣的指数
5. 查看仪表盘和操作建议

## 📁 项目结构

```
invest-plt/
├── backend/                    # 后端目录
│   ├── app.py                 # Flask主应用和API路由
│   ├── models.py              # SQLAlchemy数据库模型
│   ├── data_fetcher.py        # akshare数据抓取模块
│   ├── calculator.py          # 核心计算逻辑（分位数、ROE权重等）
│   ├── scheduler.py           # APScheduler定时任务
│   ├── init_db.py             # 数据库初始化脚本
│   └── invest.db              # SQLite数据库文件（运行后生成）
│
├── frontend/                   # 前端目录
│   ├── src/
│   │   ├── components/        # React组件
│   │   │   ├── Dashboard.js   # 仪表盘组件
│   │   │   ├── IndexTable.js  # 指数表格组件
│   │   │   ├── IndexSelector.js # 指数选择器
│   │   │   ├── Header.js      # 头部导航
│   │   │   └── InitialSetup.js # 初始化页面
│   │   ├── App.js             # 主应用组件
│   │   ├── index.js           # React入口文件
│   │   └── index.css          # 全局样式
│   ├── public/
│   │   └── index.html         # HTML模板
│   ├── package.json           # 前端依赖配置
│   └── tailwind.config.js     # TailwindCSS配置
│
├── requirements.txt            # Python依赖
├── start.bat                   # Windows启动脚本
├── .gitignore                  # Git忽略文件
├── .env.example                # 环境变量示例
│
├── README.md                   # 项目说明（本文件）
├── USER_GUIDE.md              # 用户使用指南
├── API_DOCUMENTATION.md       # API接口文档
├── DEPLOYMENT.md              # 部署和运维指南
├── TESTING_CHECKLIST.md       # 测试检查清单
├── CHANGELOG.md               # 版本更新日志
└── LICENSE                     # MIT许可证
```

## 📖 使用指南

### 基本操作流程

```mermaid
graph LR
    A[启动系统] --> B[初始化数据]
    B --> C[添加自选指数]
    C --> D[查看配置建议]
    D --> E[调整权重]
    E --> F[执行交易]
    F --> G[定期复盘]
    G --> D
```

### 详细文档

- 📘 **[用户使用指南](USER_GUIDE.md)** - 完整的使用教程和最佳实践
- 📗 **[API文档](API_DOCUMENTATION.md)** - 后端API接口详细说明
- 📙 **[部署指南](DEPLOYMENT.md)** - 生产环境部署和运维
- 📕 **[测试清单](TESTING_CHECKLIST.md)** - 完整的测试检查项

## 🔧 开发文档

### 数据流程

```
1. 数据抓取 (data_fetcher.py)
   ↓
2. 数据存储 (models.py + SQLite)
   ↓
3. 指标计算 (calculator.py)
   ↓
4. API提供 (app.py)
   ↓
5. 前端展示 (React Components)
```

### 核心算法

#### 股债性价比计算
```python
ratio = (1 / csi800_pe) - (bond_yield_10y / 100)
percentile = rank(ratio, historical_ratios) * 100
stock_allocation = percentile
```

#### 估值分位数计算
```python
values = historical_pe_values[-10_years:]
current_pe = latest_pe
percentile = (sum(values <= current_pe) / len(values)) * 100
```

#### ROE权重计算
```python
roe_weight = 1.0 + (roe - 10) * 0.1
roe_weight = max(0, roe_weight)  # 不能为负
```

### 扩展开发

#### 添加新的数据源

1. 在 `data_fetcher.py` 中添加新的抓取方法
2. 在 `models.py` 中定义对应的数据模型
3. 在 `app.py` 中添加API端点
4. 在前端组件中展示数据

#### 自定义评分规则

修改 `calculator.py` 中的 `PERCENTILE_RANGES` 配置：

```python
PERCENTILE_RANGES = [
    (0, 10, 50),   # 自定义分数
    (10, 20, 40),
    # ...
]
```

## 🔄 数据抓取重试机制

系统已实现**智能重试机制**，应对公开API的不稳定性：

### 核心特性

- ✅ **自动重试**: API调用失败时自动重试（默认10次）
- ✅ **随机延迟**: 每次重试间隔3-10秒随机延迟，避免频率限制
- ✅ **详细日志**: 记录每次重试的详细信息
- ✅ **全面覆盖**: 所有数据抓取接口都支持重试

### 配置说明

```python
# 默认配置（推荐）
fetcher = DataFetcher()  # 10次重试，3-10秒延迟

# 自定义配置
fetcher = DataFetcher(max_retries=15, min_delay=5, max_delay=15)
```

### 详细文档

- 📘 [重试机制使用指南](DATA_FETCHER_GUIDE.md)
- 📗 [更新总结](RETRY_MECHANISM_SUMMARY.md)

## ❓ 常见问题

### Q: 首次初始化失败怎么办？

**A**: 系统已有自动重试机制，如果仍然失败：
1. 检查网络连接是否正常
2. 查看后端日志 `logs/app.log` 确认具体错误
3. 尝试在非高峰时段（如晚上）重新初始化
4. 手动执行 `python backend/init_db.py`

### Q: 数据更新不及时？

**A**: 
- 系统会自动重试失败的请求（最多10次）
- 手动点击"刷新数据"按钮
- 查看系统日志确认更新时间和重试情况

### Q: 如何备份数据？

**A**: 
复制 `backend/invest.db` 文件即可。建议定期备份，保留多个历史版本。

### Q: 支持哪些浏览器？

**A**: 
支持所有现代浏览器：Chrome、Firefox、Edge、Safari（最新版本）

### Q: 可以在服务器上部署吗？

**A**: 
可以。参考 [DEPLOYMENT.md](DEPLOYMENT.md) 了解详细的部署方案。

## 🤝 贡献指南

欢迎贡献代码、报告问题或提出建议！

### 如何贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- Python: 遵循 PEP 8
- JavaScript: 遵循 Airbnb Style Guide
- 提交信息: 使用清晰的描述性信息

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## ⚠️ 免责声明

**重要提示**：

1. 本系统仅供**学习和参考**使用，不构成任何投资建议
2. 投资有风险，决策需谨慎，请根据自身情况做出独立判断
3. 历史数据不代表未来表现，任何投资模型都有局限性
4. 使用本系统产生的任何投资损失，开发者不承担责任
5. 建议在使用前咨询专业的财务顾问

## 📞 联系方式

- 问题反馈：通过 GitHub Issues
- 功能建议：通过 GitHub Discussions
- 技术交流：欢迎 Star 和 Fork

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ for investors

</div>
