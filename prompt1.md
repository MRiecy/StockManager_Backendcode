获取历史行情与实时行情
提示

在gmd系列函数中，历史行情需要从本地读取，所以若想取历史行情，需要先将历史行情下载到本地，而实时行情是从服务器返回的

所以，若需要历史行情，请先使用界面端或者download_history函数进行下载；若需要最新行情，请向服务器进行订阅

特别的，对于xtdata.get_market_data_ex来说，由于没有subscribe参数，需要在参数外先进行订阅(subscribe_quote)才能获取最新行情

对于同时获取历史和实时行情的情况，gmd系列函数会自动进行拼接

内置Python
调用方法

内置python

ContextInfo.get_market_data_ex(
    fields=[], 
    stock_code=[], 
    period='follow', 
    start_time='', 
    end_time='', 
    count=-1, 
    dividend_type='follow', 
    fill_data=True, 
    subscribe=True)
释义

获取实时行情与历史行情数据

参数

名称	类型	描述
field	list	数据字段，详情见下方field字段表
stock_list	list	合约代码列表
period	str	数据周期，可选字段为:
"tick"
"1m"的整数倍周期
"5m"的整数倍周期
"1d"的整数倍周期
start_time	str	数据起始时间，格式为 %Y%m%d 或 %Y%m%d%H%M%S，填""为获取历史最早一天
end_time	str	数据结束时间，格式为 %Y%m%d 或 %Y%m%d%H%M%S ，填""为截止到最新一天
count	int	数据个数
dividend_type	str	除权方式,可选值为
'none'：不复权
'front':前复权
'back':后复权
'front_ratio': 等比前复权
'back_ratio': 等比后复权
fill_data	bool	是否填充数据
subscribe	bool	订阅数据开关，默认为True，设置为False时不做数据订阅，只读取本地已有数据。
field字段可选：
field	数据类型	含义
time	int	时间
open	float	开盘价
high	float	最高价
low	float	最低价
close	float	收盘价
volume	float	成交量
amount	float	成交额
settle	float	今结算
openInterest	float	持仓量
preClose	float	前收盘价
suspendFlag	int	停牌 1停牌，0 不停牌
period周期为tick时，field字段可选:
字段名	数据类型	含义
time	int	时间戳
stime	string	时间戳字符串形式
lastPrice	float	最新价
open	float	开盘价
high	float	最高价
low	float	最低价
lastClose	float	前收盘价
amount	float	成交总额
volume	int	成交总量（手）
pvolume	int	原始成交总量(未经过股手转换的成交总量)【不推荐使用】
stockStatus	int	证券状态
openInterest	int	若是股票，则openInt含义为股票状态，非股票则是持仓量openInt字段说明
transactionNum	float	成交笔数(期货没有，单独计算)
lastSettlementPrice	float	前结算(股票为0)
settlementPrice	float	今结算(股票为0)
askPrice	list[float]	多档委卖价
askVol	list[int]	多档委卖量
bidPrice	list[float]	多档委买价
bidVol	list[int]	多档委买量
返回值

返回dict { stock_code1 : value1, stock_code2 : value2, ... }
value1, value2, ... ：pd.DataFrame 数据集，index为time_list，columns为fields,可参考Bar字段
各标的对应的DataFrame维度相同、索引相同
示例

获取行情示例仅获取历史行情仅获取最新行情获取历史行情+最新行情

# coding:gbk

def init(C):
  start_date = '20231001'# 格式"YYYYMMDD"，开始下载的日期，date = ""时全量下载
  end_date = "" 
  period = "1d" 

  need_download = 1  # 取数据是空值时，将need_download赋值为1，确保正确下载了历史数据
  
  code_list = ["000001.SZ", "600519.SH"] # 股票列表

  if need_download: # 判断要不要下载数据, gmd系列函数都是从本地读取历史数据,从服务器订阅获取最新数据
    my_download(code_list, period, start_date, end_date)
  
  ############ 仅获取历史行情 #####################
  subscribe = False # 设置订阅参数，使gmd_ex仅返回本地数据
  count = -1 # 设置count参数，使gmd_ex返回全部数据
  data1 = C.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date,subscribe = subscribe)

  ############ 仅获取最新行情 #####################
  subscribe = True # 设置订阅参数，使gmd_ex仅返回最新行情
  count = 1 # 设置count参数，使gmd_ex仅返回最新行情数据
  data2 = C.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date,subscribe = subscribe, count = 1) # count 设置为1，使返回值只包含最新行情

  ############ 获取历史行情+最新行情 #####################
  subscribe = True # 设置订阅参数，使gmd_ex仅返回最新行情
  count = -1 # 设置count参数，使gmd_ex返回全部数据
  data3 = C.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date,subscribe = subscribe, count = -1) # count 设置为-1，使返回值包含最新行情和历史行情


  print(data1[code_list[0]].tail())# 行情数据查看
  print(data2[code_list[0]].tail())
  print(data3[code_list[0]].tail())

def handlebar(C):
  return


def my_download(stock_list,period,start_date = '', end_date = ''):
  '''
  用于显示下载进度
  '''
  if "d" in period:
    period = "1d"
  elif "m" in period:
    if int(period[0]) < 5:
      period = "1m"
    else:
      period = "5m"
  elif "tick" == period:
    pass
  else:
    raise KeyboardInterrupt("周期传入错误")


  n = 1
  num = len(stock_list)
  for i in stock_list:
    print(f"当前正在下载{n}/{num}")
    
    download_history_data(i,period,start_date, end_date)
    n += 1
  print("下载任务结束")

原生Python
调用方法

python

from xtquant import xtdata
xtdata.get_market_data_ex(
    field_list=[],# 字段
    stock_list=[],# 合约代码列表
    period='1d',# 数据周期——1m、5m、1d、tick
    start_time='',# 数据起始时间%Y%m%d或%Y%m%d%H%M%S
    end_time='',# 数据结束时间%Y%m%d或%Y%m%d%H%M%S
    count=-1, # 数据个数
    dividend_type='none', # 除权方式
    fill_data=True, # 是否填充数据
)
参数

名称	类型	描述
field	list	数据字段，详情见下方field字段表
stock_list	list	合约代码列表
period	str	数据周期——1m、5m、1d、tick
start_time	str	数据起始时间，格式为 %Y%m%d 或 %Y%m%d%H%M%S，填""为获取历史最早一天
end_time	str	数据结束时间，格式为 %Y%m%d 或 %Y%m%d%H%M%S ，填""为截止到最新一天
count	int	数据个数
dividend_type	str	除权方式
fill_data	bool	是否填充数据
field字段可选：
field	数据类型	含义
time	int	时间
open	float	开盘价
high	float	最高价
low	float	最低价
close	float	收盘价
volume	float	成交量
amount	float	成交额
settle	float	今结算
openInterest	float	持仓量
preClose	float	前收盘价
suspendFlag	int	停牌 1停牌，0 不停牌
period周期为tick时，field字段可选:
字段名	数据类型	含义
time	int	时间戳
stime	string	时间戳字符串形式
lastPrice	float	最新价
open	float	开盘价
high	float	最高价
low	float	最低价
lastClose	float	前收盘价
amount	float	成交总额
volume	int	成交总量（手）
pvolume	int	原始成交总量(未经过股手转换的成交总量)【不推荐使用】
stockStatus	int	证券状态
openInterest	int	若是股票，则openInt含义为股票状态，非股票则是持仓量openInt字段说明
transactionNum	float	成交笔数(期货没有，单独计算)
lastSettlementPrice	float	前结算(股票为0)
settlementPrice	float	今结算(股票为0)
askPrice	list[float]	多档委卖价
askVol	list[int]	多档委卖量
bidPrice	list[float]	多档委买价
bidVol	list[int]	多档委买量
返回值

period为1m 5m 1dK线周期时
返回dict { field1 : value1, field2 : value2, ... }
value1, value2, ... ：pd.DataFrame 数据集，index为stock_list，columns为time_list
各字段对应的DataFrame维度相同、索引相同
示例

示例仅获取历史行情仅获取最新行情获取历史行情+最新行情


from xtquant import xtdata
import time


def my_download(stock_list:list,period:str,start_date = '', end_date = ''):
    '''
    用于显示下载进度
    '''
    import string
    
    if [i for i in ["d","w","mon","q","y",] if i in period]:
        period = "1d"
    elif "m" in period:
        numb = period.translate(str.maketrans("", "", string.ascii_letters))
        if int(numb) < 5:
            period = "1m"
        else:
            period = "5m"
    elif "tick" == period:
        pass
    else:
        raise KeyboardInterrupt("周期传入错误")


    n = 1
    num = len(stock_list)
    for i in stock_list:
        print(f"当前正在下载 {period} {n}/{num}")
        
        xtdata.download_history_data(i,period,start_date, end_date)
        n += 1
    print("下载任务结束")

def do_subscribe_quote(stock_list:list, period:str):
  for i in stock_list:
    xtdata.subscribe_quote(i,period = period)
  time.sleep(1) # 等待订阅完成

if __name__ == "__main__":

  start_date = '20231001'# 格式"YYYYMMDD"，开始下载的日期，date = ""时全量下载
  end_date = "" 
  period = "1d" 

  need_download = 1  # 取数据是空值时，将need_download赋值为1，确保正确下载了历史数据
  
  code_list = ["000001.SZ", "600519.SH"] # 股票列表

  if need_download: # 判断要不要下载数据, gmd系列函数都是从本地读取历史数据,从服务器订阅获取最新数据
    my_download(code_list, period, start_date, end_date)
  
  ############ 仅获取历史行情 #####################
  count = -1 # 设置count参数，使gmd_ex返回全部数据
  data1 = xtdata.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date)

  ############ 仅获取最新行情 #####################
  do_subscribe_quote(code_list,period)# 设置订阅参数，使gmd_ex取到最新行情
  count = 1 # 设置count参数，使gmd_ex仅返回最新行情数据
  data2 = xtdata.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date, count = 1) # count 设置为1，使返回值只包含最新行情

  ############ 获取历史行情+最新行情 #####################
  do_subscribe_quote(code_list,period) # 设置订阅参数，使gmd_ex取到最新行情
  count = -1 # 设置count参数，使gmd_ex返回全部数据
  data3 = xtdata.get_market_data_ex([],code_list,period = period, start_time = start_date, end_time = end_date, count = -1) # count 设置为1，使返回值只包含最新行情


  print(data1[code_list[0]].tail())# 行情数据查看
  print(data2[code_list[0]].tail())
  print(data3[code_list[0]].tail())


