"""
Token登录认证模块
实现前端Token登录功能，配置Token并连接迅投
"""
import logging
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from apps.utils.xt_trader import get_xt_trader_connection
from apps.utils.token_manager import get_xt_token, set_xt_token

logger = logging.getLogger(__name__)


def verify_xt_connection(token):
    """
    验证迅投连接
    
    使用提供的Token尝试连接迅投系统，验证Token的有效性
    通过测试xtdatacenter和xt_trader两种连接方式来验证
    
    参数:
        token: 要验证的Token
    
    返回:
        dict: {
            'success': bool,  # 是否连接成功
            'message': str,   # 连接结果消息
            'error_code': str # 错误代码（可选）
        }
    """
    # 保存原始Token，确保在所有情况下都能恢复
    original_token = settings.XT_CONFIG.get('TOKEN', '')
    
    try:
        logger.info('开始验证迅投连接...')
        
        # 临时更新Token到settings（用于本次连接测试）
        settings.XT_CONFIG['TOKEN'] = token
        
        try:
            # 方法1: 测试xtdatacenter连接（主要验证方式）
            from xtquant import xtdatacenter as xtdc
            
            # 设置Token
            xtdc.set_token(token)
            # 设置连接池地址
            xtdc.set_allow_optmize_address(settings.XT_CONFIG['ADDR_LIST'])
            
            # 尝试初始化（不阻塞，只验证连接）
            try:
                xtdc.init(False)
                logger.info('xtdatacenter初始化成功')
                
                # 尝试获取服务器状态来验证连接
                from xtquant import xtdata
                servers = xtdata.get_quote_server_status()
                
                # 检查服务器状态
                if servers:
                    # 检查是否有可用的服务器
                    has_valid_server = False
                    for server, status in servers.items():
                        status_str = str(status)
                        if '已连接' in status_str or 'connected' in status_str.lower():
                            has_valid_server = True
                            break
                        # 如果状态不是"用户已过期"或"expired"，也认为可能有效
                        if '过期' not in status_str and 'expired' not in status_str.lower():
                            has_valid_server = True
                            break
                    
                    if has_valid_server:
                        logger.info('迅投连接验证成功（通过xtdatacenter）')
                        # 恢复原始Token（如果连接成功，会在token_login中更新）
                        settings.XT_CONFIG['TOKEN'] = original_token
                        return {
                            'success': True,
                            'message': '连接成功'
                        }
                    else:
                        # 所有服务器都显示过期或无效
                        logger.warning('迅投连接验证失败：所有服务器状态异常')
                        settings.XT_CONFIG['TOKEN'] = original_token
                        return {
                            'success': False,
                            'message': 'Token无效或已过期',
                            'error_code': 'TOKEN_EXPIRED'
                        }
                else:
                    # 无法获取服务器状态，尝试使用xt_trader验证
                    logger.info('无法获取服务器状态，尝试使用xt_trader验证')
                    result = verify_with_xt_trader(token, original_token)
                    # verify_with_xt_trader内部会恢复Token，这里不需要再次恢复
                    return result
                    
            except ConnectionError as e:
                # 连接错误，通常是Token问题
                error_msg = str(e)
                logger.warning(f'xtdatacenter连接失败: {error_msg}')
                settings.XT_CONFIG['TOKEN'] = original_token
                
                if '过期' in error_msg or 'expired' in error_msg.lower():
                    return {
                        'success': False,
                        'message': 'Token无效或已过期',
                        'error_code': 'TOKEN_EXPIRED'
                    }
                else:
                    return {
                        'success': False,
                        'message': '无法连接到迅投服务，请检查网络或服务状态',
                        'error_code': 'SERVICE_UNAVAILABLE'
                    }
            
            except Exception as e:
                # 其他异常，尝试使用xt_trader验证
                logger.warning(f'xtdatacenter验证异常: {str(e)}，尝试使用xt_trader验证')
                result = verify_with_xt_trader(token, original_token)
                # verify_with_xt_trader内部会恢复Token
                return result
                
        except Exception as e:
            logger.error(f'迅投连接验证异常: {str(e)}', exc_info=True)
            # 恢复原始Token
            settings.XT_CONFIG['TOKEN'] = original_token
            
            # 分析错误类型
            error_msg = str(e)
            if '过期' in error_msg or 'expired' in error_msg.lower():
                return {
                    'success': False,
                    'message': 'Token无效或已过期',
                    'error_code': 'TOKEN_EXPIRED'
                }
            elif '连接' in error_msg:
                return {
                    'success': False,
                    'message': '无法连接到迅投服务，请检查网络或服务状态',
                    'error_code': 'SERVICE_UNAVAILABLE'
                }
            else:
                return {
                    'success': False,
                    'message': 'Token无效，无法连接到迅投',
                    'error_code': 'TOKEN_INVALID'
                }
                
    except Exception as e:
        logger.error(f'验证迅投连接时发生异常: {str(e)}', exc_info=True)
        # 确保恢复原始Token
        settings.XT_CONFIG['TOKEN'] = original_token
        return {
            'success': False,
            'message': '服务器内部错误',
            'error_code': 'INTERNAL_ERROR'
        }


def verify_with_xt_trader(token, original_token):
    """
    使用xt_trader验证连接（备用验证方式）
    
    参数:
        token: 要验证的Token
        original_token: 原始Token（用于恢复）
    
    返回:
        dict: 验证结果
    """
    try:
        # 尝试连接迅投交易接口
        xt_trader, connected = get_xt_trader_connection()
        
        if connected:
            logger.info('迅投连接验证成功（通过xt_trader）')
            # 恢复原始Token（如果连接成功，会在token_login中更新）
            settings.XT_CONFIG['TOKEN'] = original_token
            return {
                'success': True,
                'message': '连接成功'
            }
        else:
            logger.warning('迅投连接验证失败：无法建立连接（xt_trader）')
            # 恢复原始Token
            settings.XT_CONFIG['TOKEN'] = original_token
            return {
                'success': False,
                'message': 'Token无效或已过期，无法连接到迅投',
                'error_code': 'CONNECTION_FAILED'
            }
    except Exception as e:
        logger.error(f'xt_trader验证异常: {str(e)}', exc_info=True)
        # 恢复原始Token
        settings.XT_CONFIG['TOKEN'] = original_token
        return {
            'success': False,
            'message': 'Token无效，无法连接到迅投',
            'error_code': 'TOKEN_INVALID'
        }


@api_view(['POST'])
def token_login(request):
    """
    Token登录接口
    接收前端传来的Token，配置到settings，连接迅投，返回连接结果
    
    API路径: /api/auth/token-login/
    请求方法: POST
    请求体: {"token": "用户输入的Token字符串"}
    
    响应格式:
    成功: {
        "success": true,
        "connected": true,
        "message": "登录成功，已连接到迅投",
        "token": "保存的token值"
    }
    失败: {
        "success": false,
        "connected": false,
        "message": "错误消息"
    }
    """
    try:
        # 1. 获取并验证Token
        token = request.data.get('token', '').strip()
        
        if not token:
            logger.warning('Token登录失败：Token为空')
            return Response({
                'success': False,
                'connected': False,
                'message': 'Token不能为空'
            }, status=400)
        
        logger.info(f'收到Token登录请求，Token长度: {len(token)}')
        
        # 2. 验证迅投连接
        connection_result = verify_xt_connection(token)
        
        # 3. 如果连接成功，更新Token配置
        if connection_result['success']:
            # 更新Token到运行时配置
            set_xt_token(token)
            
            logger.info('Token登录成功，已连接到迅投')
            return Response({
                'success': True,
                'connected': True,
                'message': '登录成功，已连接到迅投',
                'token': token
            })
        else:
            # 连接失败，返回错误信息
            logger.warning(f'Token登录失败: {connection_result.get("message", "未知错误")}')
            return Response({
                'success': False,
                'connected': False,
                'message': connection_result.get('message', 'Token无效，无法连接到迅投')
            })
            
    except Exception as e:
        # 记录错误日志
        logger.error(f'Token登录失败: {str(e)}', exc_info=True)
        return Response({
            'success': False,
            'connected': False,
            'message': '服务器内部错误'
        }, status=500)

