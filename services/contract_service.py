from Crypto.Util import number

from brain.privacy import remove_sensitive_information
from core.blockchain import Block


def _generate_random_r(n):
    r = number.getRandomRange(2, n - 1)
    while number.GCD(r, n) != 1:
        r = number.getRandomRange(2, n - 1)
    return r


def create_contract_block(contract_text, sender, recipient, chain):
    prev_hash = chain.latest_block().hash if chain.latest_block() else 0
    r = _generate_random_r(sender.n)
    block = Block(
        sender.name,
        recipient.name,
        contract_text,
        prev_hash,
        r,
        sender.n,
    )
    chain.add_block(block)
    return block


def apply_manual_redaction(block, edited_text, user):
    old_hash = block.hash
    block.manual_edit(edited_text, user.p, user.q)
    return old_hash, block.hash


def apply_ai_redaction(block, text, user):
    analysis = remove_sensitive_information(text)
    redacted_text = analysis["redacted_text"]
    old_hash = block.hash
    block.redact(redacted_text, user.p, user.q)
    return old_hash, block.hash, analysis
