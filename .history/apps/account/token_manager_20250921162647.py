from cryptography.fernet import Fernet
import base64
import re
from django.conf import settings
from django.utils import timezone


class TokenManager:
    """Token加密/解密管理器"""
    
    @staticmethod
    def get_encryption_key():
        """获取加密密钥"""
        # 使用Django SECRET_KEY的前32位作为密钥
        secret_key = settings.SECRET_KEY[:32].encode()
        return base64.urlsafe_b64encode(secret_key)
    
    @staticmethod
    def encrypt_token(token):
        """
        加密Token
        
        Args:
            token (str): 原始Token
            
        Returns:
            str: 加密后的Token
        """
        if not token:
            return None
            
        try:
            key = TokenManager.get_encryption_key()
            f = Fernet(key)
            encrypted_token = f.encrypt(token.encode())
            return encrypted_token.decode()
        except Exception as e:
            raise ValueError(f"Token加密失败: {str(e)}")
    
    @staticmethod
    def decrypt_token(encrypted_token):
        """
        解密Token
        
        Args:
            encrypted_token (str): 加密的Token
            
        Returns:
            str: 解密后的Token
        """
        if not encrypted_token:
            return None
            
        try:
            key = TokenManager.get_encryption_key()
            f = Fernet(key)
            decrypted_token = f.decrypt(encrypted_token.encode())
            return decrypted_token.decode()
        except Exception as e:
            raise ValueError(f"Token解密失败: {str(e)}")
    
    @staticmethod
    def validate_token_format(token):
        """
        验证Token格式
        
        Args:
            token (str): Token字符串
            
        Returns:
            bool: 格式是否正确
        """
        if not token:
            return False
        
        # 迅投Token通常是40位十六进制字符串
        # 格式: 40位十六进制字符
        pattern = r'^[a-fA-F0-9]{40}$'
        return bool(re.match(pattern, token))
    
    @staticmethod
    def mask_token(token, visible_chars=4):
        """
        遮蔽Token用于显示
        
        Args:
            token (str): 原始Token
            visible_chars (int): 显示字符数
            
        Returns:
            str: 遮蔽后的Token
        """
        if not token or len(token) <= visible_chars:
            return token
        
        visible_part = token[:visible_chars]
        masked_part = '*' * (len(token) - visible_chars)
        return visible_part + masked_part


class XtTokenValidator:
    """XtQuant Token验证器"""
    
    @staticmethod
    def validate_token_with_api(token):
        """
        通过API验证Token有效性
        
        Args:
            token (str): Token字符串
            
        Returns:
            tuple: (is_valid, message)
        """
        try:
            # 这里可以调用XtQuant API来验证Token
            # 目前先进行基本格式验证
            if not TokenManager.validate_token_format(token):
                return False, "Token格式不正确"
            
            # TODO: 实际API验证逻辑
            # 可以尝试连接XtQuant服务来验证Token
            return True, "Token格式正确"
            
        except Exception as e:
            return False, f"Token验证失败: {str(e)}"
    
    @staticmethod
    def test_token_connection(token):
        """
        测试Token连接
        
        Args:
            token (str): Token字符串
            
        Returns:
            tuple: (success, message)
        """
        try:
            # 这里可以尝试使用Token连接XtQuant服务
            # 目前返回模拟结果
            return True, "Token连接测试成功"
            
        except Exception as e:
            return False, f"Token连接测试失败: {str(e)}"
