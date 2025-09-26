#!/bin/bash
# API自动触发数据下载功能 - curl命令示例

echo "🚀 API自动触发数据下载功能测试"
echo "=================================="

# 基础URL
BASE_URL="http://localhost:8000"
API_URL="$BASE_URL/api/asset_comparison/"

echo "📡 测试1: 下载贵州茅台和平安银行的日线数据"
echo "----------------------------------------"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["600519.SH", "000001.SZ"],
    "period": "1d",
    "start_time": "2024-01-01 00:00:00",
    "end_time": "2024-12-31 23:59:59"
  }' \
  | python -m json.tool

echo -e "\n\n📡 测试2: 下载小时线数据"
echo "------------------------"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["600519.SH"],
    "period": "1h",
    "start_time": "2024-12-01 00:00:00",
    "end_time": "2024-12-31 23:59:59"
  }' \
  | python -m json.tool

echo -e "\n\n📡 测试3: 下载多只股票数据"
echo "--------------------------"

curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "symbols": ["600519.SH", "000001.SZ", "000002.SZ", "600036.SH"],
    "period": "1d",
    "start_time": "2024-11-01 00:00:00",
    "end_time": "2024-12-31 23:59:59"
  }' \
  | python -m json.tool

echo -e "\n\n📡 测试4: 获取API信息"
echo "-------------------"

curl -X GET "$API_URL" \
  -H "Content-Type: application/json" \
  | python -m json.tool

echo -e "\n\n✅ 测试完成!"
echo "💡 提示: 查看Django服务器日志可以看到数据下载过程"


