"""
Token管理工具类
用于加密和解密用户Token
"""
from cryptography.fernet import Fernet
import base64
from django.conf import settings
import re


class TokenManager:
    """Token加密解密管理器"""
    
    @staticmethod
    def encrypt_token(token):
        """
        加密Token
        
        Args:
            token (str): 原始Token
            
        Returns:
            str: 加密后的Token
        """
        try:
            # 使用Fernet加密Token
            key = settings.SECRET_KEY[:32].encode()
            f = Fernet(base64.urlsafe_b64encode(key))
            return f.encrypt(token.encode()).decode()
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
        try:
            # 解密Token
            key = settings.SECRET_KEY[:32].encode()
            f = Fernet(base64.urlsafe_b64encode(key))
            return f.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            raise ValueError(f"Token解密失败: {str(e)}")
    
    @staticmethod
    def validate_xt_token_format(token):
        """
        验证XtQuant Token格式
        
        Args:
            token (str): Token字符串
            
        Returns:
            bool: 格式是否正确
        """
        if not token or not isinstance(token, str):
            return False
        
        # XtQuant Token通常是40位十六进制字符串
        # 或者包含字母数字的较长字符串
        if len(token) < 20 or len(token) > 100:
            return False
        
        # 检查是否包含有效字符（字母、数字、可能包含特殊字符）
        if not re.match(r'^[a-zA-Z0-9\-_]+$', token):
            return False
        
        return True
    
    @staticmethod
    def test_xt_token_validity(token):
        """
        测试Token有效性（可选实现）
        
        Args:
            token (str): Token字符串
            
        Returns:
            bool: Token是否有效
        """
        # 这里可以添加实际的XtQuant API调用来验证Token
        # 目前只做格式验证
        return TokenManager.validate_xt_token_format(token)
