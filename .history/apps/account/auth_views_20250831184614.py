import time
import traceback
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import json

User = get_user_model()  # 使用Django的标准User模型
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    LoginResponseSerializer, ProfileResponseSerializer
)


def create_tokens_for_user(user):
    """为用户创建JWT令牌"""
    refresh = RefreshToken()
    refresh['user_id'] = user.id  # 使用标准的id字段
    refresh['username'] = user.username
    
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)
    
    return access_token, refresh_token


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册 - 简化版"""
    try:
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        with transaction.atomic():
            # 创建用户
            user = User.objects.create(
                username=data['username'],
                password=data['password'],  # 模型会自动加密
                nickname=data.get('nickname', ''),
                phone=data.get('phone', ''),
                is_new_user=True
            )
            
            # 生成JWT令牌
            access_token, refresh_token = create_tokens_for_user(user)
            
            # 保存令牌到数据库
            UserToken.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600
            )
            
            # 序列化用户信息
            user_data = UserSerializer(user).data
            token_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 3600
            }
            
            return JsonResponse({
                'success': True,
                'message': '注册成功',
                'data': {
                    'user': user_data,
                    'token': token_data
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
    """用户登录 - 支持用户名或手机号"""
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        with transaction.atomic():
            # 更新登录时间
            user.last_login = timezone.now()
            user.is_new_user = False
            user.save()
            
            # 生成JWT令牌
            access_token, refresh_token = create_tokens_for_user(user)
            
            # 保存令牌到数据库
            UserToken.objects.filter(user=user).update(is_active=False)
            UserToken.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600
            )
            
            # 序列化用户信息
            user_data = UserSerializer(user).data
            token_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': 3600
            }
            
            return JsonResponse({
                'success': True,
                'message': '登录成功',
                'data': {
                    'user': user_data,
                    'token': token_data
                }
            })
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """刷新访问令牌"""
    try:
        # 从请求头获取refresh_token
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({
                'success': False,
                'message': '缺少Authorization头'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh_token = auth_header.split(' ')[1]
        
        # 验证refresh_token
        try:
            refresh = RefreshToken(refresh_token)
            user_id = refresh.payload.get('user_id')  # 使用user_id字段
            
            # 查找用户
            user = User.objects.get(id=user_id)  # 使用标准的id字段
            
            # 生成新的access_token
            new_access_token = str(refresh.access_token)
            
            # 更新数据库中的令牌
            user_token = UserToken.objects.filter(
                user=user,
                refresh_token=refresh_token,
                is_active=True
            ).first()
            
            if user_token:
                user_token.access_token = new_access_token
                user_token.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Token刷新成功',
                'data': {
                    'access_token': new_access_token,
                    'expires_in': 3600
                }
            })
            
        except TokenError:
            return JsonResponse({
                'success': False,
                'message': 'Refresh token无效'
            }, status=status.HTTP_401_UNAUTHORIZED)
            
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'刷新Token失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """退出登录"""
    try:
        # 获取当前用户的令牌并标记为无效
        user = request.user
        UserToken.objects.filter(user=user).update(is_active=False)
        
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """获取用户资料"""
    try:
        user = request.user
        user_data = UserSerializer(user).data
        
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
        allowed_fields = ['nickname', 'avatar', 'phone']
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        user_data = UserSerializer(user).data
        
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