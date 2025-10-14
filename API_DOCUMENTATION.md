# API 文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **数据格式**: JSON
- **字符编码**: UTF-8

## API 端点

### 1. 系统管理

#### 1.1 健康检查

```
GET /health
```

**响应示例**:
```json
{
  "status": "ok",
  "timestamp": "2024-10-13T15:30:00"
}
```

#### 1.2 获取系统状态

```
GET /system/status
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "is_initialized": true,
    "total_indices": 1500,
    "favorite_indices": 10,
    "latest_data_date": "2024-10-13",
    "latest_ratio_date": "2024-10-13"
  }
}
```

#### 1.3 初始化数据

```
POST /data/init
```

**说明**: 首次运行时初始化所有数据，包括指数列表、历史数据、财务数据等。

**响应示例**:
```json
{
  "success": true,
  "message": "数据初始化成功"
}
```

#### 1.4 刷新数据

```
POST /data/refresh
```

**请求体**:
```json
{
  "type": "all"  // 可选: "all", "indices", "financials", "calculate"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "数据刷新成功"
}
```

### 2. 指数管理

#### 2.1 获取指数列表

```
GET /indices?is_favorite=true&search=沪深300
```

**查询参数**:
- `is_favorite` (可选): 筛选自选指数 (true/false)
- `search` (可选): 搜索关键词（指数名称或代码）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "code": "000300",
      "name": "沪深300",
      "name_en": "CSI 300",
      "is_favorite": true,
      "manual_weight": 1.0,
      "latest_date": "2024-10-13",
      "pe_ttm": 12.5,
      "pb": 1.5,
      "close": 3500.0,
      "metrics": {
        "pe_percentile": 45.2,
        "pb_percentile": 42.8,
        "weighted_roe": 12.5,
        "roe_weight": 1.25,
        "percentile_range": "35%-50%",
        "initial_score": 25,
        "composite_weight": 1.25,
        "composite_score": 31.25,
        "target_position": 15.5,
        "operation_signal": null,
        "operation_percent": null
      }
    }
  ],
  "total": 1
}
```

#### 2.2 获取指数详情

```
GET /indices/{index_id}?days=365
```

**路径参数**:
- `index_id`: 指数ID

**查询参数**:
- `days` (可选): 获取历史数据天数，默认365

**响应示例**:
```json
{
  "success": true,
  "data": {
    "index": {
      "id": 1,
      "code": "000300",
      "name": "沪深300",
      "is_favorite": true,
      "manual_weight": 1.0
    },
    "history": [
      {
        "date": "2024-10-13",
        "open": 3480.0,
        "high": 3520.0,
        "low": 3470.0,
        "close": 3500.0,
        "volume": 1500.0,
        "amount": 2000.0,
        "pe_ttm": 12.5,
        "pb": 1.5
      }
    ],
    "metrics": [
      {
        "date": "2024-10-13",
        "pe_percentile": 45.2,
        "composite_score": 31.25,
        "target_position": 15.5
      }
    ]
  }
}
```

#### 2.3 切换自选状态

```
POST /indices/{index_id}/favorite
```

**请求体**:
```json
{
  "is_favorite": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "code": "000300",
    "name": "沪深300",
    "is_favorite": true
  }
}
```

#### 2.4 更新人为权重

```
PUT /indices/{index_id}/weight
```

**请求体**:
```json
{
  "manual_weight": 1.5
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "manual_weight": 1.5
  }
}
```

### 3. 股债性价比

#### 3.1 获取股债性价比数据

```
GET /stock-bond-ratio?days=365
```

**查询参数**:
- `days` (可选): 获取历史数据天数，默认365

**响应示例**:
```json
{
  "success": true,
  "data": {
    "latest": {
      "date": "2024-10-13",
      "csi800_pe": 13.2,
      "bond_yield_10y": 2.5,
      "ratio": 0.0507,
      "percentile_10y": 65.5,
      "stock_allocation": 65.5
    },
    "history": [
      {
        "date": "2024-10-12",
        "ratio": 0.0505,
        "percentile_10y": 64.8
      }
    ]
  }
}
```

### 4. 仪表盘

#### 4.1 获取仪表盘数据

```
GET /dashboard
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "stock_bond_ratio": {
      "date": "2024-10-13",
      "csi800_pe": 13.2,
      "bond_yield_10y": 2.5,
      "ratio": 0.0507,
      "percentile_10y": 65.5,
      "stock_allocation": 65.5
    },
    "indices": [
      {
        "index": {
          "id": 1,
          "code": "000300",
          "name": "沪深300"
        },
        "metrics": {
          "pe_percentile": 45.2,
          "target_position": 15.5,
          "operation_signal": "add",
          "operation_percent": 5.0
        },
        "valuation": {
          "pe_ttm": 12.5,
          "pb": 1.5,
          "close": 3500.0
        }
      }
    ],
    "update_time": "2024-10-13T15:30:00"
  }
}
```

## 错误响应

所有错误响应格式统一：

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

常见HTTP状态码：
- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

## 数据更新机制

1. **首次初始化**: 调用 `/data/init` 接口
2. **手动刷新**: 调用 `/data/refresh` 接口
3. **自动更新**: 每交易日15:30自动执行（通过定时任务）

## 计算逻辑说明

### 股债性价比

```
股债性价比 = 1/中证800市盈率 - 10年国债收益率
分位数 = 当前值在近10年数据中的排名百分比
股票配置比例 = 分位数
```

### 估值分位区间

| 区间 | 初始分数 |
|------|---------|
| 0%-10% | 40 |
| 10%-20% | 35 |
| 20%-35% | 30 |
| 35%-50% | 25 |
| 50%-65% | 20 |
| 65%-80% | 15 |
| 80%-90% | 10 |
| 90%-100% | 5 |

### ROE权重

```
ROE权重 = 1.0 + (ROE - 10) × 0.1
当ROE ≤ 0或缺失时，权重 = 1.0
```

### 综合分数与仓位

```
综合权重 = ROE权重 × 人为权重
综合分数 = 初始分数 × 综合权重
目标仓位 = (该指数综合分数 / 所有自选指数综合分数之和) × 100%
```

### 操作信号

- **加仓**: 分位数向下突破区间下限，且达到上一区间均值
- **减仓**: 分位数向上突破区间上限
