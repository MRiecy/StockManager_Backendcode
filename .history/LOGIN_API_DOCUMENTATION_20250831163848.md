# 🔐 登录API文档

## 📋 概述

本文档描述了股票管理系统后端的登录认证API接口。系统使用手机号+验证码的方式进行用户认证，支持JWT令牌管理。

## 🚀 API端点

### 基础信息
- **服务器地址**: `http://localhost:8000`
- **API前缀**: `/api`
- **认证方式**: JWT Bearer Token

---

## 📱 1. 发送验证码

### 接口信息
- **URL**: `/api/auth/send-code/`
- **方法**: `POST`
- **描述**: 向指定手机号发送验证码

### 请求参数
```json
{
    "phone": "13800138000"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "验证码已发送",
    "data": {
        "expire_time": 300,      // 验证码有效期（秒）
        "can_resend_time": 60    // 可重发时间（秒）
    }
}
```

### 错误响应
```json
{
    "success": false,
    "message": "发送验证码失败",
    "errors": {
        "phone": ["请输入有效的手机号"]
    }
}
```

---

## 🔑 2. 用户登录

### 接口信息
- **URL**: `/api/auth/login/`
- **方法**: `POST`
- **描述**: 使用手机号和验证码进行登录/注册

### 请求参数
```json
{
    "phone": "13800138000",
    "code": "123456"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "user": {
            "user_id": "user_123456",
            "phone": "13800138000",
            "nickname": "用户昵称",
            "avatar": "头像URL",
            "created_at": "2024-01-01T00:00:00Z",
            "last_login": "2024-01-01T12:00:00Z",
            "account_status": "active"
        },
        "token": {
            "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
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
    "message": "验证码无效或已过期"
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
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
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
        "user_id": "user_123456",
        "phone": "13800138000",
        "nickname": "用户昵称",
        "avatar": "头像URL",
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z",
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
    "avatar": "新头像URL"
}
```

### 响应格式
```json
{
    "success": true,
    "message": "更新用户资料成功",
    "data": {
        "user_id": "user_123456",
        "phone": "13800138000",
        "nickname": "新昵称",
        "avatar": "新头像URL",
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-01T12:00:00Z",
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
  // 发送验证码
  sendVerificationCode(phone) {
    return apiClient.post('/auth/send-code/', { phone })
  },
  
  // 登录
  login(phone, code) {
    return apiClient.post('/auth/login/', { phone, code })
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
      <input v-model="phone" type="tel" placeholder="手机号" required>
      <div class="code-input">
        <input v-model="code" type="text" placeholder="验证码" required>
        <button type="button" @click="sendCode" :disabled="countdown > 0">
          {{ countdown > 0 ? `${countdown}s` : '发送验证码' }}
        </button>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>
    </form>
  </div>
</template>

<script>
import { ref } from 'vue'
import { authService } from '@/services/authService'

export default {
  setup() {
    const phone = ref('')
    const code = ref('')
    const loading = ref(false)
    const countdown = ref(0)
    
    const sendCode = async () => {
      try {
        await authService.sendVerificationCode(phone.value)
        countdown.value = 60
        const timer = setInterval(() => {
          countdown.value--
          if (countdown.value <= 0) {
            clearInterval(timer)
          }
        }, 1000)
      } catch (error) {
        console.error('发送验证码失败:', error)
      }
    }
    
    const handleLogin = async () => {
      loading.value = true
      try {
        const response = await authService.login(phone.value, code.value)
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
    
    return {
      phone,
      code,
      loading,
      countdown,
      sendCode,
      handleLogin
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
4. **验证码**: 限制验证码发送频率，防止恶意攻击

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
3. 短信服务配置是否正确
4. JWT配置是否完整 