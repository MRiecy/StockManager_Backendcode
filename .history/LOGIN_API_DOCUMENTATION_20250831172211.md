# 🔐 用户名密码登录API文档

## 📋 概述

本文档描述了股票管理系统后端的用户名密码登录认证API接口。系统使用用户名+密码的方式进行用户认证，支持JWT令牌管理。

## 🚀 API端点

### 基础信息
- **服务器地址**: `http://localhost:8000`
- **API前缀**: `/api`
- **认证方式**: JWT Bearer Token

---

## 📝 1. 用户注册

### 接口信息
- **URL**: `/api/auth/register/`
- **方法**: `POST`
- **描述**: 注册新用户账户
- **认证**: 不需要认证

### 请求参数
```json
{
    "username": "testuser",
    "password": "123456",
    "confirm_password": "123456",
    "nickname": "测试用户",
    "phone": "13800138000"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "user": {
            "user_id": "user_db9e830a",
            "username": "testuser",
            "phone": "13800138000",
            "nickname": "测试用户",
            "avatar": null,
            "is_new_user": true,
            "created_at": "2025-08-31T09:16:20.374862Z",
            "last_login": "2025-08-31T09:16:20.374898Z",
            "account_status": "active"
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

### 错误响应
```json
{
    "success": false,
    "message": "参数错误",
    "errors": {
        "username": ["用户名已存在"],
        "password": ["密码长度至少6位"],
        "confirm_password": ["两次输入的密码不一致"]
    }
}
```

---

## 🔑 2. 用户登录

### 接口信息
- **URL**: `/api/auth/login/`
- **方法**: `POST`
- **描述**: 使用用户名和密码登录
- **认证**: 不需要认证

### 请求参数
```json
{
    "username": "testuser",
    "password": "123456"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "user": {
            "user_id": "user_db9e830a",
            "username": "testuser",
            "phone": "13800138000",
            "nickname": "测试用户",
            "avatar": null,
            "is_new_user": false,
            "created_at": "2025-08-31T09:16:20.374862Z",
            "last_login": "2025-08-31T09:16:22.771372Z",
            "account_status": "active"
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

### 错误响应
```json
{
    "success": false,
    "message": "用户名或密码错误"
}
```

---

## 🔄 3. 刷新访问令牌

### 接口信息
- **URL**: `/api/auth/refresh/`
- **方法**: `POST`
- **描述**: 使用refresh_token刷新access_token
- **认证**: 需要Authorization头

### 请求头
```
Authorization: Bearer {refresh_token}
```

### 响应格式
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

---

## 👤 4. 获取用户资料

### 接口信息
- **URL**: `/api/auth/profile/`
- **方法**: `GET`
- **描述**: 获取当前登录用户的详细资料
- **认证**: 需要Authorization头

### 请求头
```
Authorization: Bearer {access_token}
```

### 响应格式
```json
{
    "success": true,
    "message": "获取用户资料成功",
    "data": {
        "user_id": "user_db9e830a",
        "username": "testuser",
        "phone": "13800138000",
        "nickname": "测试用户",
        "avatar": null,
        "created_at": "2025-08-31T09:16:20.374862Z",
        "last_login": "2025-08-31T09:16:22.771372Z",
        "account_status": "active"
    }
}
```

---

## ✏️ 5. 更新用户资料

### 接口信息
- **URL**: `/api/auth/profile/update/`
- **方法**: `POST`
- **描述**: 更新当前登录用户的资料
- **认证**: 需要Authorization头

### 请求头
```
Authorization: Bearer {access_token}
```

### 请求参数
```json
{
    "nickname": "新昵称",
    "avatar": "新头像URL",
    "phone": "13900139000"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "更新用户资料成功",
    "data": {
        "user_id": "user_db9e830a",
        "username": "testuser",
        "phone": "13900139000",
        "nickname": "新昵称",
        "avatar": "新头像URL",
        "created_at": "2025-08-31T09:16:20.374862Z",
        "last_login": "2025-08-31T09:16:22.771372Z",
        "account_status": "active"
    }
}
```

---

## 🚪 6. 退出登录

### 接口信息
- **URL**: `/api/auth/logout/`
- **方法**: `POST`
- **描述**: 退出登录，使当前token失效
- **认证**: 需要Authorization头

### 请求头
```
Authorization: Bearer {access_token}
```

### 响应格式
```json
{
    "success": true,
    "message": "退出登录成功"
}
```

---

## 🔧 前端集成示例

### Axios配置
```javascript
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// 请求拦截器 - 添加token
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器 - 处理token过期
apiClient.interceptors.response.use(
  response => response.data,
  async error => {
    if (error.response?.status === 401) {
      // token过期，尝试刷新
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh/`, {}, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          })
          if (response.data.success) {
            localStorage.setItem('access_token', response.data.data.access_token)
            // 重试原请求
            return apiClient.request(error.config)
          }
        } catch (refreshError) {
          // 刷新失败，跳转到登录页
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          window.location.href = '/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 登录服务
```javascript
// services/authService.js
import apiClient from './apiClient'

export const authService = {
  // 注册
  register(data) {
    return apiClient.post('/auth/register/', data)
  },
  
  // 登录
  login(username, password) {
    return apiClient.post('/auth/login/', { username, password })
  },
  
  // 获取用户资料
  getProfile() {
    return apiClient.get('/auth/profile/')
  },
  
  // 更新用户资料
  updateProfile(data) {
    return apiClient.post('/auth/profile/update/', data)
  },
  
  // 退出登录
  logout() {
    return apiClient.post('/auth/logout/')
  }
}
```

### Vue组件示例
```vue
<template>
  <div class="login-container">
    <form @submit.prevent="handleLogin">
      <input v-model="username" type="text" placeholder="用户名" required>
      <input v-model="password" type="password" placeholder="密码" required>
      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
    
    <div class="register-section">
      <h3>还没有账户？</h3>
      <form @submit.prevent="handleRegister">
        <input v-model="registerData.username" type="text" placeholder="用户名" required>
        <input v-model="registerData.password" type="password" placeholder="密码" required>
        <input v-model="registerData.confirm_password" type="password" placeholder="确认密码" required>
        <input v-model="registerData.nickname" type="text" placeholder="昵称">
        <input v-model="registerData.phone" type="tel" placeholder="手机号">
        <button type="submit" :disabled="registerLoading">
          {{ registerLoading ? '注册中...' : '注册' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { authService } from '@/services/authService'

export default {
  setup() {
    const username = ref('')
    const password = ref('')
    const loading = ref(false)
    
    const registerData = ref({
      username: '',
      password: '',
      confirm_password: '',
      nickname: '',
      phone: ''
    })
    const registerLoading = ref(false)
    
    const handleLogin = async () => {
      loading.value = true
      try {
        const response = await authService.login(username.value, password.value)
        if (response.success) {
          localStorage.setItem('access_token', response.data.token.access_token)
          localStorage.setItem('refresh_token', response.data.token.refresh_token)
          // 跳转到主页
          this.$router.push('/dashboard')
        }
      } catch (error) {
        console.error('登录失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const handleRegister = async () => {
      registerLoading.value = true
      try {
        const response = await authService.register(registerData.value)
        if (response.success) {
          localStorage.setItem('access_token', response.data.token.access_token)
          localStorage.setItem('refresh_token', response.data.token.refresh_token)
          // 跳转到主页
          this.$router.push('/dashboard')
        }
      } catch (error) {
        console.error('注册失败:', error)
      } finally {
        registerLoading.value = false
      }
    }
    
    return {
      username,
      password,
      loading,
      registerData,
      registerLoading,
      handleLogin,
      handleRegister
    }
  }
}
</script>
```

---

## 🚨 注意事项

### 安全建议
1. **HTTPS**: 生产环境必须使用HTTPS
2. **Token存储**: 前端应安全存储token，避免XSS攻击
3. **Token过期**: 实现自动刷新机制
4. **密码强度**: 建议要求用户设置强密码

### 错误处理
- `400`: 请求参数错误
- `401`: 未认证或token过期
- `403`: 权限不足
- `500`: 服务器内部错误

### 测试
使用提供的测试脚本验证API功能：
```bash
python test_login_api.py
```

---

## 📞 技术支持

如有问题，请检查：
1. Django服务器是否正常运行
2. 数据库连接是否正常
3. JWT配置是否完整
4. 前端请求格式是否正确

## ✅ 当前状态

**已完成的API**:
- ✅ 用户注册 (`/api/auth/register/`)
- ✅ 用户登录 (`/api/auth/login/`)
- ✅ 刷新Token (`/api/auth/refresh/`)
- ✅ 获取用户资料 (`/api/auth/profile/`)
- ✅ 更新用户资料 (`/api/auth/profile/update/`)
- ✅ 退出登录 (`/api/auth/logout/`)

**测试结果**: 注册和登录API已正常工作，返回正确的JWT令牌。 