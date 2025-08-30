# 🚀 前端对接指南 - Django后端API集成

## 📋 后端API现状

### ✅ 已完成的API端点

**后端服务器地址**: `http://localhost:8000`

| API端点 | 方法 | 功能 | 状态 |
|---------|------|------|------|
| `/api/account-info/` | GET | 获取所有账户信息 | ✅ 已测试 |
| `/api/asset_comparison/?account_id={id}` | GET | 获取账户资产对比数据 | ✅ 已测试 |

### 📊 真实数据示例

**账户信息API返回格式**:
```json
{
  "accounts": [
    {
      "account_type": 2,
      "account_id": "40000326", 
      "cash": 19836910.13,
      "frozen_cash": 0.0,
      "market_value": 169841.2,
      "total_asset": 20011501.63,
      "positions": [
        {
          "account_type": 2,
          "account_id": "40000326",
          "stock_code": "000001.SZ",
          "volume": 1000,
          "can_use_volume": 1000,
          "open_price": 12.50,
          "market_value": 12500.0,
          "avg_price": 12.30
        }
      ]
    }
  ]
}
```

**资产对比API返回格式**:
```json
{
  "total_market_value": 169841.2,
  "positions": [
    {
      "stock_code": "000001.SZ",
      "asset_ratio": 0.0736,
      "market_value": 12500.0,
      "daily_return": 1.63
    }
  ]
}
```

## 🎯 与前端AI的沟通模板

### **模板1: 基础API对接**

```
请帮我在Vue3前端项目中集成Django后端API，实现QMT数据的动态显示：

【后端API信息】
- 后端地址：http://localhost:8000
- 已有API端点：
  1. GET /api/account-info/ - 获取账户信息
  2. GET /api/asset_comparison/?account_id=40000326 - 获取资产对比

【前端需求】
- 使用Axios发送HTTP请求
- 在现有Vue组件中展示数据
- 添加加载状态和错误处理
- 实现数据的定时刷新

【数据格式】
账户信息包含：账户ID、可用资金、总资产、持仓市值、持仓列表
资产对比包含：总市值、各股票占比、市值、涨跌幅

请提供完整的Vue组件代码和Axios配置。
```

### **模板2: 数据可视化集成**

```
请帮我将Django后端的QMT数据集成到现有的ECharts图表中：

【后端数据源】
- API地址：http://localhost:8000/api/asset_comparison/?account_id=40000326
- 返回数据：股票代码、资产占比、市值、涨跌幅

【图表需求】
1. 饼图：显示各股票的资产占比
2. 柱状图：显示各股票的市值
3. 散点图：显示涨跌幅分布

【技术栈】
- Vue 3 + Composition API
- ECharts 5.x
- Element Plus UI

请提供完整的图表组件代码，包括数据获取、图表配置和响应式更新。
```

### **模板3: 实时数据更新**

```
请帮我实现前端的实时数据更新功能：

【后端API】
- 账户数据：GET /api/account-info/
- 资产数据：GET /api/asset_comparison/?account_id=40000326

【实时更新需求】
- 每30秒自动刷新数据
- 用户可手动刷新
- 显示最后更新时间
- 网络错误时的重试机制

【UI要求】
- 加载动画
- 数据变化的过渡效果
- 错误提示
- 刷新按钮

请提供Vue3的完整实现方案。
```

## 🔧 前端开发配置

### **Axios配置建议**

```javascript
// api/config.js
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  config => {
    console.log('发送请求:', config.url)
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
apiClient.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API请求错误:', error)
    return Promise.reject(error)
  }
)

export default apiClient
```

### **API服务封装**

```javascript
// api/qmtService.js
import apiClient from './config'

export const qmtAPI = {
  // 获取账户信息
  getAccountInfo() {
    return apiClient.get('/api/account-info/')
  },
  
  // 获取资产对比
  getAssetComparison(accountId) {
    return apiClient.get(`/api/asset_comparison/?account_id=${accountId}`)
  }
}
```

## 🚨 重要注意事项

### **CORS配置**
后端已配置CORS允许跨域访问：
```python
CORS_ALLOW_ALL_ORIGINS = True
```

### **数据格式说明**
- 所有金额字段为浮点数（单位：元）
- 股票代码格式：`000001.SZ`（深交所）、`600000.SH`（上交所）
- 账户类型：`2`表示股票账户

### **错误处理**
常见错误码：
- `400`: 参数错误（如缺少account_id）
- `500`: 服务器错误（如QMT连接失败）

## 📞 技术支持

如果前端集成过程中遇到问题：

1. **后端API测试**: 使用 `python test_api.py` 验证后端功能
2. **服务器启动**: `python manage.py runserver 8000`
3. **数据格式**: 参考上述JSON示例
4. **实时调试**: 查看Django服务器终端输出

---

**准备就绪！** 使用上述模板与前端AI沟通，可以快速实现前后端数据对接。
