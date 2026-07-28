from Crypto.Util import number
from datetime import datetime

# ==========================================================
# Text ↔ Binary conversion
# ==========================================================

def str_to_bin(s):
    return ''.join(format(ord(c), '08b') for c in s)


def bin_to_str(b):
    chars = [chr(int(b[i:i+8], 2)) for i in range(0, len(b), 8)]
    return ''.join(chars)


# ==========================================================
# Chameleon Hash
# ==========================================================

def generate_keys(bits=256):
    while True:
        p = number.getPrime(bits)
        if p % 8 == 3:
            break

    while True:
        q = number.getPrime(bits)
        if q % 8 == 7:
            break

    n = p * q

    return p, q, n


def f0(x, n):
    return pow(x, 2, n)


def f1(x, n):
    return (4 * pow(x, 2, n)) % n


def chameleon_hash(m, r, n):

    h = pow(r, 2, n)

    for bit in m:

        if bit == "0":
            h = f0(h, n)
        else:
            h = f1(h, n)

    return h


def mod_sqrt(a, p, q):

    rp = pow(a, (p + 1) // 4, p)
    rq = pow(a, (q + 1) // 4, q)

    yp = number.inverse(p, q)
    yq = number.inverse(q, p)

    return (rp * q * yq + rq * p * yp) % (p * q)


def inverse_f(bit, y, n, p, q):

    if bit == "0":
        return mod_sqrt(y, p, q)

    inv4 = pow(4, -1, n)

    return mod_sqrt((y * inv4) % n, p, q)


def find_collision(m1, r1, m2, n, p, q):

    h = chameleon_hash(m1, r1, n)

    r2 = h

    for bit in reversed(m2):
        r2 = inverse_f(bit, r2, n, p, q)

    return mod_sqrt(r2, p, q)


# ==========================================================
# Block
# ==========================================================

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

        combined = bin(prev_hash)[2:] + self.message_bin

        self.hash = chameleon_hash(combined, r, n)

    # ======================================================
    # Main Redaction
    # ======================================================

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
            q
        )

        self.message_text = new_text
        self.message_bin = new_bin
        self.r = r_new

        self.hash = chameleon_hash(
            combined_new,
            r_new,
            self.n
        )

    # ======================================================
    # Manual Edit
    # ======================================================

    def manual_edit(self, new_text, p, q):

        """
        User edits any part of the contract.
        """

        self.redact(
            new_text,
            p,
            q
        )

    # ======================================================
    # Selective Redaction
    # ======================================================

    def selective_redact(
        self,
        original_text,
        selected_items,
        p,
        q
    ):

        new_text = original_text

        for item in selected_items:

            if item.strip():

                new_text = new_text.replace(
                    item,
                    "[REDACTED]"
                )

        self.redact(
            new_text,
            p,
            q
        )

        return new_text

    # ======================================================
    # Integrity Verification
    # ======================================================

    def verify_integrity(self, old_hash):

        return self.hash == old_hash

# ==========================================================
# Blockchain
# ==========================================================

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


# ==========================================================
# User
# ==========================================================

class User:

    def __init__(self, name):

        self.name = name
        self.p, self.q, self.n = generate_keys()

    # ------------------------------------------------------

    def send_message(self, recipient, message_text, chain):

        prev_hash = chain.chain[-1].hash if chain.chain else 0

        r = number.getRandomRange(2, self.n - 1)

        while number.GCD(r, self.n) != 1:
            r = number.getRandomRange(2, self.n - 1)

        block = Block(
            self.name,
            recipient.name,
            message_text,
            prev_hash,
            r,
            self.n
        )

        chain.add_block(block)

        return block

    # ------------------------------------------------------

    def edit_message(self, chain, index, new_text):

        block = chain.get_block(index)

        if block is None:
            raise Exception("Invalid block index.")

        if block.sender != self.name:
            raise Exception("Permission denied.")

        old_hash = block.hash

        block.redact(
            new_text,
            self.p,
            self.q
        )

        return old_hash, block.hash

    # ------------------------------------------------------

    def manual_edit(self, block, new_text):

        if block.sender != self.name:
            raise Exception("Permission denied.")

        old_hash = block.hash

        block.manual_edit(
            new_text,
            self.p,
            self.q
        )

        return old_hash, block.hash

    # ------------------------------------------------------

    def selective_redaction(
        self,
        block,
        original_text,
        selected_items
    ):

        if block.sender != self.name:
            raise Exception("Permission denied.")

        old_hash = block.hash

        new_text = block.selective_redact(
            original_text,
            selected_items,
            self.p,
            self.q
        )

        return old_hash, block.hash, new_text

    # ------------------------------------------------------

    def verify_block(self, block, old_hash):

        return block.verify_integrity(old_hash)


# ==========================================================
# Test
# ==========================================================

if __name__ == "__main__":

    chain = ChatChain()

    alice = User("Alice")
    bob = User("Bob")

    print("Creating block...")

    block = alice.send_message(
        bob,
        "This contract is signed between ABC Company and Mohamed Ali for 50000 USD.",
        chain
    )

    print("\nOriginal text:")
    print(block.message_text)

    print("\nOriginal Hash:")
    print(block.hash)

    old_hash = block.hash

    # Manual edit example
    alice.manual_edit(
        block,
        "This contract is signed between XYZ Company and Mohamed Ali for 70000 USD."
    )

    print("\nAfter manual edit:")
    print(block.message_text)

    print("\nHash:")
    print(block.hash)

    print("\nIntegrity:", block.verify_integrity(old_hash))