import os
import json
from core.crypto_engine import generate_keys

def ensure_trapdoor_key(env_path=".env"):
    # تحقق إذا كان TRAPDOOR_KEY موجود بالفعل
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f:
            f.write("")
    with open(env_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith("TRAPDOOR_KEY="):
            found = True
            if line.strip() == "TRAPDOOR_KEY=":
                # توليد مفاتيح جديدة
                p, q, n = generate_keys()
                key_json = json.dumps({"p": str(p), "q": str(q)})
                lines[i] = f"TRAPDOOR_KEY={key_json}\n"
            break
    if not found:
        # أضف السطر إذا لم يكن موجوداً
        p, q, n = generate_keys()
        key_json = json.dumps({"p": str(p), "q": str(q)})
        lines.append(f"TRAPDOOR_KEY={key_json}\n")
    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

if __name__ == "__main__":
    try:
        ensure_trapdoor_key()
        print("تم التأكد من وجود TRAPDOOR_KEY في .env.")
    except Exception as e:
        print("حدث خطأ أثناء توليد TRAPDOOR_KEY:", e)
