import os
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from brain.auditor import audit_contract
from core.blockchain import Block, User, ChatChain
from Crypto.Util import number

DATA_PATH = os.path.join("data", "contracts.json")

# تحميل العقود من قاعدة البيانات (ملف JSON)
def load_contracts():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# حفظ العقود إلى قاعدة البيانات
def save_contracts(contracts):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(contracts, f, ensure_ascii=False, indent=2)

# عملية الحذف الآمن التلقائي للعقود المنتهية
def auto_redact_expired_contracts():
    contracts = load_contracts()
    today = datetime.now().strftime("%Y-%m-%d")
    changed = False
    for contract in contracts:
        if contract.get("status") == "Active" and contract.get("expiry_date") == today:
            # تنفيذ الحذف الآمن
            user = User(contract["sender"])
            prev_hash = contract["prev_hash"]
            r = contract["r"]
            n = contract["n"]
            block = Block(contract["sender"], contract["recipient"], contract["text"], prev_hash, r, n)
            # استخدم النص الممسوح من التحليل
            redacted_text = contract["redacted_text"]
            block.redact(redacted_text, user.p, user.q)
            # تحديث العقد
            contract["text"] = redacted_text
            contract["r"] = block.r
            contract["hash"] = block.hash
            contract["status"] = "Redacted (Expired)"
            changed = True
    if changed:
        save_contracts(contracts)
        print("تم تحديث العقود المنتهية تلقائياً.")

# جدولة الفحص اليومي
scheduler = BackgroundScheduler()
scheduler.add_job(auto_redact_expired_contracts, 'interval', days=1, next_run_time=datetime.now())
scheduler.start()

# لإيقاف الجدولة عند إنهاء البرنامج
import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    print("مراقبة العقود قيد التشغيل بالخلفية...")
    import time
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("تم إيقاف المراقبة.")
