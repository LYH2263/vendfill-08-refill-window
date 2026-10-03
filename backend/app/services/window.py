"""点位补货时段窗：一天内分钟数的半开区间 [start, end)。

放行口径唯一定义于此，点位接口、补货生成接口、补货单查询全部共用：
- start/end 均为 None  -> 不限时段，随时可生成（与现网一致）
- 仅一端为空          -> 非法窗（保存时即被拒绝；若库中混入则按窗外处理）
- 合法窗              -> start <= 当前分钟 < end 才放行
"""
from __future__ import annotations

from datetime import datetime

MINUTES_PER_DAY = 1440

# 窗外失败原因：只写这一句，不得改写成满仓或无货道
REASON_OUTSIDE_WINDOW = "不在补货时段"


def current_minute_of_day(now: datetime | None = None) -> int:
    """当前时刻在一天内的分钟数（0..1439），本地墙钟。"""
    now = now or datetime.now()
    return now.hour * 60 + now.minute


def validate_window(start: int | None, end: int | None) -> str | None:
    """返回 None 表示合法，否则返回拒绝原因。合法窗：0 <= start < end <= 1440。"""
    if start is None and end is None:
        return None
    if start is None or end is None:
        return "开始与结束分钟需同时填写或同时留空"
    if not (0 <= start < MINUTES_PER_DAY):
        return "开始分钟越界（0..1439）"
    if not (0 < end <= MINUTES_PER_DAY):
        return "结束分钟越界（1..1440）"
    if end <= start:
        return "结束分钟必须大于开始分钟"
    return None


def is_window_open(start: int | None, end: int | None, now_min: int | None = None) -> bool:
    """当前时刻是否落在补货时段窗内（半开区间 [start, end)）。"""
    if start is None and end is None:
        return True
    if start is None or end is None:
        return False
    if now_min is None:
        now_min = current_minute_of_day()
    return start <= now_min < end
