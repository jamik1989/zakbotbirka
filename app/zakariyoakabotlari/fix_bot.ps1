$ErrorActionPreference = "Stop"

Write-Host "===> 1) Files backup..."
Copy-Item .\app\main.py .\app\main.py.bak -Force
Copy-Item .\app\handlers\order.py .\app\handlers\order.py.bak -Force

Write-Host "===> 2) Patch main.py..."
$mainPath = ".\app\main.py"
$main = Get-Content $mainPath -Raw

# 2.1) order import ichiga on_review_action qo'shish
if ($main -notmatch "on_review_action") {
    $main = $main -replace "(\s*STEP_REVIEW,\s*\r?\n)", "    STEP_REVIEW,`r`n    on_review_action,`r`n"
}

# 2.2) STEP_REVIEW handlerni to'g'rilash
$main = $main -replace "STEP_REVIEW:\s*\[CallbackQueryHandler\(takror_review_action,\s*pattern=r""\^rv:""\)\],", "STEP_REVIEW: [CallbackQueryHandler(on_review_action, pattern=r""^rv:"")],"

Set-Content $mainPath $main -Encoding UTF8

Write-Host "===> 3) Patch order.py..."
$orderPath = ".\app\handlers\order.py"
$order = Get-Content $orderPath -Raw

# cancel funksiyasi bo'lmasa qo'shamiz
if ($order -notmatch "async\s+def\s+cancel\s*\(") {
    $cancelFunc = @"

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Bekor qilindi.", reply_markup=_menu_keyboard())
    _cleanup_after_done(context)
    return ConversationHandler.END
"@
    $order = $order + "`r`n" + $cancelFunc
    Set-Content $orderPath $order -Encoding UTF8
}

Write-Host "===> 4) Run app..."
python -m app.main
