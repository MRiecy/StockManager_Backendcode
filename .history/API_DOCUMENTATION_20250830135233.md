# StockManager 后端API文档

## 概述
本文档描述了StockManager后端系统的所有API接口，包括用户认证、账户信息、对比分析等功能。

## 基础信息
- **基础URL**: `http://localhost:8000/api`
- **认证方式**: JWT Token (Bearer)
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "errors": {
    // 详细错误信息（可选）
  }
}
```

## 1. 用户认证相关接口

### 1.1 发送手机验证码
- **接口路径**: `POST /api/auth/send-code/`
- **功能**: 向指定手机号发送登录验证码
- **请求参数**:
```json
{
  "phone": "13888888888"
}
```
- **响应数据**:
```json
{
  "success": true,
  "message": "验证码已发送",
  "data": {
    "expire_time": 300,
    "can_resend_time": 60
  }
}
```
- **说明**: 
  - `expire_time`: 验证码有效期（秒）
  - `can_resend_time`: 可重新发送时间（秒）
  - 同一手机号1分钟内只能发送一次

### 1.2 手机号登录/注册
- **接口路径**: `POST /api/auth/login/`
- **功能**: 使用手机号和验证码进行登录，首次使用自动注册
- **请求参数**:
```json
{
  "phone": "13888888888",
  "code": "123456"
}
```
- **响应数据**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user": {
      "user_id": "user_123456",
      "phone": "13888888888",
      "nickname": "用户8888",
      "avatar": "",
      "is_new_user": false,
      "created_at": "2024-01-01T00:00:00Z",
      "last_login": "2024-01-01T00:00:00Z"
    },
    "token": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 3600
    }
  }
}
```

### 1.3 刷新访问令牌
- **接口路径**: `POST /api/auth/refresh/`
- **功能**: 使用refresh_token刷新access_token
- **请求头**: 
```
Authorization: Bearer refresh_token_here
```
- **响应数据**:
```json
{
  "success": true,
  "message": "Token刷新成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 3600
  }
}
```

### 1.4 退出登录
- **接口路径**: `POST /api/auth/logout/`
- **功能**: 注销当前用户会话，使token失效
- **认证**: 需要access_token
- **请求头**:
```
Authorization: Bearer access_token_here
```
- **响应数据**:
```json
{
  "success": true,
  "message": "退出登录成功"
}
```

### 1.5 获取当前用户信息
- **接口路径**: `GET /api/auth/profile/`
- **功能**: 获取当前登录用户的详细信息
- **认证**: 需要access_token
- **请求头**:
```
Authorization: Bearer access_token_here
```
- **响应数据**:
```json
{
  "success": true,
  "data": {
    "user_id": "user_123456",
    "phone": "13888888888",
    "nickname": "用户8888",
    "avatar": "",
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T00:00:00Z",
    "account_status": "active",
    "permissions": ["read", "write"]
  }
}
```

## 2. 账户信息相关接口

### 2.1 获取账户基本信息
- **接口路径**: `GET /api/account-info/`
- **功能**: 获取账户资产、持仓等基本信息
- **认证**: 需要access_token
- **请求头**:
```
Authorization: Bearer access_token_here
```
- **响应数据**:
```json
{
  "accounts": [
    {
      "account_type": "STOCK",
      "account_id": "DEMO000001",
      "cash": 1250000,
      "frozen_cash": 75000,
      "market_value": 2850000,
      "total_asset": 4100000,
      "positions": [
        {
          "account_type": "STOCK",
          "account_id": "DEMO000001",
          "stock_code": "000001.SZ",
          "volume": 10000,
          "can_use_volume": 10000,
          "open_price": 12.5,
          "market_value": 125000,
          "frozen_volume": 0,
          "on_road_volume": 0,
          "yesterday_volume": 10000,
          "avg_price": 12.5
        }
      ]
    }
  ]
}
```

### 2.2 获取资产类别分布
- **接口路径**: `GET /api/asset-category/`
- **功能**: 获取按行业分类的资产分布
- **认证**: 需要access_token
- **请求参数**: `account_id` (可选)
- **响应数据**:
```json
{
  "message": "此API暂未实现真实数据查询，前端使用模拟数据",
  "data_available": false
}
```

### 2.3 获取地区分布数据
- **接口路径**: `GET /api/region-data/`
- **功能**: 获取按地区分类的资产分布
- **认证**: 需要access_token
- **响应数据**:
```json
{
  "success": true,
  "data": [
    {
      "region": "上海",
      "totalAssets": 820000,
      "returnRate": "8.5%",
      "maxDrawdown": 28.8
    },
    {
      "region": "深圳",
      "totalAssets": 712500,
      "returnRate": "7.8%",
      "maxDrawdown": 25.0
    }
  ]
}
```

## 3. 对比分析相关接口

### 3.1 资产对比分析
- **接口路径**: `GET /api/asset_comparison/`
- **功能**: 获取资产对比分析数据
- **认证**: 需要access_token
- **请求参数**: `account_id` (必填)
- **响应数据**:
```json
{
  "total_market_value": 2850000,
  "positions": [
    {
      "stock_code": "000001.SZ",
      "asset_ratio": 0.0439,
      "market_value": 125000,
      "daily_return": 2.5
    }
  ]
}
```

### 3.2 年度对比分析
- **接口路径**: `GET /api/timecomparison/yearly_comparison/`
- **功能**: 获取年度对比分析数据
- **认证**: 需要access_token
- **请求参数**: `account_id` (可选，默认40000326)
- **响应数据**:
```json
{
  "yearly_data": [
    {
      "timePeriod": "2022",
      "totalAssets": 3500000,
      "marketValue": 2400000,
      "returnRate": 5.2,
      "growthRate": 8.5
    }
  ],
  "data_available": true,
  "source": "XtQuant历史数据中心"
}
```

### 3.3 周度对比分析
- **接口路径**: `GET /api/timecomparison/weekly_comparison/`
- **功能**: 获取周度对比分析数据
- **认证**: 需要access_token
- **请求参数**: `account_id` (可选，默认40000326)
- **响应数据**:
```json
{
  "weekly_data": [
    {
      "timePeriod": "2024-W52",
      "totalAssets": 4100000,
      "marketValue": 2850000,
      "returnRate": 8.0,
      "growthRate": 12.3
    }
  ],
  "data_available": true,
  "source": "XtQuant历史数据中心"
}
```

### 3.4 地区对比分析
- **接口路径**: `GET /api/areacomparsion/area_comparison/`
- **功能**: 获取地区对比分析数据
- **认证**: 需要access_token
- **请求参数**: `account_id` (可选，默认40000326)
- **响应数据**:
```json
{
  "area_data": [
    {
      "region": "上海",
      "totalAssets": 820000,
      "returnRate": "8.5%",
      "maxDrawdown": 28.8
    }
  ],
  "is_mock": false,
  "message": "基于真实持仓数据计算地区分布"
}
```

## 4. 错误码说明

### HTTP状态码
- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未认证或认证失败
- `403`: 权限不足
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误

### 业务错误码
- `INVALID_PHONE`: 手机号格式错误
- `INVALID_CODE`: 验证码格式错误
- `CODE_EXPIRED`: 验证码已过期
- `CODE_USED`: 验证码已使用
- `TOO_FREQUENT`: 请求过于频繁
- `TOKEN_EXPIRED`: 令牌已过期
- `TOKEN_INVALID`: 令牌无效

## 5. 认证流程

### 5.1 登录流程
1. 调用 `/api/auth/send-code/` 发送验证码
2. 用户输入验证码
3. 调用 `/api/auth/login/` 进行登录
4. 获取access_token和refresh_token
5. 后续请求在Header中携带access_token

### 5.2 Token刷新流程
1. access_token过期时，使用refresh_token调用 `/api/auth/refresh/`
2. 获取新的access_token
3. 继续使用新的access_token

### 5.3 退出登录流程
1. 调用 `/api/auth/logout/` 使当前token失效
2. 清除本地存储的token

## 6. 开发环境配置

### 6.1 安装依赖
```bash
pip install -r requirements.txt
```

### 6.2 数据库迁移
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6.3 创建超级用户
```bash
python manage.py createsuperuser
```

### 6.4 启动服务
```bash
python manage.py runserver
```

### 6.5 测试API
```bash
python test_auth_api.py
```

## 7. 注意事项

1. **安全性**: 
   - 生产环境请修改SECRET_KEY
   - 启用HTTPS
   - 配置适当的CORS策略

2. **性能**: 
   - 验证码有效期设置为5分钟
   - 请求频率限制为1分钟
   - 使用数据库索引优化查询

3. **监控**: 
   - 记录API调用日志
   - 监控错误率和响应时间
   - 设置告警机制

4. **扩展性**: 
   - 支持多数据库后端
   - 可配置的验证码服务
   - 灵活的权限系统

## 8. 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 实现用户认证系统
- 实现账户信息查询
- 实现对比分析功能
- 集成XtQuant交易接口 