# 部署指南

## 开发环境部署

### 前置要求

- Python 3.8+
- Node.js 16+
- pip
- npm

### Windows 快速启动

1. **双击运行启动脚本**
   ```
   start.bat
   ```

2. **等待服务启动**
   - 后端服务: http://localhost:5000
   - 前端服务: http://localhost:3000

3. **首次使用**
   - 访问 http://localhost:3000
   - 点击"开始初始化"按钮
   - 等待数据初始化完成（约5-10分钟）

### 手动启动

#### 后端

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (Windows)
venv\Scripts\activate

# 激活虚拟环境 (Linux/Mac)
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python backend/init_db.py

# 启动后端
python backend/app.py
```

#### 前端

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

## 生产环境部署

### 使用 Gunicorn + Nginx

#### 1. 安装 Gunicorn

```bash
pip install gunicorn
```

#### 2. 启动后端

```bash
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 3. 构建前端

```bash
cd frontend
npm run build
```

#### 4. 配置 Nginx

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/invest-plt/frontend/build;
        try_files $uri /index.html;
    }

    # API代理
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 使用 Docker

#### 1. 创建 Dockerfile (后端)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/

EXPOSE 5000

CMD ["python", "backend/app.py"]
```

#### 2. 创建 Dockerfile (前端)

```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
```

#### 3. Docker Compose

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
    environment:
      - FLASK_ENV=production

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
```

## 定时任务配置

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器: 每天 15:30
4. 操作: 启动程序
   - 程序: `python`
   - 参数: `backend/app.py`
   - 起始于: `E:\Project\invest-plt`

### Linux Crontab

```bash
# 编辑 crontab
crontab -e

# 添加定时任务（每天15:30执行）
30 15 * * * cd /path/to/invest-plt && /path/to/venv/bin/python backend/scheduler.py
```

### 使用 Supervisor (推荐)

```ini
[program:invest-plt]
command=/path/to/venv/bin/python backend/app.py
directory=/path/to/invest-plt
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/invest-plt.log
```

## 数据备份

### 自动备份脚本

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DB_FILE="/path/to/invest-plt/backend/invest.db"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份
cp $DB_FILE $BACKUP_DIR/invest_$DATE.db

# 保留最近30天的备份
find $BACKUP_DIR -name "invest_*.db" -mtime +30 -delete

echo "Backup completed: invest_$DATE.db"
```

### Windows 备份脚本

```batch
@echo off
set BACKUP_DIR=D:\backups
set DB_FILE=E:\Project\invest-plt\backend\invest.db
set DATE=%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%

copy "%DB_FILE%" "%BACKUP_DIR%\invest_%DATE%.db"

echo Backup completed: invest_%DATE%.db
```

## 性能优化

### 1. 数据库优化

```python
# 在 models.py 中添加索引
class IndexHistory(db.Model):
    # ...
    __table_args__ = (
        db.Index('idx_index_date', 'index_id', 'date'),
    )
```

### 2. 缓存配置

```python
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})

@app.route('/api/dashboard')
@cache.cached(timeout=60)
def get_dashboard():
    # ...
```

### 3. 数据库连接池

```python
app.config['SQLALCHEMY_POOL_SIZE'] = 10
app.config['SQLALCHEMY_POOL_RECYCLE'] = 3600
```

## 监控与日志

### 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10000000,
    backupCount=10
)
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
```

### 健康检查

```bash
# 检查后端服务
curl http://localhost:5000/api/health

# 检查前端服务
curl http://localhost:3000
```

## 故障排查

### 常见问题

1. **数据库锁定**
   - 症状: `database is locked`
   - 解决: 重启服务或使用 PostgreSQL

2. **akshare 接口限流**
   - 症状: 频繁请求失败
   - 解决: 增加请求间隔时间

3. **内存不足**
   - 症状: 进程被杀死
   - 解决: 增加服务器内存或优化查询

4. **端口占用**
   - 症状: `Address already in use`
   - 解决: 更改端口或关闭占用进程

### 日志查看

```bash
# 查看后端日志
tail -f logs/app.log

# 查看系统日志
journalctl -u invest-plt -f
```

## 安全建议

1. **使用 HTTPS**
   - 配置 SSL 证书
   - 强制 HTTPS 重定向

2. **环境变量**
   - 不要在代码中硬编码敏感信息
   - 使用 `.env` 文件管理配置

3. **访问控制**
   - 添加用户认证
   - 限制 API 访问频率

4. **数据库安全**
   - 定期备份
   - 使用强密码
   - 限制数据库访问

## 更新与维护

### 更新依赖

```bash
# 后端
pip install --upgrade -r requirements.txt

# 前端
cd frontend
npm update
```

### 数据库迁移

```bash
# 备份数据库
cp backend/invest.db backend/invest.db.backup

# 执行迁移脚本
python backend/migrate.py
```

### 版本回滚

```bash
# 恢复数据库
cp backend/invest.db.backup backend/invest.db

# 回滚代码
git checkout <previous-version>
```
