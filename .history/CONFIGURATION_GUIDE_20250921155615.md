# 🔧 StockManager 后端配置指南

## 📋 项目概述

StockManager是一个基于Django的股票管理系统后端，集成了XtQuant交易接口，提供账户信息查询、资产对比分析等功能。

## 🚀 快速开始

### 1. 环境配置

#### 创建Conda环境
```bash
# 创建Python 3.8环境
conda create -n ssc python=3.8
conda activate ssc

# 安装依赖
pip install django xtquant pymongo djangorestframework django-cors-headers djangorestframework-simplejwt
```

#### 启动项目
```bash
# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 启动服务器
python manage.py runserver
```

### 2. 🎯 XtQuant配置

#### 客户端路径配置
找到你的**国金QMT**或**迅投QMT**安装目录：

**国金QMT路径示例**：
```
C:\国金证券QMT交易端\userdata_mini
D:\国金证券QMT交易端\userdata_mini
```

**迅投QMT路径示例**：
```
D:\迅投极速交易终端 睿智融科版\userdata
E:\迅投极速交易终端\userdata
```

#### 环境变量配置
创建 `.env` 文件：
```env
# XtQuant配置
XT_USERDATA_PATH=你的实际路径\userdata_mini
XT_TOKEN=你的实际token
XT_API_KEY=你的API密钥
XT_SECRET_KEY=你的密钥
```

### 3. 📊 当前API状态

#### ✅ 已实现的API端点
| API端点 | 功能 | 状态 |
|---------|------|------|
| `/api/auth/register/` | 用户注册 | ✅ 完成 |
| `/api/auth/login/` | 用户登录 | ✅ 完成 |
| `/api/auth/profile/` | 获取用户资料 | ✅ 完成 |
| `/api/auth/logout/` | 退出登录 | ✅ 完成 |
| `/api/account-info/` | 账户信息查询 | ✅ 完成 |
| `/api/asset_comparison/` | 资产对比分析 | ✅ 完成 |
| `/api/timecomparison/yearly_comparison/` | 年度对比 | ✅ 完成 |
| `/api/timecomparison/weekly_comparison/` | 周度对比 | ✅ 完成 |

#### 🔄 数据来源
- **账户信息**: 真实QMT数据
- **持仓数据**: 真实QMT数据  
- **历史对比**: XtQuant历史数据中心
- **认证系统**: Django JWT认证

### 4. 🧪 测试验证

#### 运行测试脚本
```bash
# 测试API连接
python test_api.py

# 测试认证功能
python test_auth_api.py

# 测试账户信息
python test_account_api.py
```

#### 验证XtQuant连接
```bash
# Django shell测试
python manage.py shell
>>> import xtquant.xtdata as xtdata
>>> print("数据目录:", xtdata.data_dir)
>>> print("服务器状态:", xtdata.get_quote_server_status())
```

## 📋 配置检查清单

- [x] 创建Conda环境 `ssc`
- [x] 安装所有依赖包
- [x] 配置XtQuant路径和Token
- [x] 数据库迁移完成
- [x] API端点测试通过
- [x] XtQuant连接正常

## 🔧 故障排除

### 常见问题

1. **XtQuant连接失败**
   - 检查QMT客户端是否启动
   - 验证路径和Token是否正确
   - 确认端口58601是否可用

2. **API返回500错误**
   - 检查Django日志输出
   - 验证XtQuant配置
   - 确认数据库连接正常

3. **认证失败**
   - 检查JWT配置
   - 验证用户数据
   - 确认Token格式正确

## 📞 技术支持

- **API文档**: 参考 `API_DOCUMENTATION.md`
- **测试脚本**: 使用项目根目录的test_*.py文件
- **日志查看**: Django控制台输出和 `django.log` 文件
