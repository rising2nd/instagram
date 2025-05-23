import datetime
from dateutil.parser import isoparse

def convert_timestamp_to_jst_formatted(timestamp_str):
    """
    UTC タイムスタンプ文字列を JST の YYYY-MM-DD HH:MM 形式に変換します。

    Args:
        timestamp_str (str): UTC タイムスタンプの文字列 (例: '2025-04-23T12:51:44+0000').

    Returns:
        str: JST 形式のタイムスタンプ文字列 (例: '2025-04-23 21:51').
             変換に失敗した場合は None を返します。
    """
    jst_offset = datetime.timedelta(hours=9)
    try:
        # dateutil.parser.isoparse を使用して解析
        utc_dt = isoparse(timestamp_str)
        # タイムゾーン情報がない場合に UTC を指定（もしあればそのまま）
        if utc_dt.tzinfo is None or utc_dt.tzinfo.utcoffset(utc_dt) is None:
            utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
        # UTC に JST のオフセットを加算
        jst_dt = utc_dt + jst_offset
        # 指定の形式にフォーマット
        return jst_dt.strftime('%Y-%m-%d %H:%M')
    except ValueError:
        print(f"Warning: Could not parse timestamp string: {timestamp_str}")
        return None