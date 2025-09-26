# 📋 用户Token管理需求文档

## 🎯 项目背景

当前StockManager后端系统使用全局统一的XtQuant Token配置，所有用户共享同一个Token。为了提升用户体验和数据安全性，需要实现用户级别的Token管理，让每个用户在注册时输入自己的迅投平台Token。

## 📊 现状分析

### 当前实现
- **Token配置**: 全局统一配置在 `settings.py` 中
- **Token来源**: 环境变量 `XT_TOKEN` 或硬编码默认值
- **用户注册**: 仅收集用户名、密码、昵称、手机号
- **Token使用**: 所有用户共享同一个Token

### 存在的问题
1. **安全性**: 所有用户共享Token，存在安全风险
2. **用户体验**: 用户需要手动修改后端配置
3. **数据隔离**: 无法实现用户级别的数据隔离
4. **扩展性**: 难以支持多用户独立使用

## 🎯 需求目标

### 核心需求
1. **用户注册时输入Token**: 用户在注册时提供自己的迅投平台Token
2. **密码确认**: 用户需要输入两次密码进行确认
3. **自动配置**: 后端自动使用用户提供的Token，无需手动修改配置
4. **用户隔离**: 每个用户使用自己的Token，实现数据隔离

### 功能需求

#### 1. 注册流程增强
- **必填字段**:
  - `username`: 用户名（账号）
  - `password`: 密码
  - `confirm_password`: 确认密码
  - `xt_token`: 迅投平台Token
-
#### 2. Token验证
- **格式验证**: 验证Token格式是否正确
- **有效性验证**: 验证Token是否有效
- **唯一性**: 确保Token未被其他用户使用

#### 3. 用户数据模型扩展
- **新增字段**: `xt_token` 字段存储用户Token
- **加密存储**: Token需要加密存储，保护用户隐私
- **关联关系**: 用户与Token的一对一关系

#### 4. API接口调整
- **注册接口**: 修改注册接口支持Token输入
- **登录接口**: 登录时自动加载用户Token
- **Token管理**: 提供Token更新、验证等接口

## 🔧 技术实现方案

### 1. 数据模型设计

#### 用户模型扩展
```python
class User(AbstractUser):
    # 现有字段
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=30, blank=True)  # 昵称
    email = models.EmailField(blank=True)  # 手机号
    
    # 新增字段
    xt_token = models.CharField(max_length=100, unique=True, verbose_name="迅投Token")
    token_encrypted = models.BooleanField(default=True, verbose_name="Token已加密")
    token_created_at = models.DateTimeField(auto_now_add=True, verbose_name="Token创建时间")
    token_last_used = models.DateTimeField(null=True, blank=True, verbose_name="Token最后使用时间")
```

#### Token加密存储
```python
from cryptography.fernet import Fernet
import base64

class TokenManager:
    @staticmethod
    def encrypt_token(token):
        # 使用Fernet加密Token
        key = settings.SECRET_KEY[:32].encode()
        f = Fernet(base64.urlsafe_b64encode(key))
        return f.encrypt(token.encode()).decode()
    
    @staticmethod
    def decrypt_token(encrypted_token):
        # 解密Token
        key = settings.SECRET_KEY[:32].encode()
        f = Fernet(base64.urlsafe_b64encode(key))
        return f.decrypt(encrypted_token.encode()).decode()
```

### 2. API接口设计

#### 注册接口增强
```python
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册 - 支持Token输入"""
    try:
        # 获取注册数据
        username = request.data.get('username')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        xt_token = request.data.get('xt_token')
        nickname = request.data.get('nickname', '')
        phone = request.data.get('phone', '')
        
        # 验证必填字段
        if not all([username, password, confirm_password, xt_token]):
            return JsonResponse({
                'success': False,
                'message': '用户名、密码、确认密码和Token不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证密码一致性
        if password != confirm_password:
            return JsonResponse({
                'success': False,
                'message': '两次输入的密码不一致'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证Token格式
        if not validate_xt_token_format(xt_token):
            return JsonResponse({
                'success': False,
                'message': 'Token格式不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名和Token是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(xt_token=TokenManager.encrypt_token(xt_token)).exists():
            return JsonResponse({
                'success': False,
                'message': 'Token已被其他用户使用'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nickname,
            email=phone,
            xt_token=TokenManager.encrypt_token(xt_token)
        )
        
        # 生成JWT令牌
        access_token, refresh_token = create_tokens_for_user(user)
        
        return JsonResponse({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'nickname': user.first_name,
                    'phone': user.email,
                    'created_at': user.date_joined,
                    'is_active': user.is_active
                },
                'token': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

#### Token管理接口
```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_xt_token(request):
    """更新用户Token"""
    try:
        user = request.user
        new_token = request.data.get('xt_token')
        
        if not new_token:
            return JsonResponse({
                'success': False,
                'message': 'Token不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证Token格式
        if not validate_xt_token_format(new_token):
            return JsonResponse({
                'success': False,
                'message': 'Token格式不正确'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查Token是否已被其他用户使用
        encrypted_token = TokenManager.encrypt_token(new_token)
        if User.objects.filter(xt_token=encrypted_token).exclude(id=user.id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Token已被其他用户使用'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新Token
        user.xt_token = encrypted_token
        user.token_last_used = timezone.now()
        user.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Token更新成功'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Token更新失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_xt_token(request):
    """验证用户Token有效性"""
    try:
        user = request.user
        decrypted_token = TokenManager.decrypt_token(user.xt_token)
        
        # 调用XtQuant API验证Token
        is_valid = test_xt_token_validity(decrypted_token)
        
        return JsonResponse({
            'success': True,
            'data': {
                'is_valid': is_valid,
                'message': 'Token有效' if is_valid else 'Token无效或已过期'
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Token验证失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### 3. XtQuant集成调整

#### 用户级别Token使用
```python
def get_user_xt_token(user):
    """获取用户解密后的Token"""
    if hasattr(user, 'xt_token') and user.xt_token:
        return TokenManager.decrypt_token(user.xt_token)
    return None

def init_xtdatacenter_for_user(user):
    """为用户初始化XtQuant连接"""
    user_token = get_user_xt_token(user)
    if not user_token:
        raise ValueError("用户Token不存在")
    
    # 设置用户Token
    xtdc.set_token(user_token)
    # 使用全局VIP站点配置
    xtdc.set_allow_optmize_address(settings.XT_CONFIG['ADDR_LIST'])
    
    return True
```

#### API接口调整
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_account_info(request):
    """获取账户信息 - 使用用户Token"""
    try:
        user = request.user
        
        # 使用用户Token初始化连接
        init_xtdatacenter_for_user(user)
        
        # 获取账户信息
        accounts = xt_trader.query_account_infos()
        
        # 更新Token使用时间
        user.token_last_used = timezone.now()
        user.save()
        
        return JsonResponse({
            'accounts': accounts,
            'source': 'XtQuant用户Token',
            'data_available': True
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'获取账户信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

## 📋 实施计划

### 阶段1: 数据模型设计 (1-2天)
- [ ] 设计用户模型扩展
- [ ] 实现Token加密/解密功能
- [ ] 创建数据库迁移文件
- [ ] 测试数据模型

### 阶段2: API接口开发 (2-3天)
- [ ] 修改注册接口支持Token输入
- [ ] 实现Token验证功能
- [ ] 开发Token管理接口
- [ ] 编写API测试用例

### 阶段3: XtQuant集成 (2-3天)
- [ ] 调整XtQuant连接逻辑
- [ ] 实现用户级别Token使用
- [ ] 修改现有API接口
- [ ] 测试数据获取功能

### 阶段4: 测试和优化 (1-2天)
- [ ] 完整功能测试
- [ ] 性能优化
- [ ] 安全测试
- [ ] 文档更新

## 🔒 安全考虑

### 1. Token安全
- **加密存储**: 使用Fernet加密算法存储Token
- **传输安全**: API接口使用HTTPS传输
- **访问控制**: Token只能被所属用户访问

### 2. 数据隔离
- **用户隔离**: 每个用户只能访问自己的数据
- **Token隔离**: 用户Token不能重复使用
- **权限控制**: 严格的用户权限验证

### 3. 错误处理
- **Token验证**: 完善的Token格式和有效性验证
- **异常处理**: 详细的错误信息和日志记录
- **降级方案**: Token失效时的处理机制

## 📊 预期效果

### 用户体验提升
- **简化配置**: 用户无需手动修改后端配置
- **快速注册**: 一次注册完成所有配置
- **数据安全**: 用户数据完全隔离

### 系统架构优化
- **多用户支持**: 支持多个用户独立使用
- **扩展性**: 易于扩展更多用户功能
- **维护性**: 降低系统维护复杂度

### 安全性增强
- **Token隔离**: 每个用户使用独立Token
- **数据保护**: 用户数据完全隔离
- **访问控制**: 严格的权限管理

## 🚀 后续扩展

### 功能扩展
- **Token自动刷新**: 支持Token自动续期
- **多Token支持**: 支持用户配置多个Token
- **Token使用统计**: 提供Token使用情况统计

### 管理功能
- **用户管理**: 管理员查看用户Token状态
- **Token监控**: 监控Token使用情况
- **异常告警**: Token异常时自动告警

---

**文档版本**: v1.0  
**创建日期**: 2025-01-25  
**最后更新**: 2025-01-25  
**负责人**: 开发团队
