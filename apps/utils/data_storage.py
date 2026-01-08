"""
数据存储工具模块
用于存储和查询账户历史数据
"""

import logging
from datetime import datetime, timedelta
from django.conf import settings
from apps.utils.db import get_mongodb_db

logger = logging.getLogger(__name__)


def save_account_snapshot(account_id, account_data):
    """
    保存账户快照到MongoDB
    
    参数:
        account_id: 账户ID
        account_data: 账户数据字典，包含：
            - total_asset: 总资产
            - market_value: 持仓市值
            - cash: 可用金额
            - frozen_cash: 冻结金额
            - positions: 持仓列表（可选）
    
    返回:
        bool: 是否保存成功
    """
    try:
        # 获取数据库对象
        db = get_mongodb_db()
        
        snapshot = {
            'account_id': str(account_id),
            'date': datetime.now().date().isoformat(),  # YYYY-MM-DD格式
            'timestamp': datetime.now(),
            'total_asset': float(account_data.get('total_asset', 0)),
            'market_value': float(account_data.get('market_value', 0)),
            'cash': float(account_data.get('cash', 0)),
            'frozen_cash': float(account_data.get('frozen_cash', 0)),
            'positions': account_data.get('positions', [])
        }
        
        # 保存到account_snapshots集合
        result = db.account_snapshots.insert_one(snapshot)
        logger.info(f'账户 {account_id} 快照保存成功，ID: {result.inserted_id}')
        return True
        
    except Exception as e:
        logger.error(f'保存账户快照失败: {str(e)}', exc_info=True)
        return False


def get_account_history(account_id, days=30, start_date=None, end_date=None):
    """
    从MongoDB获取账户历史数据
    
    参数:
        account_id: 账户ID
        days: 获取最近多少天的数据（如果start_date和end_date未指定）
        start_date: 开始日期（YYYY-MM-DD格式或datetime对象）
        end_date: 结束日期（YYYY-MM-DD格式或datetime对象）
    
    返回:
        list: 账户历史数据列表，按日期升序排序
        [
            {
                'date': '2025-01-01',
                'total_assets': 4100000.00,
                'market_value': 2850000.00,
                'cash': 1250000.00
            },
            ...
        ]
    """
    try:
        # 构建查询条件
        query = {'account_id': str(account_id)}
        
        # 处理日期范围
        if start_date or end_date:
            date_query = {}
            if start_date:
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                date_query['$gte'] = start_date.isoformat()
            if end_date:
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                date_query['$lte'] = end_date.isoformat()
            if date_query:
                query['date'] = date_query
        else:
            # 如果没有指定日期范围，获取最近days天的数据
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            query['date'] = {
                '$gte': start_date.isoformat(),
                '$lte': end_date.isoformat()
            }
        
        # 获取数据库对象并查询数据
        db = get_mongodb_db()
        snapshots = db.account_snapshots.find(query).sort('date', 1)  # 按日期升序排序
        
        # 转换为前端需要的格式
        history = []
        for snapshot in snapshots:
            history.append({
                'date': snapshot['date'],
                'total_assets': float(snapshot.get('total_asset', 0)),
                'market_value': float(snapshot.get('market_value', 0)),
                'cash': float(snapshot.get('cash', 0))
            })
        
        logger.info(f'从数据库获取账户 {account_id} 历史数据，共 {len(history)} 条记录')
        return history
        
    except Exception as e:
        logger.error(f'获取账户历史数据失败: {str(e)}', exc_info=True)
        return []


def get_account_snapshot_by_date(account_id, target_date):
    """
    获取指定日期的账户快照
    
    参数:
        account_id: 账户ID
        target_date: 目标日期（YYYY-MM-DD格式或datetime对象）
    
    返回:
        dict: 账户快照数据，如果不存在返回None
    """
    try:
        if isinstance(target_date, str):
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # 获取数据库对象
        db = get_mongodb_db()
        snapshot = db.account_snapshots.find_one({
            'account_id': str(account_id),
            'date': target_date.isoformat()
        })
        
        if snapshot:
            return {
                'date': snapshot['date'],
                'total_asset': float(snapshot.get('total_asset', 0)),
                'market_value': float(snapshot.get('market_value', 0)),
                'cash': float(snapshot.get('cash', 0)),
                'frozen_cash': float(snapshot.get('frozen_cash', 0)),
                'positions': snapshot.get('positions', [])
            }
        return None
        
    except Exception as e:
        logger.error(f'获取账户快照失败: {str(e)}', exc_info=True)
        return None


def get_yearly_data(account_id, start_year=None, end_year=None):
    """
    获取年度汇总数据
    
    参数:
        account_id: 账户ID
        start_year: 开始年份（如2023）
        end_year: 结束年份（如2025）
    
    返回:
        dict: 年度数据字典
        {
            '2023': {
                'totalAssets': 3200000.00,
                'returnRate': 12.50,
                'investmentRate': 8.30
            },
            ...
        }
    """
    try:
        # 构建查询条件
        query = {'account_id': str(account_id)}
        
        if start_year or end_year:
            date_query = {}
            if start_year:
                date_query['$gte'] = f'{start_year}-01-01'
            if end_year:
                date_query['$lte'] = f'{end_year}-12-31'
            if date_query:
                query['date'] = date_query
        
        # 获取数据库对象并查询所有数据
        db = get_mongodb_db()
        snapshots = db.account_snapshots.find(query).sort('date', 1)
        
        # 按年份分组
        yearly_data = {}
        for snapshot in snapshots:
            year = snapshot['date'][:4]  # 提取年份
            if year not in yearly_data:
                yearly_data[year] = {
                    'totalAssets': [],
                    'marketValues': []  # 直接存储market_value，避免重复查询
                }
            
            yearly_data[year]['totalAssets'].append(float(snapshot.get('total_asset', 0)))
            yearly_data[year]['marketValues'].append(float(snapshot.get('market_value', 0)))
        
        # 计算年度统计数据
        result = {}
        for year, data in yearly_data.items():
            if not data['totalAssets']:
                continue
            
            # 年度平均资产（或年末资产）
            avg_assets = sum(data['totalAssets']) / len(data['totalAssets'])
            end_assets = data['totalAssets'][-1] if data['totalAssets'] else 0
            start_assets = data['totalAssets'][0] if data['totalAssets'] else 0
            
            # 计算回报率（年度收益率）
            return_rate = ((end_assets - start_assets) / start_assets * 100) if start_assets > 0 else 0
            
            # 计算投资占比（持仓市值占比）
            avg_market_value = sum(data['marketValues']) / len(data['marketValues']) if data['marketValues'] else 0
            investment_rate = (avg_market_value / avg_assets * 100) if avg_assets > 0 else 0
            
            result[year] = {
                'totalAssets': round(end_assets, 2),
                'returnRate': round(return_rate, 2),
                'investmentRate': round(investment_rate, 2)
            }
        
        return result
        
    except Exception as e:
        logger.error(f'获取年度数据失败: {str(e)}', exc_info=True)
        return {}


def get_weekly_data(account_id, weeks=4):
    """
    获取周度汇总数据
    
    参数:
        account_id: 账户ID
        weeks: 获取最近多少周的数据
    
    返回:
        dict: 周度数据字典
        {
            '2025-W01': {
                'totalAssets': 4100000.00,
                'returnRate': 8.0,
                'investmentRate': 7.8
            },
            ...
        }
    """
    try:
        # 计算日期范围
        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        # 获取历史数据
        history = get_account_history(account_id, start_date=start_date, end_date=end_date)
        
        if not history:
            return {}
        
        # 按周分组
        weekly_data = {}
        for record in history:
            date_obj = datetime.strptime(record['date'], '%Y-%m-%d').date()
            year, week, _ = date_obj.isocalendar()
            week_key = f'{year}-W{week:02d}'
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    'totalAssets': [],
                    'marketValues': []
                }
            
            weekly_data[week_key]['totalAssets'].append(record['total_assets'])
            weekly_data[week_key]['marketValues'].append(record['market_value'])
        
        # 计算周度统计数据
        result = {}
        for week_key, data in weekly_data.items():
            if not data['totalAssets']:
                continue
            
            # 周平均资产（或周末资产）
            end_assets = data['totalAssets'][-1] if data['totalAssets'] else 0
            start_assets = data['totalAssets'][0] if data['totalAssets'] else 0
            
            # 计算回报率（周收益率）
            return_rate = ((end_assets - start_assets) / start_assets * 100) if start_assets > 0 else 0
            
            # 计算投资占比
            avg_market_value = sum(data['marketValues']) / len(data['marketValues']) if data['marketValues'] else 0
            avg_assets = sum(data['totalAssets']) / len(data['totalAssets'])
            investment_rate = (avg_market_value / avg_assets * 100) if avg_assets > 0 else 0
            
            result[week_key] = {
                'totalAssets': round(end_assets, 2),
                'returnRate': round(return_rate, 2),
                'investmentRate': round(investment_rate, 2)
            }
        
        return result
        
    except Exception as e:
        logger.error(f'获取周度数据失败: {str(e)}', exc_info=True)
        return {}

