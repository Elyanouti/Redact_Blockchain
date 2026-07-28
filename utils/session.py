import streamlit as st
from core.blockchain import ChatChain, User
from core.crypto_engine import generate_keys


def initialize_session_state():
    if "alice" not in st.session_state:
        p, q, n = generate_keys()
        st.session_state.alice = User("Alice", p, q, n)

    if "bob" not in st.session_state:
        p, q, n = generate_keys()
        st.session_state.bob = User("Bob", p, q, n)

    if "chain" not in st.session_state:
        st.session_state.chain = ChatChain()

    if "block" not in st.session_state:
        st.session_state.block = None

    if "editable" not in st.session_state:
        st.session_state.editable = False

    if "original_hash" not in st.session_state:
        st.session_state.original_hash = None

    if "current_hash" not in st.session_state:
        st.session_state.current_hash = None

    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""

    if "contract_text" not in st.session_state:
        st.session_state.contract_text = ""
    
    if "original_text" not in st.session_state:
        st.session_state.original_text = ""

    if "modified_text" not in st.session_state:
        st.session_state.modified_text = ""

    if "hash_history" not in st.session_state:
        st.session_state.hash_history = []

    if "ai_redact_pending" not in st.session_state:
        st.session_state.ai_redact_pending = False

    if "sensitive_items" not in st.session_state:
        st.session_state.sensitive_items = []

    if "manual_redact_pending" not in st.session_state:
        st.session_state.manual_redact_pending = False
