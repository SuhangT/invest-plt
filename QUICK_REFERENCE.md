# 快速参考卡片

## 🚀 启动系统

```bash
# Windows 一键启动
start.bat

# 手动启动后端
python backend/app.py

# 手动启动前端
cd frontend && npm start
```

## 🔄 手动更新数据

### 方法1: 前端界面（推荐）
点击右上角 **"刷新数据"** 按钮

### 方法2: API接口
```bash
curl -X POST http://localhost:5000/api/data/refresh \
  -H "Content-Type: application/json" \
  -d '{"type":"all"}'
```

### 方法3: Python脚本
```python
from backend.app import app
from backend.data_fetcher import DataFetcher
from backend.calculator import Calculator

with app.app_context():
    fetcher = DataFetcher()
    calculator = Calculator()
    
    # 更新数据
    fetcher.fetch_bond_yield()
    calculator.run_daily_calculation()
```

## ⚙️ 重试机制配置

### 默认配置
```python
DataFetcher()  # 10次重试，3-10秒延迟
```

### 自定义配置
```python
# 首次初始化（最大成功率）
DataFetcher(max_retries=15, min_delay=5, max_delay=15)

# 快速测试（快速失败）
DataFetcher(max_retries=3, min_delay=1, max_delay=3)

# 网络不稳定（极致稳定）
DataFetcher(max_retries=20, min_delay=10, max_delay=30)
```

## 📊 查看日志

```bash
# 查看所有日志
cat logs/app.log

# 查看重试日志
grep "重试" logs/app.log

# 统计失败次数
grep "已重试.*次仍然失败" logs/app.log | wc -l

# 实时监控
tail -f logs/app.log
```

## 🧪 测试重试机制

```bash
cd backend
python test_retry.py
```

## 📁 重要文件位置

| 文件 | 路径 | 说明 |
|-----|------|------|
| 数据库 | `backend/invest.db` | SQLite数据库文件 |
| 日志 | `logs/app.log` | 应用日志 |
| 配置 | `.env` | 环境变量配置 |
| 后端入口 | `backend/app.py` | Flask应用 |
| 前端入口 | `frontend/src/App.js` | React应用 |

## 🔧 常用API端点

| 端点 | 方法 | 说明 |
|-----|------|------|
| `/api/health` | GET | 健康检查 |
| `/api/system/status` | GET | 系统状态 |
| `/api/indices` | GET | 获取指数列表 |
| `/api/dashboard` | GET | 仪表盘数据 |
| `/api/data/refresh` | POST | 刷新数据 |
| `/api/data/init` | POST | 初始化数据 |

## 🐛 故障排查

### 问题: 数据抓取失败

**检查步骤**:
1. 查看日志: `grep "失败" logs/app.log`
2. 检查网络: `ping www.baidu.com`
3. 测试API: `python backend/test_retry.py`
4. 增加重试: 修改 `DataFetcher` 参数

### 问题: 前端无法访问

**检查步骤**:
1. 后端是否启动: `curl http://localhost:5000/api/health`
2. 端口是否占用: `netstat -ano | findstr 3000`
3. 查看浏览器控制台错误
4. 清除浏览器缓存

### 问题: 数据库锁定

**解决方案**:
```bash
# 重启后端服务
# 或使用PostgreSQL替代SQLite
```

## 📚 文档索引

| 文档 | 说明 |
|-----|------|
| [README.md](README.md) | 项目概述 |
| [USER_GUIDE.md](USER_GUIDE.md) | 用户使用指南 |
| [API_DOCUMENTATION.md](API_DOCUMENTATION.md) | API文档 |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 部署指南 |
| [DATA_FETCHER_GUIDE.md](DATA_FETCHER_GUIDE.md) | 重试机制指南 |
| [TESTING_CHECKLIST.md](TESTING_CHECKLIST.md) | 测试清单 |

## 💡 最佳实践

### 数据抓取
- ✅ 在非交易时间（晚上）进行大量抓取
- ✅ 使用默认重试配置（10次，3-10秒）
- ✅ 监控日志，关注失败率
- ❌ 避免频繁手动刷新

### 系统使用
- ✅ 每周或每月查看一次即可
- ✅ 定期备份数据库文件
- ✅ 根据自己判断调整权重
- ❌ 不要过度交易

### 性能优化
- ✅ 只添加需要的指数到自选
- ✅ 定期清理旧日志
- ✅ 使用SSD存储数据库
- ❌ 避免同时运行多个实例

## 🔐 安全建议

- 🔒 不要暴露到公网（仅本地使用）
- 🔒 定期备份数据库
- 🔒 使用强密码（如需添加认证）
- 🔒 保持依赖包更新

## 📞 获取帮助

1. 查看文档（优先）
2. 查看日志文件
3. 运行测试脚本
4. 提交 GitHub Issue

---

**提示**: 将此文件保存到书签，便于快速查阅！
