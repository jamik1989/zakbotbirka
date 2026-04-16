@'
from pathlib import Path
import re

p = Path("app/handlers/auth.py")
if not p.exists():
    raise SystemExit("auth.py topilmadi: app/handlers/auth.py")

src = p.read_text(encoding="utf-8")
orig = src

# 1) APP_MODE importi
if "APP_MODE" not in src:
    src = re.sub(
        r"(from\s+\.\.config\s+import\s+[^\n]+)",
        r"\1, APP_MODE",
        src,
        count=1,
    )

# 2) Helperlar (agar yo'q bo'lsa boshiga qo'shamiz)
if "def _main_menu_keyboard(" not in src:
    helper = '''
from telegram import ReplyKeyboardMarkup, KeyboardButton

def _main_menu_keyboard():
    if APP_MODE == "order_bot":
        return ReplyKeyboardMarkup(
            [[KeyboardButton("/kiritish")]],
            resize_keyboard=True,
            one_time_keyboard=False,
            selective=True,
        )
    if APP_MODE == "confirm_bot":
        return ReplyKeyboardMarkup(
            [[KeyboardButton("/tasdiq"), KeyboardButton("/takror")]],
            resize_keyboard=True,
            one_time_keyboard=False,
            selective=True,
        )
    return ReplyKeyboardMarkup(
        [[KeyboardButton("/start")]],
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=True,
    )

def _menu_hint_text():
    if APP_MODE == "order_bot":
        return "Kerakli bo‘limni tanlang: /kiritish"
    return "Kerakli bo‘limlarni tanlang: /tasdiq yoki /takror"
'''
    src = helper + "\n" + src

# 3) Matnni dynamic qilish
src = src.replace(
    "Kerakli bo‘limlarni tanlang: /tasdiq yoki /takror.",
    "{menu_hint}"
)

# 4) Agar login success blokida menu_hint yo'q bo'lsa, qo'shamiz
if "menu_hint = _menu_hint_text()" not in src:
    src = src.replace(
        "await update.message.reply_text(",
        "menu_hint = _menu_hint_text()\n    await update.message.reply_text(",
        1
    )

# 5) Hardcoded tasdiq/takror keyboardni dynamicga almashtirish
src = re.sub(
    r"reply_markup\s*=\s*ReplyKeyboardMarkup\(\s*\[\s*\[\s*KeyboardButton\(\"/tasdiq\"\)\s*,\s*KeyboardButton\(\"/takror\"\)\s*\]\s*\]\s*,[\s\S]*?\)",
    "reply_markup=_main_menu_keyboard()",
    src
)

# 6) Agar xabar f-string bo'lmasa, f-stringga o'tkazish
src = src.replace('await update.message.reply_text("✅ Xush kelibsiz, {name}!\\n{menu_hint}"',
                  'await update.message.reply_text(f"✅ Xush kelibsiz, {name}!\\n{menu_hint}"')
src = src.replace('await update.message.reply_text("✅ Xush kelibsiz!\\n{menu_hint}"',
                  'await update.message.reply_text(f"✅ Xush kelibsiz!\\n{menu_hint}"')

if src == orig:
    print("Hech narsa o'zgarmadi (pattern topilmadi).")
else:
    backup = p.with_suffix(".py.bak")
    backup.write_text(orig, encoding="utf-8")
    p.write_text(src, encoding="utf-8")
    print("OK: auth.py patchlandi.")
    print(f"Backup: {backup}")
'@ | Set-Content .\fix_auth_menu.py -Encoding UTF8
