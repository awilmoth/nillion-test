# zkp.py
from Crypto.Util import number


class ZeroKnowledgeProof:
    def __init__(self, p: int, q: int, g: int):
        self.p = p
        self.q = q
        self.g = g

    def generate_private_public_key(self):
        x = number.getRandomRange(1, self.q - 1)
        y = pow(self.g, x, self.p)
        return x, y

    def generate_commitment(self):
        r = number.getRandomRange(1, self.q - 1)
        commitment = pow(self.g, r, self.p)
        return r, commitment

    def generate_challenge(self):
        return number.getRandomRange(1, self.q - 1)

    def generate_response(self, r: int, challenge: int, x: int):
        return (r + challenge * x) % self.q

    def verify(self, commitment: int, challenge: int, response: int, y: int):
        left = pow(self.g, response, self.p)
        right = (commitment * pow(y, challenge, self.p)) % self.p
        return left == right
