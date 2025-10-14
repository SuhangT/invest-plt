# 数据抓取重试机制说明

## 概述

为了应对公开API接口的不稳定性，系统已经实现了强大的**自动重试机制**，确保数据抓取的可靠性。

## 核心特性

### 1. 智能重试装饰器

```python
@retry_on_failure(max_retries=10, min_delay=2, max_delay=10)
```

**参数说明**：
- `max_retries`: 最大重试次数（默认10次）
- `min_delay`: 最小延迟时间（默认2秒）
- `max_delay`: 最大延迟时间（默认10秒）

### 2. 随机延迟机制

每次API调用之间会有**随机延迟**，避免触发频率限制：

```python
delay = random.uniform(min_delay, max_delay)
```

这样可以：
- 避免固定间隔被识别为机器人
- 降低触发API频率限制的概率
- 提高长期稳定性

### 3. 详细日志记录

每次重试都会记录详细日志：

```
[重试 1/10] _fetch_index_history_data 失败: Connection timeout, 5.3秒后重试...
[重试 2/10] _fetch_index_history_data 失败: HTTP 429 Too Many Requests, 7.8秒后重试...
[成功] _fetch_index_history_data 在第3次尝试后成功
```

## 已实现重试的接口

### 1. 指数列表获取
```python
fetcher._fetch_indices_data()
```
- **用途**: 获取所有中证指数列表
- **重试次数**: 10次
- **延迟范围**: 3-10秒

### 2. 指数历史数据
```python
fetcher._fetch_index_history_data(index_code, start_date, end_date)
```
- **用途**: 获取指定指数的历史行情数据
- **重试次数**: 10次
- **延迟范围**: 3-10秒

### 3. 指数成份股
```python
fetcher._fetch_constituents_data(index_code)
```
- **用途**: 获取指数成份股及权重
- **重试次数**: 10次
- **延迟范围**: 3-10秒

### 4. 财务数据
```python
fetcher._fetch_financials_data(report_date)
```
- **用途**: 获取股票财务报表数据
- **重试次数**: 10次
- **延迟范围**: 3-10秒

### 5. 国债收益率
```python
fetcher._fetch_bond_yield_data()
```
- **用途**: 获取10年期国债收益率
- **重试次数**: 10次
- **延迟范围**: 3-10秒

## 使用示例

### 基本使用

```python
from data_fetcher import DataFetcher

# 使用默认配置（10次重试，2-10秒延迟）
fetcher = DataFetcher()

# 获取数据（自动重试）
fetcher.fetch_index_history('000906')
```

### 自定义重试参数

```python
# 更激进的重试策略（15次重试，5-15秒延迟）
fetcher = DataFetcher(max_retries=15, min_delay=5, max_delay=15)

# 更保守的重试策略（5次重试，1-5秒延迟）
fetcher = DataFetcher(max_retries=5, min_delay=1, max_delay=5)
```

### 测试重试机制

```bash
cd backend
python test_retry.py
```

## 重试策略说明

### 何时触发重试？

1. **网络错误**: 连接超时、DNS解析失败等
2. **API错误**: HTTP 429（频率限制）、500（服务器错误）等
3. **数据异常**: 返回空数据、数据格式错误等
4. **函数返回False**: 任何返回False的情况

### 重试间隔计算

```python
delay = random.uniform(min_delay, max_delay)
```

**示例**（min_delay=3, max_delay=10）：
- 第1次重试: 等待 5.3秒
- 第2次重试: 等待 7.8秒
- 第3次重试: 等待 4.1秒
- 第4次重试: 等待 9.2秒
- ...

### 失败处理

如果所有重试都失败：
1. 记录错误日志
2. 返回 `False`
3. 不会抛出异常（避免中断整个流程）
4. 调用方可以根据返回值决定后续操作

## 最佳实践

### 1. 批量抓取时的策略

```python
fetcher = DataFetcher(max_retries=10, min_delay=3, max_delay=10)

success_count = 0
fail_count = 0

for index_code in index_codes:
    result = fetcher.fetch_index_history(index_code)
    if result:
        success_count += 1
    else:
        fail_count += 1
        # 记录失败的指数，稍后重试
        failed_indices.append(index_code)

print(f"成功: {success_count}, 失败: {fail_count}")

# 对失败的指数进行二次尝试
if failed_indices:
    print("开始二次尝试...")
    time.sleep(60)  # 等待1分钟
    for index_code in failed_indices:
        fetcher.fetch_index_history(index_code)
```

### 2. 非交易时间抓取

建议在**非交易时间**（如晚上）进行大量数据抓取：
- API负载较低
- 成功率更高
- 不影响日常使用

### 3. 监控重试情况

查看日志文件，监控重试频率：

```bash
# 查看重试日志
grep "重试" logs/app.log

# 统计重试次数
grep "重试" logs/app.log | wc -l

# 查看失败的接口
grep "已重试.*次仍然失败" logs/app.log
```

### 4. 调整重试参数

根据实际情况调整：

**网络不稳定**：
```python
fetcher = DataFetcher(max_retries=15, min_delay=5, max_delay=15)
```

**API限流严格**：
```python
fetcher = DataFetcher(max_retries=10, min_delay=10, max_delay=30)
```

**快速测试**：
```python
fetcher = DataFetcher(max_retries=3, min_delay=1, max_delay=3)
```

## 性能影响

### 时间成本

假设每次API调用需要2秒，重试配置为10次，延迟3-10秒：

**最坏情况**（所有重试都失败）：
```
总时间 = 10次尝试 × 2秒 + 9次延迟 × 平均6.5秒
       = 20秒 + 58.5秒
       = 78.5秒
```

**正常情况**（第2次成功）：
```
总时间 = 2次尝试 × 2秒 + 1次延迟 × 6.5秒
       = 4秒 + 6.5秒
       = 10.5秒
```

### 资源占用

- **CPU**: 几乎无额外占用
- **内存**: 每个重试增加约1KB日志
- **网络**: 失败重试会增加流量

## 故障排查

### 问题1: 所有请求都失败

**可能原因**：
- 网络完全断开
- API服务器宕机
- IP被封禁

**解决方案**：
1. 检查网络连接
2. 访问akshare官网确认服务状态
3. 更换网络环境或使用代理

### 问题2: 部分请求失败

**可能原因**：
- 特定接口不稳定
- 特定参数导致错误
- 偶发性网络波动

**解决方案**：
1. 查看日志确定失败的接口
2. 手动测试该接口
3. 增加重试次数和延迟时间

### 问题3: 重试次数过多

**可能原因**：
- 延迟时间太短
- API频率限制严格
- 并发请求过多

**解决方案**：
1. 增加延迟时间（min_delay, max_delay）
2. 减少并发请求
3. 分批次抓取数据

## 配置建议

### 开发环境
```python
DataFetcher(max_retries=3, min_delay=1, max_delay=3)
```
- 快速失败，便于调试

### 生产环境
```python
DataFetcher(max_retries=10, min_delay=3, max_delay=10)
```
- 平衡可靠性和性能

### 首次初始化
```python
DataFetcher(max_retries=15, min_delay=5, max_delay=15)
```
- 最大化成功率，时间不敏感

## 更新日志

### v1.1.0 (2024-10-14)
- ✅ 添加智能重试装饰器
- ✅ 实现随机延迟机制
- ✅ 所有API接口支持重试
- ✅ 详细的重试日志记录
- ✅ 可配置的重试参数

### v1.0.0 (2024-10-13)
- 基础数据抓取功能

## 技术细节

### 装饰器实现

```python
def retry_on_failure(max_retries=10, min_delay=2, max_delay=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    result = func(*args, **kwargs)
                    if result is False and attempt < max_retries - 1:
                        raise Exception("Function returned False")
                    return result
                except Exception as e:
                    if attempt < max_retries - 1:
                        delay = random.uniform(min_delay, max_delay)
                        logger.warning(f"[重试 {attempt + 1}/{max_retries}] ...")
                        time.sleep(delay)
            return False
        return wrapper
    return decorator
```

### 关键设计决策

1. **使用装饰器**: 保持代码简洁，易于维护
2. **随机延迟**: 避免固定模式被识别
3. **不抛出异常**: 避免中断整个流程
4. **详细日志**: 便于监控和调试
5. **可配置参数**: 适应不同场景

## 参考资料

- [akshare官方文档](https://akshare.akfamily.xyz/)
- [Python装饰器详解](https://docs.python.org/zh-cn/3/glossary.html#term-decorator)
- [重试策略最佳实践](https://aws.amazon.com/cn/blogs/architecture/exponential-backoff-and-jitter/)

---

**注意**: 虽然重试机制大大提高了成功率，但仍建议在非高峰时段进行大量数据抓取，以获得最佳效果。
