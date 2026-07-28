# Redactable Contract

Redactable Contract هو تطبيق بسيط يساعد على رفع العقود والاطلاع على نصّها، ثم إزالة المعلومات الحساسة أو الشخصية باستخدام الذكاء الاصطناعي مع حفظ بنية العقد وتنسيقه قدر الإمكان.

## ما الذي يقدمه التطبيق؟

- رفع ملفات العقود بصيغة PDF أو TXT
- استخراج النص من الملف المرفوع
- عرض النص في واجهة سهلة باستخدام Streamlit
- استخدام الذكاء الاصطناعي لإزالة المعلومات الحساسة مثل:
  - الأسماء
  - العناوين
  - البريد الإلكتروني
  - أرقام الهواتف
  - أرقام الهوية
  - البيانات المالية
- حفظ التغييرات على مستوى النص مع التحقق من التغييرات عبر blockchain

## التقنيات المستخدمة

- Python
- Streamlit
- OpenAI API
- PyCryptodome
- PyPDF2 / pdfplumber
- python-dotenv

## بنية المشروع

```text
redactable/
├── app.py
├── requirements.txt
├── .env
├── brain/
│   ├── auditor.py
│   └── privacy.py
├── core/
│   ├── blockchain.py
│   ├── crypto_engine.py
│   ├── ocr.py
│   └── trapdoor_init.py
├── services/
│   └── contract_service.py
└── utils/
    └── session.py
```

## المتطلبات

تأكد من أن Python 3.8+ مثبت على جهازك.

## التثبيت

1. أنشئ بيئة افتراضية:

```bash
python -m venv .venv
```

2. فعّل البيئة الافتراضية:

- Windows:

```bash
.venv\Scripts\activate
```

- Linux/macOS:

```bash
source .venv/bin/activate
```

3. ثبّت المكتبات المطلوبة:

```bash
pip install -r requirements.txt
```

4. أنشئ ملف `.env` وأضف مفتاح OpenAI:

```env
OPENAI_API_KEY=your_api_key_here
```

## التشغيل

شغّل التطبيق باستخدام:

```bash
streamlit run app.py
```

## الاستخدام

1. افتح التطبيق في المتصفح.
2. ارفع عقدًا بصيغة PDF أو TXT.
3. راجع النص المستخرج.
4. استخدم زر "Remove Sensitive Information (AI)" لإزالة المعلومات الحساسة.
5. احفظ التعديلات إذا رغبت في ذلك.

## ملاحظات مهمة

- لا تقم بمشاركة مفتاح OpenAI أو أي بيانات حساسة في GitHub.
- يُفضّل إضافة ملف `.env` إلى `.gitignore`.
- بعض الملفات مثل `__pycache__` وملفات `.pyc` لا يجب تضمينها في المستودع.

## الترخيص

هذا المشروع مخصص للاستخدام التعليمي والتجريبي.
