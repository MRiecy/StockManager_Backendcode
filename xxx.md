订阅账号信息

subscribe(account)
释义
订阅账号信息，包括资金账号、委托信息、成交信息、持仓信息
参数
account - StockAccount 资金账号
返回
订阅结果信息，订阅成功返回0，订阅失败返回-1
备注
无
示例
订阅资金账号1000000365

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
subscribe_result = xt_trader.subscribe(account)
反订阅账号信息

unsubscribe(account)
释义
反订阅账号信息
参数
account - StockAccount 资金账号
返回
反订阅结果信息，订阅成功返回0，订阅失败返回-1
备注
无
示例
订阅资金账号1000000365

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
unsubscribe_result = xt_trader.unsubscribe(account)
股票同步报单

order_stock(account, stock_code, order_type, order_volume, price_type, price, strategy_name, order_remark)
释义
对股票进行下单操作
参数
account - StockAccount 资金账号
stock_code - str 证券代码，如'600000.SH'
order_type - int 委托类型
order_volume - int 委托数量，股票以'股'为单位，债券以'张'为单位
price_type - int 报价类型
price - float 委托价格
strategy_name - str 策略名称
order_remark - str 委托备注
返回
系统生成的订单编号，成功委托后的订单编号为大于0的正整数，如果为-1表示委托失败
备注
无
示例
股票资金账号1000000365对浦发银行买入1000股，使用限价价格10.5元, 委托备注为'order_test'

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
order_id = xt_trader.order_stock(account, '600000.SH', xtconstant.STOCK_BUY, 1000, xtconstant.FIX_PRICE, 10.5, 'strategy1', 'order_test')
股票异步报单

order_stock_async(account, stock_code, order_type, order_volume, price_type, price, strategy_name, order_remark)
释义
对股票进行异步下单操作，异步下单接口如果正常返回了下单请求序号seq，会收到on_order_stock_async_response的委托反馈
参数
account - StockAccount 资金账号
stock_code - str 证券代码， 如'600000.SH'
order_type - int 委托类型
order_volume - int 委托数量，股票以'股'为单位，债券以'张'为单位
price_type - int 报价类型
price - float 委托价格
strategy_name - str 策略名称
order_remark - str 委托备注
返回
返回下单请求序号seq，成功委托后的下单请求序号为大于0的正整数，如果为-1表示委托失败
备注
如果失败，则通过下单失败主推接口返回下单失败信息
示例
股票资金账号1000000365对浦发银行买入1000股，使用限价价格10.5元，委托备注为'order_test'

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
seq = xt_trader.order_stock_async(account, '600000.SH', xtconstant.STOCK_BUY, 1000, xtconstant.FIX_PRICE, 10.5, 'strategy1', 'order_test')
股票同步撤单

cancel_order_stock(account, order_id)
释义
根据订单编号对委托进行撤单操作
参数
account - StockAccount 资金账号
order_id - int 同步下单接口返回的订单编号,对于期货来说，是order结构中的order_sysid字段
返回
返回是否成功发出撤单指令，0: 成功, -1: 表示撤单失败
备注
无
示例
股票资金账号1000000365对订单编号为order_id的委托进行撤单

account = StockAccount('1000000365')
order_id = 100
#xt_trader为XtQuant API实例对象
cancel_result = xt_trader.cancel_order_stock(account, order_id)
股票同步撤单

cancel_order_stock_sysid(account, market, order_sysid)
释义
根据券商柜台返回的合同编号对委托进行撤单操作
参数
account - StockAccount 资金账号
market - int 交易市场
order_sysid - str 券商柜台的合同编号
返回
返回是否成功发出撤单指令，0: 成功， -1: 表示撤单失败
备注
无
示例
股票资金账号1000000365对柜台合同编号为order_sysid的上交所委托进行撤单

account = StockAccount('1000000365')
market = xtconstant.SH_MARKET
order_sysid = "100" 
#xt_trader为XtQuant API实例对象
cancel_result = xt_trader.cancel_order_stock_sysid(account, market, order_sysid)
股票异步撤单

cancel_order_stock_async(account, order_id)
释义
根据订单编号对委托进行异步撤单操作
参数
account - StockAccount 资金账号
order_id - int 下单接口返回的订单编号，对于期货来说，是order结构中的order_sysid
返回
返回撤单请求序号, 成功委托后的撤单请求序号为大于0的正整数, 如果为-1表示委托失败
备注
如果失败，则通过撤单失败主推接口返回撤单失败信息
示例
股票资金账号1000000365对订单编号为order_id的委托进行异步撤单

account = StockAccount('1000000365')
order_id = 100
#xt_trader为XtQuant API实例对象
cancel_result = xt_trader.cancel_order_stock_async(account, order_id)
股票异步撤单

cancel_order_stock_sysid_async(account, market, order_sysid)
释义
根据券商柜台返回的合同编号对委托进行异步撤单操作
参数
account - StockAccount 资金账号
market - int 交易市场
order_sysid - str 券商柜台的合同编号
返回
返回撤单请求序号, 成功委托后的撤单请求序号为大于0的正整数, 如果为-1表示委托失败
备注
如果失败，则通过撤单失败主推接口返回撤单失败信息
示例
股票资金账号1000000365对柜台合同编号为order_sysid的上交所委托进行异步撤单

account = StockAccount('1000000365')
market = xtconstant.SH_MARKET
order_sysid = "100" 
#xt_trader为XtQuant API实例对象
cancel_result = xt_trader.cancel_order_stock_sysid_async(account, market, order_sysid)
资金划拨

fund_transfer(account, transfer_direction, price)
释义
资金划拨
参数
account - StockAccount 资金账号
transfer_direction - int 划拨方向，见数据字典划拨方向(transfer_direction)字段说明
price - float 划拨金额
返回
(success, msg)
success - bool 划拨操作是否成功
msg - str 反馈信息
外部交易数据录入

sync_transaction_from_external(operation, data_type, account, deal_list)
释义

通用数据导出
参数

operation - str 操作类型，有"UPDATE","REPLACE","ADD","DELETE"
data_type - str 数据类型，有"DEAL"
account - StockAccount 资金账号
deal_list - list 成交列表,每一项是Deal成交对象的参数字典,键名参考官网数据字典,大小写保持一致
返回

result - dict 结果反馈信息
示例


deal_list = [
    			{'m_strExchangeID':'SF', 'm_strInstrumentID':'ag2407'
        		, 'm_strTradeID':'123456', 'm_strOrderSysID':'1234566'
        		, 'm_dPrice':7600, 'm_nVolume':1
        		, 'm_strTradeDate': '20240627'
            	}
]
resp = xt_trader.sync_transaction_from_external('ADD', 'DEAL', acc, deal_list)
print(resp)
#成功输出示例：{'msg': 'sync transaction from external success'}
#失败输出示例：{'error': {'msg': '[0-0: invalid operation type: ADDD], '}}
股票查询接口
资产查询

query_stock_asset(account)
释义
查询资金账号对应的资产
参数
account - StockAccount 资金账号
返回
该账号对应的资产对象XtAsset或者None
备注
返回None表示查询失败
示例
查询股票资金账号1000000365对应的资产数据

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
asset = xt_trader.query_stock_asset(account)
委托查询

query_stock_orders(account, cancelable_only = False)
释义
查询资金账号对应的当日所有委托
参数
account - StockAccount 资金账号
cancelable_only - bool 仅查询可撤委托
返回
该账号对应的当日所有委托对象XtOrder组成的list或者None
备注
None表示查询失败或者当日委托列表为空
示例
查询股票资金账号1000000365对应的当日所有委托

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
orders = xt_trader.query_stock_orders(account, False)
成交查询

query_stock_trades(account)
释义
查询资金账号对应的当日所有成交
参数
account - StockAccount 资金账号
返回
该账号对应的当日所有成交对象XtTrade组成的list或者None
备注
None表示查询失败或者当日成交列表为空
示例
查询股票资金账号1000000365对应的当日所有成交

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
trades = xt_trader.query_stock_trades(account)
持仓查询

query_stock_positions(account)
释义
查询资金账号对应的持仓
参数
account - StockAccount 资金账号
返回
该账号对应的最新持仓对象XtPosition组成的list或者None
备注
None表示查询失败或者当日持仓列表为空
示例
查询股票资金账号1000000365对应的最新持仓

account = StockAccount('1000000365')
#xt_trader为XtQuant API实例对象
positions = xt_trader.query_stock_positions(account)
期货持仓统计查询

query_position_statistics(account)
释义
查询期货账号的持仓统计
参数
account - StockAccount 资金账号
返回
该账号对应的最新持仓对象XtPositionStatistics组成的list或者None
备注
None表示查询失败或者当日持仓列表为空
示例
查询期货资金账号1000000365对应的最新持仓

account = StockAccount('1000000365', 'FUTURE')
#xt_trader为XtQuant API实例对象
positions = xt_trader.query_position_statistics(account)
信用查询接口
信用资产查询

query_credit_detail(account)
释义
查询信用资金账号对应的资产
参数
account - StockAccount 资金账号
返回
该信用账户对应的资产对象XtCreditDetail组成的list或者None
备注
None表示查询失败
通常情况下一个资金账号只有一个详细信息数据
示例
查询信用资金账号1208970161对应的资产信息

account = StockAccount('1208970161', 'CREDIT')
#xt_trader为XtQuant API实例对象
datas = xt_trader.query_credit_detail(account)
负债合约查询

query_stk_compacts(account)
释义
查询资金账号对应的负债合约
参数
account - StockAccount 资金账号
返回
该账户对应的负债合约对象StkCompacts组成的list或者None
备注
None表示查询失败或者负债合约列表为空
示例
查询信用资金账号1208970161对应的负债合约

account = StockAccount('1208970161', 'CREDIT')
#xt_trader为XtQuant API实例对象
datas = xt_trader.query_stk_compacts(account)
融资融券标的查询

query_credit_subjects(account)
释义
查询资金账号对应的融资融券标的
参数
account - StockAccount 资金账号
返回
该账户对应的融资融券标的对象CreditSubjects组成的list或者None
备注
None表示查询失败或者融资融券标的列表为空
示例
查询信用资金账号1208970161对应的融资融券标的

account = StockAccount('1208970161', 'CREDIT')
#xt_trader为XtQuant API实例对象
datas = xt_trader.query_credit_subjects(account)
可融券数据查询

query_credit_slo_code(account)
释义
查询资金账号对应的可融券数据
参数
account - StockAccount 资金账号
返回
该账户对应的可融券数据对象CreditSloCode组成的list或者None
备注
None表示查询失败或者可融券数据列表为空
示例
查询信用资金账号1208970161对应的可融券数据

account = StockAccount('1208970161', 'CREDIT')
#xt_trader为XtQuant API实例对象
datas = xt_trader.query_credit_slo_code(account)
标的担保品查询

query_credit_assure(account)
释义
查询资金账号对应的标的担保品
参数
account - StockAccount 资金账号
返回
该账户对应的标的担保品对象CreditAssure组成的list或者None
备注
None表示查询失败或者标的担保品列表为空
示例
查询信用资金账号1208970161对应的标的担保品

account = StockAccount('1208970161', 'CREDIT')
#xt_trader为XtQuant API实例对象
datas = xt_trader.query_credit_assure(account)
其他查询接口
新股申购额度查询

query_new_purchase_limit(account)
释义
查询新股申购额度
参数
account - StockAccount 资金账号
返回
dict 新股申购额度数据集
{ type1: number1, type2: number2, ... }
type - str 品种类型
KCB - 科创板，SH - 上海，SZ - 深圳
number - int 可申购股数
备注
数据仅代表股票申购额度，债券的申购额度固定10000张
当日新股信息查询

query_ipo_data()
释义

查询当日新股新债信息
参数

无
返回

dict 新股新债信息数据集

{ stock1: info1, stock2: info2, ... }

stock - str 品种代码，例如 '301208.SZ'
info - dict 新股信息
name - str 品种名称
type - str 品种类型
STOCK - 股票，BOND - 债券
minPurchaseNum / maxPurchaseNum - int 最小 / 最大申购额度
单位为股（股票）/ 张（债券）
purchaseDate - str 申购日期
issuePrice - float 发行价
返回值示例


{'754810.SH': {'name': '丰山发债', 'type': 'BOND', 'maxPurchaseNum': 10000, 'minPurchaseNum': 10, 'purchaseDate': '20220627', 'issuePrice': 100.0}, '301208.SZ': {'name': '中亦科技', 'type': 'STOCK', 'maxPurchaseNum': 16500, 'minPurchaseNum': 500, 'purchaseDate': '20220627', 'issuePrice': 46.06}}
备注

无
账号信息查询

query_account_infos()
释义

查询所有资金账号
参数

无
返回

list 账号信息列表

[ XtAccountInfo ]
备注

无
账号状态查询

query_account_status()
释义

查询所有账号状态
参数

无
返回

list 账号状态列表

[ XtAccountStatus ]
备注

无
普通柜台资金查询

query_com_fund(account)
释义
划拨业务查询普通柜台的资金
参数
account - StockAccount 资金账号
返回
result - dict 资金信息，包含以下字段
success - bool
erro - str
currentBalance - double 当前余额
enableBalance - double 可用余额
fetchBalance - double 可取金额
interest - double 待入账利息
assetBalance - double 总资产
fetchCash - double 可取现金
marketValue - double 市值
debt - double 负债
普通柜台持仓查询

query_com_position(account)
释义
划拨业务查询普通柜台的持仓
参数
account - StockAccount 资金账号
返回
result - list 持仓信息列表[position1, position2, ...]
position - dict 持仓信息，包含以下字段
success - bool
error - str
stockAccount - str 股东号
exchangeType - str 交易市场
stockCode - str 证券代码
stockName - str 证券名称
totalAmt - float 总量
enableAmount - float 可用量
lastPrice - float 最新价
costPrice - float 成本价
income - float 盈亏
incomeRate - float 盈亏比例
marketValue - float 市值
costBalance - float 成本总额
bsOnTheWayVol - int 买卖在途量
prEnableVol - int 申赎可用量
通用数据导出

export_data(account, result_path, data_type, start_time = None, end_time = None, user_param = {})
释义

通用数据导出
参数

account - StockAccount 资金账号
result_path - str 导出路径，包含文件名及.csv后缀，如'C:\Users\Desktop\test\deal.csv'
data_type - str 数据类型，如'deal'
start_time - str 开始时间（可缺省）
end_time - str 结束时间（可缺省）
user_param - dict 用户参数（可缺省）
返回

result - dict 结果反馈信息
示例


resp = xt_trader.export_data(acc, 'C:\\Users\\Desktop\\test\\deal.csv', 'deal')
print(resp)
#成功输出示例：{'msg': 'export success'}
#失败输出示例：{'error': {'errorMsg': 'can not find account info, accountID:2000449 accountType:2'}}
通用数据查询

query_data(account, result_path, data_type, start_time = None, end_time = None, user_param = {})
释义

通用数据查询，利用export_data接口导出数据后再读取其中的数据内容，读取完毕后删除导出的文件
参数

同export_data

返回

result - dict 数据信息
示例


data = xt_trader.query_data(acc, 'C:\\Users\\Desktop\\test\\deal.csv', 'deal')
print(data)
#成功输出示例：
#    account_id    account_Type    stock_code    order_type    ...  
#0    2003695    2    688488.SH    23    ...
#1    2003695    2    000096.SZ    23    ...
#失败输出示例：{'error': {'errorMsg': 'can not find account info, accountID:2000449 accountType:2'}}
约券相关接口
券源行情查询

smt_query_quoter(account)
释义
券源行情查询
参数
account - StockAccount 资金账号
返回
result - list 券源信息列表[quoter1, quoter2, ...]
quoter - dict 券源信息，包含以下字段
success - bool
error - str
finType - str 金融品种
stockType - str 证券类型
date - int 期限天数
code - str 证券代码
codeName - str 证券代码名称
exchangeType - str 市场
fsmpOccupedRate - float 资券占用利率
fineRate - float 罚息利率
fsmpreendRate - float 资券提前归还利率
usedRate - float 资券使用利率
unUusedRate - float 资券占用未使用利率
initDate - int 交易日期
endDate - int 到期日期
enableSloAmountT0 - float T+0可融券数量
enableSloAmountT3 - float T+3可融券数量
srcGroupId - str 来源组编号
applyMode - str 资券申请方式，"1":库存券，"2":专项券
lowDate - int 最低期限天数
库存券约券申请

smt_negotiate_order_async(self, account, src_group_id, order_code, date, amount, apply_rate, dict_param={})
释义

库存券约券申请的异步接口，异步接口如果正常返回了请求序号seq，会收到on_smt_appointment_async_response的反馈
参数

account - StockAccount 资金账号
src_group_id - str 来源组编号
order_code - str 证券代码，如'600000.SH'
date - int 期限天数
amount - int 委托数量
apply_rate - float 资券申请利率
注：目前有如下参数通过一个可缺省的字典传递，键名与参数名称相同

dict_param - dict 可缺省的字典参数
subFareRate - float 提前归还利率
fineRate - float 罚息利率
返回

返回请求序号seq，成功发起申请后的请求序号为大于0的正整数，如果为-1表示发起申请失败
示例


account = StockAccount('1000008', 'CREDIT')
dict_param = {'subFareRate':0.1, 'fineRate':0.1}
#xt_trader为XtQuant API实例对象
seq = xt_trader.smt_negotiate_order_async(account, '', '000001.SZ', 7, 100, 0.2, dict_param)
约券合约查询

smt_query_compact(account)
释义
约券合约查询
参数
account - StockAccount 资金账号
返回
result - list 约券合约信息列表[compact1, compact2, ...]
compact - dict 券源信息，包含以下字段
success - bool
error - str
createDate - int 创建日期
cashcompactId - str 头寸合约编号
oriCashcompactId - str 原头寸合约编号
applyId - str 资券申请编号
srcGroupId - str 来源组编号
comGroupId - str 资券组合编号
finType - str 金融品种
exchangeType - str 市场
code - str 证券代码
codeName - str 证券代码名称
date - int 期限天数
beginCompacAmount - float 期初合约数量
beginCompacBalance - float 期初合约金额
compacAmount - float 合约数量
compacBalance - float 合约金额
returnAmount - float 返还数量
returnBalance - float 返还金额
realBuyAmount - float 回报买入数量
fsmpOccupedRate - float 资券占用利率
compactInterest - float 合约利息金额
compactFineInterest - float 合约罚息金额
repaidInterest - float 已还利息
repaidFineInterest - float 归还罚息
fineRate - float 罚息利率
preendRate - float 资券提前归还利率
compactType - str 资券合约类型
postponeTimes - int 展期次数
compactStatus - str 资券合约状态，"0":未归还，"1":部分归还，"2":提前了结，"3":到期了结，"4":逾期了结，"5":逾期，"9":已作废
lastInterestDate - int 上次结息日期
interestEndDate - int 记息结束日期
validDate - int 有效日期
dateClear - int 清算日期
usedAmount - float 已使用数量
usedBalance - float 使用金额
usedRate - float 资券使用利率
unUusedRate - float 资券占用未使用利率
srcGroupName - str 来源组名称
repaidDate - int 归还日期
preOccupedInterest - float 当日实际应收利息
compactInterestx - float 合约总利息
enPostponeAmount - float 可展期数量
postponeStatus - str 合约展期状态，"0":未审核，"1":审核通过，"2":已撤销，"3":审核不通过
applyMode - str 资券申请方式，"1":库存券，"2":专项券
回调类

class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接状态回调
        :return:
        """
        print("connection lost")
    def on_account_status(self, status):
        """
        账号状态信息推送
        :param response: XtAccountStatus 对象
        :return:
        """
        print("on_account_status")
        print(status.account_id, status.account_type, status.status)
    def on_stock_order(self, order):
        """
        委托信息推送
        :param order: XtOrder对象
        :return:
        """
        print("on order callback:")
        print(order.stock_code, order.order_status, order.order_sysid)
    def on_stock_trade(self, trade):
        """
        成交信息推送
        :param trade: XtTrade对象
        :return:
        """
        print("on trade callback")
        print(trade.account_id, trade.stock_code, trade.order_id)
    def on_order_error(self, order_error):
        """
        下单失败信息推送
        :param order_error:XtOrderError 对象
        :return:
        """
        print("on order_error callback")
        print(order_error.order_id, order_error.error_id, order_error.error_msg)
    def on_cancel_error(self, cancel_error):
        """
        撤单失败信息推送
        :param cancel_error: XtCancelError 对象
        :return:
        """
        print("on cancel_error callback")
        print(cancel_error.order_id, cancel_error.error_id, cancel_error.error_msg)
    def on_order_stock_async_response(self, response):
        """
        异步下单回报推送
        :param response: XtOrderResponse 对象
        :return:
        """
        print("on_order_stock_async_response")
        print(response.account_id, response.order_id, response.seq)
    def on_smt_appointment_async_response(self, response):
        """
        :param response: XtAppointmentResponse 对象
        :return:
        """
        print("on_smt_appointment_async_response")
        print(response.account_id, response.order_sysid, response.error_id, response.error_msg, response.seq)
连接状态回调

on_disconnected()
释义
失去连接时推送信息
参数
无
返回
无
备注
无
账号状态信息推送

on_account_status(data)
释义
账号状态信息变动推送
参数
data - XtAccountStatus 账号状态信息
返回
无
备注
无
委托信息推送

on_stock_order(data)
释义
委托信息变动推送,例如已成交数量，委托状态变化等
参数
data - XtOrder 委托信息
返回
无
备注
无
成交信息推送

on_stock_trade(data)
释义
成交信息变动推送
参数
data - XtTrade 成交信息
返回
无
备注
无
下单失败信息推送

on_order_error(data)
释义
下单失败信息推送
参数
data - XtOrderError 下单失败信息
返回
无
备注
无
撤单失败信息推送

on_cancel_error(data)
释义
撤单失败信息的推送
参数
data - XtCancelError 撤单失败信息
返回
无
备注
无
异步下单回报推送

on_order_stock_async_response(data)
释义
异步下单回报推送
参数
data - XtOrderResponse 异步下单委托反馈
返回
无
备注
无
约券相关异步接口的回报推送

on_smt_appointment_async_response(data)
释义
异步约券相关接口回报推送
参数
data - XtSmtAppointmentResponse 约券相关异步接口的反馈
返回
无
备注
无



1   Token 过期或无效
日志显示：用户已过期, account is expired
影响：交易接口需要有效 Token 才能连接
2  迅投客户端未启动
USERDATA_PATH 指向的路径需要对应已启动的迅投客户端
路径：D:\迅投极速交易终端 睿智融科版\userdata
3  交易权限不足
账户可能只有行情权限，没有交易权限
4  连接超时或网络问题
无法连接到迅投交易服务器