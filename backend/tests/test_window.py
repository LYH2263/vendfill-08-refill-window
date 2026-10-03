from app.services.window import (
    MINUTES_PER_DAY,
    current_minute_of_day,
    is_window_open,
    validate_window,
)


def test_unrestricted_when_both_empty():
    assert validate_window(None, None) is None
    assert is_window_open(None, None) is True
    assert is_window_open(None, None, now_min=0) is True
    assert is_window_open(None, None, now_min=1439) is True


def test_half_open_interval():
    # [600, 660)：起点含、终点不含
    assert is_window_open(600, 660, now_min=600) is True
    assert is_window_open(600, 660, now_min=659) is True
    assert is_window_open(600, 660, now_min=660) is False
    assert is_window_open(600, 660, now_min=599) is False
    assert is_window_open(600, 660, now_min=0) is False


def test_full_day_window():
    assert validate_window(0, MINUTES_PER_DAY) is None
    assert is_window_open(0, MINUTES_PER_DAY, now_min=0) is True
    assert is_window_open(0, MINUTES_PER_DAY, now_min=1439) is True


def test_invalid_windows_rejected():
    assert validate_window(600, 600) is not None      # 结束不大于开始
    assert validate_window(660, 600) is not None      # 结束小于开始
    assert validate_window(-1, 100) is not None       # 开始越界
    assert validate_window(0, 1441) is not None       # 结束越界
    assert validate_window(1440, 1441) is not None    # 开始越界
    assert validate_window(100, None) is not None     # 只有一端
    assert validate_window(None, 100) is not None     # 只有一端


def test_edge_minutes_valid():
    assert validate_window(0, 1) is None
    assert validate_window(1439, 1440) is None
    assert is_window_open(1439, 1440, now_min=1439) is True
    assert is_window_open(1439, 1440, now_min=0) is False


def test_current_minute_of_day_range():
    assert 0 <= current_minute_of_day() < MINUTES_PER_DAY
