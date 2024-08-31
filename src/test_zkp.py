import unittest
from zkp import ZeroKnowledgeProof
from Crypto.Util import number


class TestZeroKnowledgeProof(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.p = 7477000007
        cls.q = 3738500003
        cls.g = 5
        cls.zkp_obj = ZeroKnowledgeProof(cls.p, cls.q, cls.g)

    def test_generate_private_public_key(self):
        x, y = self.zkp_obj.generate_private_public_key()
        self.assertTrue(1 <= x < self.zkp_obj.q)
        self.assertEqual(pow(self.zkp_obj.g, x, self.zkp_obj.p), y)

    def test_generate_commitment(self):
        r, commitment = self.zkp_obj.generate_commitment()
        self.assertTrue(1 <= r < self.zkp_obj.q)
        self.assertEqual(pow(self.zkp_obj.g, r, self.zkp_obj.p), commitment)

    def test_generate_challenge(self):
        challenge = self.zkp_obj.generate_challenge()
        self.assertTrue(1 <= challenge < self.zkp_obj.q)

    def test_generate_response(self):
        r = number.getRandomRange(1, self.zkp_obj.q - 1)
        x, _ = self.zkp_obj.generate_private_public_key()
        challenge = self.zkp_obj.generate_challenge()
        response = self.zkp_obj.generate_response(r, challenge, x)
        self.assertEqual(response, (r + challenge * x) % self.zkp_obj.q)


if __name__ == '__main__':
    unittest.main()
