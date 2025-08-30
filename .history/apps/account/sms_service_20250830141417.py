"""
短信服务模块
支持阿里云和腾讯云短信服务
"""
import os
import json
import logging
from typing import Dict, Optional, Tuple
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class BaseSMSService:
    """短信服务基类"""
    
    def __init__(self):
        self.provider = getattr(settings, 'SMS_PROVIDER', 'aliyun')
    
    def send_sms(self, phone: str, code: str) -> Tuple[bool, str]:
        """
        发送短信验证码
        
        Args:
            phone: 手机号
            code: 验证码
            
        Returns:
            (success, message): 发送结果和消息
        """
        raise NotImplementedError
    
    def get_balance(self) -> Optional[float]:
        """获取账户余额"""
        raise NotImplementedError


class AliyunSMSService(BaseSMSService):
    """阿里云短信服务"""
    
    def __init__(self):
        super().__init__()
        try:
            from aliyunsdkcore.client import AcsClient
            from aliyunsdkcore.request import CommonRequest
            
            self.client = AcsClient(
                getattr(settings, 'ALIYUN_ACCESS_KEY_ID', ''),
                getattr(settings, 'ALIYUN_ACCESS_KEY_SECRET', ''),
                'cn-hangzhou'
            )
            self.sign_name = getattr(settings, 'ALIYUN_SMS_SIGN_NAME', '')
            self.template_code = getattr(settings, 'ALIYUN_SMS_TEMPLATE_CODE', '')
            
        except ImportError:
            logger.error("阿里云SDK未安装，请运行: pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi")
            self.client = None
    
    def send_sms(self, phone: str, code: str) -> Tuple[bool, str]:
        """发送阿里云短信"""
        if not self.client:
            return False, "阿里云SDK未安装"
        
        try:
            from aliyunsdkcore.request import CommonRequest
            
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.aliyuncs.com')
            request.set_method('POST')
            request.set_protocol_type('https')
            request.set_version('2017-05-25')
            request.set_action_name('SendSms')
            
            request.add_query_param('RegionId', "cn-hangzhou")
            request.add_query_param('PhoneNumbers', phone)
            request.add_query_param('SignName', self.sign_name)
            request.add_query_param('TemplateCode', self.template_code)
            request.add_query_param('TemplateParam', json.dumps({'code': code}))
            
            response = self.client.do_action_with_exception(request)
            response_json = json.loads(response)
            
            if response_json.get('Code') == 'OK':
                logger.info(f"阿里云短信发送成功: {phone}")
                return True, "短信发送成功"
            else:
                error_msg = response_json.get('Message', '未知错误')
                logger.error(f"阿里云短信发送失败: {phone}, 错误: {error_msg}")
                return False, f"短信发送失败: {error_msg}"
                
        except Exception as e:
            logger.error(f"阿里云短信发送异常: {phone}, 错误: {str(e)}")
            return False, f"短信发送异常: {str(e)}"
    
    def get_balance(self) -> Optional[float]:
        """获取阿里云账户余额"""
        try:
            from aliyunsdkcore.request import CommonRequest
            
            request = CommonRequest()
            request.set_accept_format('json')
            request.set_domain('dysmsapi.aliyuncs.com')
            request.set_method('POST')
            request.set_protocol_type('https')
            request.set_version('2017-05-25')
            request.set_action_name('QuerySmsTemplate')
            
            response = self.client.do_action_with_exception(request)
            # 注意：阿里云没有直接的余额查询接口，这里返回None
            return None
            
        except Exception as e:
            logger.error(f"获取阿里云余额失败: {str(e)}")
            return None


class TencentSMSService(BaseSMSService):
    """腾讯云短信服务"""
    
    def __init__(self):
        super().__init__()
        try:
            from tencentcloud.common import credential
            from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
            from tencentcloud.sms.v20210111 import sms_client, models
            
            self.cred = credential.Credential(
                getattr(settings, 'TENCENT_SECRET_ID', ''),
                getattr(settings, 'TENCENT_SECRET_KEY', '')
            )
            self.client = sms_client.SmsClient(self.cred, "ap-guangzhou")
            self.sdk_app_id = getattr(settings, 'TENCENT_SMS_SDK_APP_ID', '')
            self.sign_name = getattr(settings, 'TENCENT_SMS_SIGN_NAME', '')
            self.template_id = getattr(settings, 'TENCENT_SMS_TEMPLATE_ID', '')
            
        except ImportError:
            logger.error("腾讯云SDK未安装，请运行: pip install tencentcloud-sdk-python")
            self.client = None
    
    def send_sms(self, phone: str, code: str) -> Tuple[bool, str]:
        """发送腾讯云短信"""
        if not self.client:
            return False, "腾讯云SDK未安装"
        
        try:
            from tencentcloud.sms.v20210111 import models
            
            req = models.SendSmsRequest()
            req.SmsSdkAppId = self.sdk_app_id
            req.SignName = self.sign_name
            req.TemplateId = self.template_id
            req.TemplateParamSet = [code]
            req.PhoneNumberSet = [f"+86{phone}"]
            
            resp = self.client.SendSms(req)
            
            if resp.SendStatusSet[0].Code == "Ok":
                logger.info(f"腾讯云短信发送成功: {phone}")
                return True, "短信发送成功"
            else:
                error_msg = resp.SendStatusSet[0].Message
                logger.error(f"腾讯云短信发送失败: {phone}, 错误: {error_msg}")
                return False, f"短信发送失败: {error_msg}"
                
        except Exception as e:
            logger.error(f"腾讯云短信发送异常: {phone}, 错误: {str(e)}")
            return False, f"短信发送异常: {str(e)}"
    
    def get_balance(self) -> Optional[float]:
        """获取腾讯云账户余额"""
        try:
            from tencentcloud.sms.v20210111 import models
            
            req = models.DescribeSmsTemplateListRequest()
            req.International = 0
            req.TemplateIdSet = [self.template_id]
            
            resp = self.client.DescribeSmsTemplateList(req)
            # 注意：腾讯云没有直接的余额查询接口，这里返回None
            return None
            
        except Exception as e:
            logger.error(f"获取腾讯云余额失败: {str(e)}")
            return None


class MockSMSService(BaseSMSService):
    """模拟短信服务（开发环境使用）"""
    
    def send_sms(self, phone: str, code: str) -> Tuple[bool, str]:
        """模拟发送短信"""
        logger.info(f"模拟短信发送: {phone} -> {code}")
        print(f"📱 模拟短信发送到 {phone}: 验证码 {code}")
        return True, "模拟短信发送成功"
    
    def get_balance(self) -> Optional[float]:
        """模拟余额"""
        return 999.99


class SMSServiceFactory:
    """短信服务工厂类"""
    
    @staticmethod
    def create_service() -> BaseSMSService:
        """创建短信服务实例"""
        provider = getattr(settings, 'SMS_PROVIDER', 'mock').lower()
        
        if provider == 'aliyun':
            return AliyunSMSService()
        elif provider == 'tencent':
            return TencentSMSService()
        else:
            return MockSMSService()


class SMSRateLimiter:
    """短信发送频率限制器"""
    
    @staticmethod
    def can_send(phone: str) -> Tuple[bool, int]:
        """
        检查是否可以发送短信
        
        Returns:
            (can_send, remaining_time): 是否可以发送和剩余等待时间
        """
        cache_key = f"sms_rate_limit:{phone}"
        last_send_time = cache.get(cache_key)
        
        if not last_send_time:
            return True, 0
        
        import time
        current_time = time.time()
        time_diff = current_time - last_send_time
        
        # 1分钟内只能发送一次
        if time_diff < 60:
            remaining = int(60 - time_diff)
            return False, remaining
        
        return True, 0
    
    @staticmethod
    def record_send(phone: str):
        """记录短信发送时间"""
        cache_key = f"sms_rate_limit:{phone}"
        import time
        cache.set(cache_key, time.time(), 120)  # 缓存2分钟


def send_verification_code(phone: str, code: str) -> Tuple[bool, str]:
    """
    发送验证码的统一接口
    
    Args:
        phone: 手机号
        code: 验证码
        
    Returns:
        (success, message): 发送结果和消息
    """
    # 检查发送频率
    can_send, remaining_time = SMSRateLimiter.can_send(phone)
    if not can_send:
        return False, f"发送过于频繁，请等待 {remaining_time} 秒后重试"
    
    # 创建短信服务实例
    sms_service = SMSServiceFactory.create_service()
    
    # 发送短信
    success, message = sms_service.send_sms(phone, code)
    
    if success:
        # 记录发送时间
        SMSRateLimiter.record_send(phone)
        logger.info(f"验证码发送成功: {phone}")
    else:
        logger.error(f"验证码发送失败: {phone}, 错误: {message}")
    
    return success, message


def get_sms_balance() -> Optional[float]:
    """获取短信服务账户余额"""
    sms_service = SMSServiceFactory.create_service()
    return sms_service.get_balance()


def get_sms_provider_info() -> Dict[str, str]:
    """获取短信服务提供商信息"""
    provider = getattr(settings, 'SMS_PROVIDER', 'mock').lower()
    
    if provider == 'aliyun':
        return {
            'provider': 'aliyun',
            'name': '阿里云短信服务',
            'sign_name': getattr(settings, 'ALIYUN_SMS_SIGN_NAME', ''),
            'template_code': getattr(settings, 'ALIYUN_SMS_TEMPLATE_CODE', '')
        }
    elif provider == 'tencent':
        return {
            'provider': 'tencent',
            'name': '腾讯云短信服务',
            'sign_name': getattr(settings, 'TENCENT_SMS_SIGN_NAME', ''),
            'template_id': getattr(settings, 'TENCENT_SMS_TEMPLATE_ID', '')
        }
    else:
        return {
            'provider': 'mock',
            'name': '模拟短信服务（开发环境）',
            'sign_name': 'N/A',
            'template_code': 'N/A'
        } 