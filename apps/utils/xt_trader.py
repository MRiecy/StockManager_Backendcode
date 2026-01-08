"""
迅投交易工具模块
提供统一的交易接口连接管理和回调类
"""

import time
import datetime
import sys
import logging
from django.conf import settings
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount

logger = logging.getLogger(__name__)


class XtQuantTraderCallbackImpl(XtQuantTraderCallback):
    """
    迅投交易回调类实现
    统一的回调处理，所有交易相关的回调都在这里处理
    """
    
    def on_disconnected(self):
        """连接断开回调"""
        logger.warning(f'{datetime.datetime.now()} 连接断开回调')

    def on_stock_order(self, order):
        """委托回调"""
        logger.info(f'{datetime.datetime.now()} 委托回调 投资备注: {order.order_remark}')

    def on_stock_trade(self, trade):
        """成交回调"""
        logger.info(f'{datetime.datetime.now()} 成交回调 {trade.order_remark} '
                   f'委托方向(48买 49卖) {trade.offset_flag} 成交价格 {trade.traded_price} 成交数量 {trade.traded_volume}')

    def on_order_error(self, order_error):
        """委托报错回调"""
        logger.error(f'委托报错回调 {order_error.order_remark} {order_error.error_msg}')

    def on_cancel_error(self, cancel_error):
        """撤单错误回调"""
        logger.error(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name}')

    def on_order_stock_async_response(self, response):
        """异步委托回调"""
        logger.info(f'异步委托回调 投资备注: {response.order_remark}')

    def on_cancel_order_stock_async_response(self, response):
        """异步撤单回调"""
        logger.info(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name}')

    def on_account_status(self, status):
        """账户状态回调"""
        logger.info(f'{datetime.datetime.now()} {sys._getframe().f_code.co_name}')


def create_xt_trader(session_id=None):
    """
    创建并初始化迅投交易对象
    
    参数:
        session_id: 会话ID，如果为None则使用当前时间戳
    
    返回:
        XtQuantTrader: 交易对象，如果创建失败返回None
    """
    try:
        # 从配置文件获取路径
        path = settings.XT_CONFIG['USERDATA_PATH']
        
        # 生成会话ID
        if session_id is None:
            session_id = int(time.time())
        
        # 创建交易对象
        xt_trader = XtQuantTrader(path, session_id)
        
        # 注册回调
        callback = XtQuantTraderCallbackImpl()
        xt_trader.register_callback(callback)
        
        # 启动交易接口
        xt_trader.start()
        
        logger.info(f'迅投交易对象创建成功，session_id: {session_id}')
        return xt_trader
        
    except Exception as e:
        logger.error(f'创建迅投交易对象失败: {str(e)}', exc_info=True)
        return None


def connect_xt_trader(xt_trader):
    """
    连接迅投交易接口
    
    参数:
        xt_trader: XtQuantTrader对象
    
    返回:
        bool: 连接成功返回True，失败返回False
    """
    try:
        connect_result = xt_trader.connect()
        if connect_result == 0:
            logger.info('迅投交易接口连接成功')
            return True
        else:
            logger.error(f'连接交易接口失败，错误码: {connect_result}')
            return False
    except Exception as e:
        logger.error(f'连接交易接口异常: {str(e)}', exc_info=True)
        return False


def get_xt_trader_connection():
    """
    获取已连接迅投交易对象（便捷函数）
    
    返回:
        tuple: (xt_trader, success)
            - xt_trader: XtQuantTrader对象，如果创建失败为None
            - success: 是否成功连接
    """
    xt_trader = create_xt_trader()
    if xt_trader is None:
        return None, False
    
    success = connect_xt_trader(xt_trader)
    if not success:
        return None, False
    
    return xt_trader, True


def create_stock_account(account_id, account_type='STOCK'):
    """
    创建股票账户对象
    
    参数:
        account_id: 账户ID
        account_type: 账户类型（默认为'STOCK'，例如'FUTURE'/'CREDIT'）
    
    返回:
        StockAccount: 股票账户对象
    """
    return StockAccount(account_id, account_type)


# 为了向后兼容，保留旧的类名
MyXtQuantTraderCallback = XtQuantTraderCallbackImpl


















