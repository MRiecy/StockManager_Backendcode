"""
邮件验证码服务
作为短信服务的免费替代方案
"""
import os
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.cache import cache
import time

logger = logging.getLogger(__name__)


class EmailVerificationService:
    """邮件验证码服务"""
    
    def __init__(self):
        self.from_email = getattr(settings, 'EMAIL_HOST_USER', 'noreply@example.com')
        self.site_name = getattr(settings, 'SITE_NAME', '股票管理系统')
    
    def send_verification_code(self, email: str, code: str) -> Tuple[bool, str]:
        """
        发送邮件验证码
        
        Args:
            email: 邮箱地址
            code: 验证码
            
        Returns:
            (success, message): 发送结果和消息
        """
        try:
            # 检查发送频率
            can_send, remaining_time = self._check_rate_limit(email)
            if not can_send:
                return False, f"发送过于频繁，请等待 {remaining_time} 秒后重试"
            
            # 邮件主题
            subject = f'{self.site_name} - 验证码'
            
            # 邮件内容模板
            html_message = render_to_string('account/email/verification_code.html', {
                'code': code,
                'site_name': self.site_name,
                'expire_minutes': 5
            })
            
            # 纯文本内容
            plain_message = strip_tags(html_message)
            
            # 发送邮件
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=self.from_email,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            
            # 记录发送时间
            self._record_send(email)
            
            logger.info(f"邮件验证码发送成功: {email}")
            return True, "邮件验证码发送成功"
            
        except Exception as e:
            logger.error(f"邮件验证码发送失败: {email}, 错误: {str(e)}")
            return False, f"邮件发送失败: {str(e)}"
    
    def _check_rate_limit(self, email: str) -> Tuple[bool, int]:
        """检查发送频率限制"""
        cache_key = f"email_rate_limit:{email}"
        last_send_time = cache.get(cache_key)
        
        if not last_send_time:
            return True, 0
        
        current_time = time.time()
        time_diff = current_time - last_send_time
        
        # 2分钟内只能发送一次（邮件比短信慢，所以限制更宽松）
        if time_diff < 120:
            remaining = int(120 - time_diff)
            return False, remaining
        
        return True, 0
    
    def _record_send(self, email: str):
        """记录邮件发送时间"""
        cache_key = f"email_rate_limit:{email}"
        cache.set(cache_key, time.time(), 300)  # 缓存5分钟


class HybridVerificationService:
    """混合验证服务：优先使用邮件，备选短信"""
    
    def __init__(self):
        self.email_service = EmailVerificationService()
        self.sms_service = None
        
        # 尝试导入短信服务
        try:
            from .sms_service import SMSServiceFactory
            self.sms_service = SMSServiceFactory.create_service()
        except ImportError:
            logger.warning("短信服务未配置，将仅使用邮件服务")
    
    def send_verification_code(self, contact: str, code: str, contact_type: str = 'auto') -> Tuple[bool, str]:
        """
        发送验证码
        
        Args:
            contact: 联系方式（手机号或邮箱）
            code: 验证码
            contact_type: 联系方式类型 ('phone', 'email', 'auto')
            
        Returns:
            (success, message): 发送结果和消息
        """
        # 自动判断联系方式类型
        if contact_type == 'auto':
            if '@' in contact:
                contact_type = 'email'
            else:
                contact_type = 'phone'
        
        if contact_type == 'email':
            return self.email_service.send_verification_code(contact, code)
        elif contact_type == 'phone' and self.sms_service:
            return self.sms_service.send_sms(contact, code)
        else:
            return False, "不支持的联系方式或短信服务未配置"
    
    def get_service_info(self) -> Dict[str, str]:
        """获取服务信息"""
        info = {
            'primary_service': 'email',
            'email_enabled': True,
            'sms_enabled': self.sms_service is not None,
            'cost': '免费（邮件）',
            'fallback': '短信服务（收费）' if self.sms_service else '无'
        }
        return info


# 全局实例
email_service = EmailVerificationService()
hybrid_service = HybridVerificationService()


def send_verification_code_email(email: str, code: str) -> Tuple[bool, str]:
    """发送邮件验证码的统一接口"""
    return email_service.send_verification_code(email, code)


def send_verification_code_hybrid(contact: str, code: str, contact_type: str = 'auto') -> Tuple[bool, str]:
    """发送验证码的混合接口"""
    return hybrid_service.send_verification_code(contact, code, contact_type)


def get_verification_service_info() -> Dict[str, str]:
    """获取验证服务信息"""
    return hybrid_service.get_service_info() 