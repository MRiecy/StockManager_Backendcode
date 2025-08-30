import time
import traceback
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User, VerificationCode, UserToken
from .serializers import (
    VerificationCodeSerializer, LoginSerializer, UserSerializer,
    SendCodeResponseSerializer, LoginResponseSerializer, ProfileResponseSerializer
)
from rest_framework import status


@api_view(['POST'])
def send_verification_code(request):
    """发送手机验证码"""
    try:
        serializer = VerificationCodeSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        
        # 检查是否在冷却时间内
        recent_code = VerificationCode.objects.filter(
            phone=phone,
            created_at__gte=timezone.now() - timezone.timedelta(minutes=1)
        ).first()
        
        if recent_code:
            return JsonResponse({
                'success': False,
                'message': '请等待1分钟后再发送验证码'
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # 生成验证码
        verification_code = VerificationCode.generate_code(phone)
        
        # 这里应该调用短信服务发送验证码
        # 目前模拟发送成功
        print(f"向手机号 {phone} 发送验证码: {verification_code.code}")
        
        return JsonResponse({
            'success': True,
            'message': '验证码已发送',
            'data': {
                'expire_time': 300,      # 5分钟有效期
                'can_resend_time': 60    # 1分钟后可重发
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'发送验证码失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def login_with_phone(request):
    """手机号登录/注册"""
    try:
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return JsonResponse({
                'success': False,
                'message': '参数错误',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']
        
        # 验证验证码
        verification_code = VerificationCode.objects.filter(
            phone=phone,
            code=code,
            is_used=False,
            expire_at__gt=timezone.now()
        ).order_by('-created_at').first()
        
        if not verification_code:
            return JsonResponse({
                'success': False,
                'message': '验证码无效或已过期'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            # 标记验证码为已使用
            verification_code.is_used = True
            verification_code.save()
            
            # 查找或创建用户
            user, created = User.objects.get_or_create(
                phone=phone,
                defaults={
                    'is_new_user': True,
                    'last_login': timezone.now()
                }
            )
            
            if not created:
                # 更新登录时间
                user.last_login = timezone.now()
                user.is_new_user = False
                user.save()
            
            # 生成JWT令牌
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
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
            user_id = refresh.payload.get('user_id')
            
            # 查找用户
            user = User.objects.get(id=user_id)
            
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
def get_current_user(request):
    """获取当前用户信息"""
    try:
        user = request.user
        
        # 模拟用户权限
        permissions = ['read', 'write']
        
        user_data = {
            'user_id': user.user_id,
            'phone': user.phone,
            'nickname': user.nickname,
            'avatar': user.avatar or '',
            'created_at': user.created_at,
            'last_login': user.last_login,
            'account_status': user.account_status,
            'permissions': permissions
        }
        
        return JsonResponse({
            'success': True,
            'data': user_data
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'获取用户信息失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_region_data(request):
    """获取地区分布数据"""
    try:
        # 这里应该从数据库或外部API获取真实的地区分布数据
        # 目前返回模拟数据
        region_data = [
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
            },
            {
                "region": "北京",
                "totalAssets": 570000,
                "returnRate": "9.2%",
                "maxDrawdown": 20.0
            }
        ]
        
        return JsonResponse({
            'success': True,
            'data': region_data
        })
        
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'获取地区数据失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 