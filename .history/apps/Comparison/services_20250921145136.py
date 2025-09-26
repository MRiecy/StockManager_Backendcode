import os
import threading
import pandas as pd
import duckdb
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum
from .models import CacheIndex

# 全局内存字典，用于存储实时行情 (线程安全需额外处理，此处简化)
REALTIME_QUOTES = {}  # 结构: { "symbol_period": {latest_data_point} }
_lock = threading.Lock()  # 线程锁

def subscribe_realtime_quotes(symbol_list, period):
    """订阅实时行情，并更新到内存字典"""
    try:
        from xtquant import xtdata
        for symbol in symbol_list:
            key = f"{symbol}_{period}"
            # 订阅迅投实时行情
            xtdata.subscribe_quote(symbol, period=period)
            # 在实际项目中需要用线程或异步任务监听更新
            print(f"已订阅 {symbol} 的 {period} 实时行情")
    except ImportError:
        print("警告: xtquant 模块未找到，跳过实时行情订阅")
    except Exception as e:
        print(f"订阅实时行情失败: {str(e)}")

def get_combined_market_data(symbol_list, period, start_time, end_time):
    """核心函数：获取拼接后的历史+实时数据"""
    # Step 1: 检查并确保实时行情已订阅
    subscribe_realtime_quotes(symbol_list, period)

    # Step 2: 初始化最终结果字典
    combined_data = {}

    for symbol in symbol_list:
        try:
            # Step 3: 检查本地缓存是否满足请求范围
            cached_data, missing_ranges = check_and_fetch_cached_data(symbol, period, start_time, end_time)

            # Step 4: 如果有缺失范围，触发异步下载
            if missing_ranges:
                trigger_async_download(symbol, period, missing_ranges)

            # Step 5: 从DuckDB查询满足范围的历史数据
            hist_df = query_historical_data_from_duckdb(symbol, period, start_time, end_time)

            # Step 6: 从内存中获取最新的实时行情点
            latest_quote = get_latest_realtime_quote(symbol, period)

            # Step 7: 将实时行情点拼接到历史数据末尾 (如果时间戳更新)
            if latest_quote is not None and not hist_df.empty:
                latest_hist_time = hist_df['time'].max()
                if latest_quote['time'] > latest_hist_time:
                    # 将字典转为DataFrame并拼接
                    latest_df = pd.DataFrame([latest_quote])
                    hist_df = pd.concat([hist_df, latest_df], ignore_index=True)

            # Step 8: 更新缓存访问时间 (用于LRU)
            update_cache_access_time(symbol, period)

            # Step 9: 将结果存入返回字典
            combined_data[symbol] = hist_df

        except Exception as e:
            print(f"处理 {symbol} 数据时出错: {str(e)}")
            combined_data[symbol] = pd.DataFrame()  # 返回空DataFrame

    return combined_data

def check_and_fetch_cached_data(symbol, period, req_start, req_end):
    """检查缓存，返回已缓存的数据范围和缺失的范围"""
    try:
        # 查询缓存索引，找出所有覆盖 [req_start, req_end] 的片段
        cached_segments = CacheIndex.objects.filter(
            symbol=symbol, 
            period=period,
            start_date__lte=req_end.date() if hasattr(req_end, 'date') else req_end,
            end_date__gte=req_start.date() if hasattr(req_start, 'date') else req_start
        ).order_by('start_date')

        # 简化处理: 假设我们只检查是否有完全覆盖的单个文件
        if cached_segments.exists():
            segment = cached_segments.first()
            req_start_date = req_start.date() if hasattr(req_start, 'date') else req_start
            req_end_date = req_end.date() if hasattr(req_end, 'date') else req_end
            
            if segment.start_date <= req_start_date and segment.end_date >= req_end_date:
                # 完全覆盖，无需下载
                return True, []
            else:
                # 部分覆盖或未覆盖，计算缺失
                if req_start_date > segment.end_date:
                    missing_start = req_start_date
                else:
                    missing_start = segment.end_date + timedelta(days=1)
                missing_end = req_end_date
                return False, [(missing_start, missing_end)]
        else:
            # 完全未缓存
            req_start_date = req_start.date() if hasattr(req_start, 'date') else req_start
            req_end_date = req_end.date() if hasattr(req_end, 'date') else req_end
            return False, [(req_start_date, req_end_date)]
    except Exception as e:
        print(f"检查缓存时出错: {str(e)}")
        return False, [(req_start, req_end)]

def trigger_async_download(symbol, period, missing_ranges):
    """异步触发历史数据下载"""
    def download_task():
        try:
            from xtquant import xtdata
            for (start, end) in missing_ranges:
                # 调用迅投下载函数
                print(f"开始下载 {symbol} {period} 数据: {start} 到 {end}")
                xtdata.download_history_data(
                    symbol, 
                    period, 
                    start.strftime("%Y%m%d"), 
                    end.strftime("%Y%m%d")
                )
                # 下载完成后，将数据转存为Parquet并更新缓存索引
                save_downloaded_data_to_parquet(symbol, period, start, end)
                # 检查并清理缓存 (LRU)
                enforce_cache_limit()
        except ImportError:
            print("警告: xtquant 模块未找到，跳过数据下载")
        except Exception as e:
            print(f"下载数据失败: {str(e)}")

    download_thread = threading.Thread(target=download_task)
    download_thread.daemon = True
    download_thread.start()

def save_downloaded_data_to_parquet(symbol, period, start_date, end_date):
    """将迅投下载的本地数据读取并保存为压缩Parquet"""
    try:
        from xtquant import xtdata
        
        # 读取刚下载的数据
        hist_data = xtdata.get_market_data_ex(
            field_list=['time', 'open', 'high', 'low', 'close', 'volume', 'amount'],
            stock_list=[symbol],
            period=period,
            start_time=start_date.strftime("%Y%m%d"),
            end_time=end_date.strftime("%Y%m%d"),
            count=-1,
            subscribe=False  # 只读本地
        )
        
        if symbol not in hist_data or hist_data[symbol].empty:
            print(f"警告: {symbol} 没有数据可保存")
            return
            
        df = hist_data[symbol]  # 获取DataFrame

        # 构建文件路径: /cache_root/SYMBOL/PERIOD/YEAR.parquet
        symbol_dir = os.path.join(settings.CACHE_ROOT, symbol.replace('.', '_'))
        os.makedirs(symbol_dir, exist_ok=True)
        file_name = f"{period}_{start_date.year}.parquet"  # 按年分区
        file_path = os.path.join(symbol_dir, file_name)

        # 使用DuckDB写入Parquet (利用其高压缩)
        con = duckdb.connect()  # 临时连接
        # 直接写入Parquet，DuckDB会自动应用高效压缩
        con.execute(f"COPY df TO '{file_path}' (FORMAT PARQUET, COMPRESSION SNAPPY)")

        # 更新缓存索引数据库
        CacheIndex.objects.create(
            symbol=symbol,
            period=period,
            start_date=start_date,
            end_date=end_date,
            file_path=file_path,
            size_bytes=os.path.getsize(file_path)
        )
        
        print(f"已保存 {symbol} 数据到 {file_path}")
        
    except ImportError:
        print("警告: xtquant 模块未找到，无法保存数据")
    except Exception as e:
        print(f"保存数据到Parquet失败: {str(e)}")

def query_historical_data_from_duckdb(symbol, period, start_time, end_time):
    """从DuckDB查询指定范围的历史数据"""
    try:
        # 根据symbol和period，查找所有相关的Parquet文件
        start_date = start_time.date() if hasattr(start_time, 'date') else start_time
        end_date = end_time.date() if hasattr(end_time, 'date') else end_time
        
        cache_entries = CacheIndex.objects.filter(
            symbol=symbol, 
            period=period,
            start_date__lte=end_date, 
            end_date__gte=start_date
        )

        dfs = []
        for entry in cache_entries:
            if os.path.exists(entry.file_path):
                try:
                    # 使用DuckDB直接查询Parquet文件，只选择需要的时间范围
                    start_timestamp = pd.Timestamp(start_time).timestamp()
                    end_timestamp = pd.Timestamp(end_time).timestamp()
                    
                    query = f"""
                    SELECT * FROM '{entry.file_path}'
                    WHERE time >= {start_timestamp} 
                    AND time <= {end_timestamp}
                    ORDER BY time
                    """
                    con = duckdb.connect()
                    result_df = con.execute(query).df()
                    if not result_df.empty:
                        dfs.append(result_df)
                except Exception as e:
                    print(f"查询文件 {entry.file_path} 失败: {str(e)}")

        if dfs:
            final_df = pd.concat(dfs, ignore_index=True).sort_values('time')
        else:
            final_df = pd.DataFrame()  # 返回空DataFrame

        return final_df
        
    except Exception as e:
        print(f"从DuckDB查询数据失败: {str(e)}")
        return pd.DataFrame()

def get_latest_realtime_quote(symbol, period):
    """从内存字典获取最新的实时行情"""
    with _lock:
        key = f"{symbol}_{period}"
        return REALTIME_QUOTES.get(key, None)  # 返回最新数据点 (字典格式)

def update_cache_access_time(symbol, period):
    """更新缓存条目的最后访问时间"""
    try:
        CacheIndex.objects.filter(symbol=symbol, period=period).update(last_access=timezone.now())
    except Exception as e:
        print(f"更新缓存访问时间失败: {str(e)}")

def enforce_cache_limit():
    """执行LRU缓存淘汰策略"""
    try:
        total_size = CacheIndex.objects.aggregate(total=Sum('size_bytes'))['total'] or 0
        max_bytes = settings.MAX_CACHE_SIZE_GB * 1024**3

        while total_size > max_bytes:
            # 找到最久未使用的条目
            oldest_entry = CacheIndex.objects.order_by('last_access').first()
            if oldest_entry:
                # 删除磁盘文件
                if os.path.exists(oldest_entry.file_path):
                    os.remove(oldest_entry.file_path)
                # 删除数据库记录
                total_size -= oldest_entry.size_bytes
                oldest_entry.delete()
                print(f"清理缓存: 删除 {oldest_entry.file_path}")
            else:
                break  # 无条目可删
    except Exception as e:
        print(f"执行缓存清理失败: {str(e)}")

def update_realtime_quote(symbol, period, quote_data):
    """更新实时行情数据 (供外部调用)"""
    with _lock:
        key = f"{symbol}_{period}"
        REALTIME_QUOTES[key] = quote_data