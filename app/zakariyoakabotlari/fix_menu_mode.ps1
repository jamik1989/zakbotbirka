$ErrorActionPreference = "Stop"

$path = ".\app\handlers\auth.py"
if (!(Test-Path $path)) {
    Write-Host "❌ auth.py topilmadi: $path"
    exit 1
}

# backup
Copy-Item $path "$path.bak" -Force
$content = Get-Content $path -Raw -Encoding UTF8

# 1) APP_MODE importini qo'shish (agar yo'q bo'lsa)
if ($content -notmatch "APP_MODE") {
    $content = $content -replace "(from\s+\.\.config\s+import\s+[^\r\n]+)", '$1, APP_MODE'
}

# 2) helper menu funksiyasini qo'shish (agar yo'q bo'lsa)
if ($content -notmatch "def\s+_main_menu_keyboard\s*\(") {
$helper = @"

def _main_menu_keyboard():
    from telegram import ReplyKeyboardMarkup, KeyboardButton
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

"@
    $content = $helper + $content
}

# 3) Eski matnni mode-aware matnga almashtirish
$content = $content -replace "Kerakli bo.?limlarni tanlang:\s*/tasdiq yoki /takror\.", "{menu_hint}"

# 4) Agar menu_hint ishlatilmagan bo'lsa, login success joylariga qo'shish
if ($content -notmatch "menu_hint\s*=\s*_menu_hint_text\(\)") {
    # eng ehtiyotkor variant: mavjud "Xush kelibsiz" bloklaridan oldin menu_hint yaratiladi
    $content = $content -replace "(Xush kelibsiz[^\r\n]*\r?\n)", '$1    menu_hint = _menu_hint_text()`r`n'
}

# 5) Hardcoded reply keyboardni mode keyboardga almashtirish (faqat auth.py ichida)
# Juda keng regex ishlatmaslik uchun 2 ta aniq naqsh:
$content = $content -replace "reply_markup\s*=\s*ReplyKeyboardMarkup\(\s*\[\s*\[\s*KeyboardButton\(""/tasdiq""\)\s*,\s*KeyboardButton\(""/takror""\)\s*\]\s*\][\s\S]*?\)", "reply_markup=_main_menu_keyboard()"
$content = $content -replace "reply_markup\s*=\s*ReplyKeyboardMarkup\(\s*\[\s*\[\s*KeyboardButton\(""/kiritish""\)\s*\]\s*\][\s\S]*?\)", "reply_markup=_main_menu_keyboard()"

# 6) Agar text ichida {menu_hint} qolgan bo'lsa, f-stringga o'tkazamiz
$content = $content -replace "(""✅ Xush kelibsiz![\s\S]*?)\{menu_hint\}", '$1{menu_hint}'
$content = $content -replace "reply_text\(\s*(""✅ Xush kelibsiz![\s\S]*?\")", 'reply_text(f$1'

Set-Content $path $content -Encoding UTF8

Write-Host "✅ Patch yozildi: $path"
Write-Host "✅ Backup: $path.bak"
Write-Host "Endi tekshiring:"
Write-Host "   python -m app.main"
