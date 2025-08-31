import time
import traceback
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import status

# 获取Django内置的User模型
User = get_user_model()


def create_tokens_for_user(user):
    """为用户创建JWT令牌"""
    try:
        refresh = RefreshToken()
        refresh['user_id'] = user.id
        refresh['username'] = user.username
        
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        return access_token, refresh_token
    except Exception as e:
        print(f"创建JWT令牌失败: {e}")
        raise e


# ==================== 认证函数 ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册 - 用户名+密码方式"""
    try:
        # 获取注册数据
        username = request.data.get('username')
        password = request.data.get('password')
        nickname = request.data.get('nickname', '')
        phone = request.data.get('phone', '')
        
        # 验证必填字段
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': '用户名已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 创建用户
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nickname,  # 使用first_name存储昵称
            email=phone,          # 使用email字段存储手机号
        )
        
        # 生成JWT令牌
        access_token, refresh_token = create_tokens_for_user(user)
        
        # 序列化用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'nickname': user.first_name,
            'phone': user.email,
            'created_at': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active
        }
        
        return JsonResponse({
            'success': True,
            'message': '注册成功',
            'data': {
                'user': user_data,
                'token': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """用户登录 - 用户名+密码方式"""
    try:
        # 获取登录数据
        username = request.data.get('username')
        password = request.data.get('password')
        
        # 验证必填字段
        if not username or not password:
            return JsonResponse({
                'success': False,
                'message': '用户名和密码不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证用户名和密码
        user = authenticate(username=username, password=password)
        if not user:
            return JsonResponse({
                'success': False,
                'message': '用户名或密码错误'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新登录时间
        user.last_login = timezone.now()
        user.save()
        
        # 生成JWT令牌
        access_token, refresh_token = create_tokens_for_user(user)
        
        # 序列化用户信息
        user_data = {
            'id': user.id,
            'username': user.username,
            'nickname': user.first_name,
            'phone': user.email,
            'created_at': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active
        }
        
        return JsonResponse({
            'success': True,
            'message': '登录成功',
            'data': {
                'user': user_data,
                'token': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """获取用户资料"""
    try:
        user = request.user
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'nickname': user.first_name,
            'phone': user.email,
            'created_at': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active
        }
        
        return JsonResponse({
            'success': True,
            'message': '获取用户资料成功',
            'data': user_data
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'获取用户资料失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """更新用户资料"""
    try:
        user = request.user
        data = request.data
        
        # 允许更新的字段
        if 'nickname' in data:
            user.first_name = data['nickname']
        if 'phone' in data:
            user.email = data['phone']
        
        user.save()
        
        user_data = {
            'id': user.id,
            'username': user.username,
            'nickname': user.first_name,
            'phone': user.email,
            'created_at': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active
        }
        
        return JsonResponse({
            'success': True,
            'message': '更新用户资料成功',
            'data': user_data
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'更新用户资料失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    """用户退出登录"""
    try:
        # 获取Authorization头
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # 这里可以添加token黑名单逻辑
            # 目前只是简单返回成功
            return JsonResponse({
                'success': True,
                'message': '退出登录成功'
            })
        else:
            return JsonResponse({
                'success': True,
                'message': '退出登录成功'
            })
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'退出登录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """刷新访问令牌"""
    try:
        # 获取Authorization头
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'message': '无效的Authorization头'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        refresh_token_str = auth_header.split(' ')[1]
        
        # 验证refresh token
        try:
            refresh = RefreshToken(refresh_token_str)
            user_id = refresh.payload.get('user_id')
            username = refresh.payload.get('username')
            
            # 获取用户
            user = User.objects.get(id=user_id)
            
            # 生成新的access token
            new_access_token = str(refresh.access_token)
            
            return JsonResponse({
                'success': True,
                'message': '刷新令牌成功',
                'data': {
                    'access_token': new_access_token,
                    'token_type': 'Bearer',
                    'expires_in': 3600
                }
            })
            
        except TokenError as e:
            return JsonResponse({
                'success': False,
                'message': '无效的refresh token'
            }, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': '用户不存在'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'刷新令牌失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 