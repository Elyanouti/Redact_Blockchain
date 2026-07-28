import streamlit as st

from core.ocr import extract_text_from_uploaded_file
from services.contract_service import (
    apply_ai_redaction,
    apply_manual_redaction,
    create_contract_block,
)
from utils.session import initialize_session_state


def main():
    st.set_page_config(page_title="Redactable Contract", layout="wide")
    st.title("Redactable Contract")

    initialize_session_state()

    alice = st.session_state.alice
    bob = st.session_state.bob
    chain = st.session_state.chain

    # --- Upload File ---
    uploaded_file = st.file_uploader("Upload Contract", type=["pdf", "txt"])

    if uploaded_file:
        extracted_text = extract_text_from_uploaded_file(uploaded_file)

        if extracted_text and extracted_text != st.session_state.extracted_text:
            st.session_state.extracted_text = extracted_text
            st.session_state.contract_text = extracted_text
            new_block = create_contract_block(
                extracted_text,
                alice,
                bob,
                chain,
            )
            st.session_state.block = new_block
            st.session_state.original_hash = new_block.hash
            st.session_state.editable = False

    block = st.session_state.block
    if block is None:
        return

    if not isinstance(st.session_state.contract_text, str):
        try:
            st.session_state.contract_text = str(st.session_state.contract_text)
        except Exception:
            st.session_state.contract_text = ""

    if not st.session_state.contract_text:
        st.session_state.contract_text = block.message_text if isinstance(block.message_text, str) else ""

    if not isinstance(st.session_state.sensitive_items, list):
        try:
            st.session_state.sensitive_items = list(st.session_state.sensitive_items)
        except Exception:
            st.session_state.sensitive_items = []

    st.session_state.sensitive_items = [str(item) for item in st.session_state.sensitive_items]

    def save_manual():
        block = st.session_state.block
        apply_manual_redaction(block, st.session_state.contract_text, st.session_state.alice)
        st.session_state.contract_text = block.message_text
        st.session_state.current_hash = block.hash
        st.session_state.editable = False
        st.session_state.block = block

    def remove_sensitive_info():
        block = st.session_state.block
        _, new_hash, analysis = apply_ai_redaction(block, st.session_state.contract_text, st.session_state.alice)
        st.session_state.contract_text = block.message_text
        st.session_state.current_hash = new_hash
        st.session_state.editable = False
        st.session_state.block = block
        st.session_state.sensitive_items = [
            item.get("original", "") for item in analysis.get("redacted_items", []) if item.get("original", "")
        ]

    # --- Inject CSS for editable mode (white background, black text) ---
    if st.session_state.editable:
        st.markdown(
            """
            <style>
            [data-testid="stTextArea"] textarea {
                background-color: white !important;
                color: black !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )

    # --- Sensitive Information Section ---
    if st.session_state.sensitive_items:
        sensitive_items = st.session_state.sensitive_items
        if not isinstance(sensitive_items, list):
            sensitive_items = [str(sensitive_items)]
        sensitive_items = [str(item) for item in sensitive_items]

        st.subheader("Sensitive Information to Remove")
        st.markdown(
            f"""
            <style>
            .sensitive-box {{
                background-color: #f5f0e6;
                border: 1px solid #d3c9b8;
                border-radius: 8px;
                padding: 14px;
                color: #2f2b24;
                font-family: monospace;
                white-space: pre-wrap;
                min-height: 150px;
            }}
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sensitive-box">' +
            "<br>".join([item.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") for item in sensitive_items]) +
            '</div>',
            unsafe_allow_html=True,
        )

    # --- Single Extracted Contract Text Area ---
    st.subheader("Extracted Contract")
    st.text_area(
        "",
        value=st.session_state.contract_text,
        height=360,
        disabled=not st.session_state.editable,
        key="contract_text",
    )

    # --- Two Buttons ---
    col1, col2 = st.columns(2)

    with col1:
        if not st.session_state.editable:
            st.button("Manual Redaction", use_container_width=True, on_click=lambda: st.session_state.update(editable=True))
        else:
            st.button("Save Changes", use_container_width=True, on_click=save_manual)

    with col2:
        st.button("Remove Sensitive Information (AI)", use_container_width=True, on_click=remove_sensitive_info)

    # --- Hashes ---
    st.divider()
    st.markdown("**Original Hash**")
    st.code(str(st.session_state.original_hash))

    current_hash = st.session_state.current_hash
    if current_hash is not None:
        st.markdown("**Redacted Hash**")
        st.code(str(current_hash))

        validity = "VALID" if current_hash == st.session_state.original_hash else "INVALID"
        if validity == "VALID":
            st.success(f"Status: {validity}")
        else:
            st.error(f"Status: {validity}")


if __name__ == "__main__":
    main()
