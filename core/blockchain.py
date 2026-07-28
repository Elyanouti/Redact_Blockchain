from datetime import datetime

from core.crypto_engine import chameleon_hash, find_collision, str_to_bin


class Block:
    def __init__(self, sender, recipient, message_text, prev_hash, r, n):
        self.sender = sender
        self.recipient = recipient
        self.message_text = message_text
        self.message_bin = str_to_bin(message_text)
        self.prev_hash = prev_hash
        self.r = r
        self.n = n
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        combined = bin(self.prev_hash)[2:] + self.message_bin
        self.hash = chameleon_hash(combined, self.r, self.n)

    def redact(self, new_text, p, q):
        new_bin = str_to_bin(new_text)
        combined_old = bin(self.prev_hash)[2:] + self.message_bin
        combined_new = bin(self.prev_hash)[2:] + new_bin

        r_new = find_collision(
            combined_old,
            self.r,
            combined_new,
            self.n,
            p,
            q,
        )

        self.message_text = new_text
        self.message_bin = new_bin
        self.r = r_new
        self.hash = chameleon_hash(combined_new, r_new, self.n)

    def manual_edit(self, new_text, p, q):
        self.redact(new_text, p, q)

    def selective_redact(self, original_text, selected_items, p, q):
        new_text = original_text
        for item in selected_items:
            if item.strip():
                new_text = new_text.replace(item, "[REDACTED]")

        self.redact(new_text, p, q)
        return new_text

    def verify_integrity(self, old_hash):
        return self.hash == old_hash


class ChatChain:
    def __init__(self):
        self.chain = []

    def add_block(self, block):
        self.chain.append(block)

    def latest_block(self):
        if len(self.chain) == 0:
            return None
        return self.chain[-1]

    def get_block(self, index):
        if index < 0 or index >= len(self.chain):
            return None
        return self.chain[index]


class User:
    def __init__(self, name, p, q, n):
        self.name = name
        self.p = p
        self.q = q
        self.n = n

    @classmethod
    def create(cls, name, p, q, n):
        return cls(name, p, q, n)

    def send_message(self, recipient, message_text, chain):
        prev_hash = chain.latest_block().hash if chain.latest_block() else 0
        r = self._generate_random_r()
        block = Block(
            self.name,
            recipient.name,
            message_text,
            prev_hash,
            r,
            self.n,
        )
        chain.add_block(block)
        return block

    def edit_message(self, chain, index, new_text):
        block = chain.get_block(index)
        if block is None:
            raise Exception("Invalid block index.")
        if block.sender != self.name:
            raise Exception("Permission denied.")
        old_hash = block.hash
        block.redact(new_text, self.p, self.q)
        return old_hash, block.hash

    def manual_edit(self, block, new_text):
        if block.sender != self.name:
            raise Exception("Permission denied.")
        old_hash = block.hash
        block.manual_edit(new_text, self.p, self.q)
        return old_hash, block.hash

    def selective_redaction(self, block, original_text, selected_items):
        if block.sender != self.name:
            raise Exception("Permission denied.")
        old_hash = block.hash
        new_text = block.selective_redact(original_text, selected_items, self.p, self.q)
        return old_hash, block.hash, new_text

    def verify_block(self, block, old_hash):
        return block.verify_integrity(old_hash)

    def _generate_random_r(self):
        from Crypto.Util import number

        r = number.getRandomRange(2, self.n - 1)
        while number.GCD(r, self.n) != 1:
            r = number.getRandomRange(2, self.n - 1)
        return r
