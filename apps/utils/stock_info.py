"""
Stock metadata helpers.

Currently provides a minimal `get_stock_region` implementation used by
`apps.account.views.get_region_data`.
You can later replace this with a real data source (DB, API, etc.).
"""

from typing import Literal


Region = Literal["上海", "深圳", "北京", "广州", "杭州", "其他"]


def get_stock_region(stock_code: str) -> Region:
    """
    Return the listing region for a given stock code.

    This is a placeholder implementation that infers region from the code
    suffix / prefix. Adjust the rules to match your real business logic.
    """
    if not stock_code:
        return "其他"

    code = stock_code.upper()

    # Very rough mapping rules – customize as needed
    if code.endswith(".SH"):
        return "上海"
    if code.endswith(".SZ"):
        return "深圳"

    # Example prefixes – tweak/remove if not needed
    if code.startswith("BJ"):
        return "北京"

    return "其他"


