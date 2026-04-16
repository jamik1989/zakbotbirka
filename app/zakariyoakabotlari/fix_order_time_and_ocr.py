@'
from pathlib import Path
import re

p = Path("app/handlers/order.py")
if not p.exists():
    raise SystemExit("File not found: app/handlers/order.py")

src = p.read_text(encoding="utf-8")
orig = src

# 1) _tg_now_as_ms_parts
src = re.sub(
    r"def _tg_now_as_ms_parts\(\) -> Tuple\[str, str\]:\n(?:    .*\n)+?",
    """def _tg_now_as_ms_parts() -> Tuple[str, str]:
    dt_tg = datetime.now(TG_TZ)
    dt_ms = dt_tg.astimezone(MS_TZ)
    return dt_ms.strftime("%Y-%m-%d"), dt_ms.strftime("%H:%M:%S")

""",
    src,
    flags=re.MULTILINE
)

# 2) _fmt_ms_to_tg
src = re.sub(
    r"def _fmt_ms_to_tg\(date_iso: Optional\[str\], time_hms: Optional\[str\]\) -> str:\n(?:    .*\n)+?",
    """def _fmt_ms_to_tg(date_iso: Optional[str], time_hms: Optional[str]) -> str:
    if not date_iso:
        return "TOPILMADI"
    raw = f"{date_iso} {time_hms or '00:00:00'}"
    try:
        dt_ms = datetime.strptime(raw, "%Y-%m-%d %H:%M:%S").replace(tzinfo=MS_TZ)
        dt_tg = dt_ms.astimezone(TG_TZ)
        return dt_tg.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return raw

""",
    src,
    flags=re.MULTILINE
)

# 3) OCR line -> try/except (handle_check_optional ichida)
old_line = "    amount, date_iso, time_hms, raw_text = detect_amount_date_time(str(img_path))"
if old_line in src:
    src = src.replace(
        old_line,
        """    try:
        amount, date_iso, time_hms, raw_text = detect_amount_date_time(str(img_path))
    except Exception:
        amount, date_iso, time_hms, raw_text = None, None, None, """""
    )

if src == orig:
    print("No changes made (patterns not found).")
else:
    backup = p.with_suffix(".py.bak")
    backup.write_text(orig, encoding="utf-8")
    p.write_text(src, encoding="utf-8")
    print("OK: Patched app/handlers/order.py")
    print(f"Backup: {backup}")
'@ | Set-Content .\fix_order_time_and_ocr.py -Encoding UTF8
