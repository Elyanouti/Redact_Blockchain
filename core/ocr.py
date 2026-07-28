def extract_text_from_uploaded_file(uploaded_file):
    uploaded_file.seek(0)
    if uploaded_file.name.lower().endswith(".txt"):
        return uploaded_file.read().decode("utf-8")

    try:
        import PyPDF2

        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        uploaded_file.seek(0)
        import pdfplumber

        with pdfplumber.open(uploaded_file) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
