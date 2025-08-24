# 🔧 StockManager 后端配置指南

## 必须调整的配置项

### 1. 创建环境变量文件
```bash
# 复制示例文件
cp .env.example .env
```

### 2. 🎯 关键路径配置

#### XtQuant 客户端路径
找到你的**国金QMT**安装目录，通常在：
```
# 可能的路径位置：
C:\国金证券QMT交易端\userdata_mini
D:\国金证券QMT交易端\userdata_mini
E:\国金证券QMT交易端\userdata_mini

# 或者迅投版本：
D:\迅投极速交易终端 睿智融科版\userdata
```

在 `.env` 文件中设置：
```env
XT_USERDATA_PATH=你的实际路径\userdata_mini
```

### 3. 🔑 Token 获取方式

#### 获取 XtQuant Token：
1. 打开国金QMT客户端
2. 登录你的账户
3. 在客户端中找到API设置或开发者选项
4. 获取或生成Token
5. 将Token填入 `.env` 文件：
```env
XT_TOKEN=你的实际token
```

### 4. 📊 数据类型说明

#### 当前状态：
- ✅ **已有真实数据接口**：`/api/account-info/` 和 `/api/asset_comparison/`
- ⚠️ **路径配置不统一**：需要修复硬编码路径
- 🔄 **需要扩展**：更多数据类型的API

#### 真实数据 vs 模拟数据：
你的项目**已经在使用真实数据**，通过XtQuant SDK连接国金QMT获取：
- 账户资产信息
- 持仓数据
- 交易记录

## 🚀 立即修复步骤

### Step 1: 修复路径不一致问题
需要修改 `apps/Comparison/views.py` 第48行，使用统一配置

### Step 2: 验证连接
运行后端，测试API是否能正常获取数据

### Step 3: 扩展API接口
添加更多QMT数据接口（行情、K线等）

## 📋 配置检查清单

- [ ] 找到国金QMT安装路径
- [ ] 创建 `.env` 文件并配置路径
- [ ] 获取并配置XtQuant Token
- [ ] 修复代码中的硬编码路径
- [ ] 测试API连接
- [ ] 验证数据返回格式
