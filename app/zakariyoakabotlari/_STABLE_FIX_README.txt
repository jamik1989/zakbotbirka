MANUAL CHECK

1) Naqt:
   dt = tashkent_now()

2) Karta:
   receipt_dt = extract_receipt_datetime(receipt_text)
   dt = ensure_tashkent(receipt_dt) if receipt_dt else tashkent_now()

3) MoySklad:
   payload["moment"] = fmt_moysklad_moment(dt)

4) Guruh matni:
   fmt_human(dt)

5) Chek summasi:
   amount = extract_max_amount(receipt_text) or amount
