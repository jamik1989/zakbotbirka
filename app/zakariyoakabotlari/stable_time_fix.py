from datetime import datetime
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Tashkent")


def tashkent_now() -> datetime:
    return datetime.now(TZ)


def ensure_tashkent(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=TZ)
    return dt.astimezone(TZ)


def fmt_moysklad_moment(dt: datetime | None) -> str:
    if dt is None:
        return ""
    dt = ensure_tashkent(dt)
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def fmt_human(value) -> str:
    if value is None:
        return ""
    if isinstance(value, datetime):
        return ensure_tashkent(value).strftime("%d.%m.%Y %H:%M")
    return str(value)


# backward-compat alias
fix_import_fmt_human = fmt_human
