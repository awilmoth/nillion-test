# test_zkp.py
import pytest
from zkp import ZeroKnowledgeProof
from Crypto.Util import number


@pytest.fixture(scope="module")
def zkp_obj():
    p = 7477000007
    q = 3738500003
    g = 5
    return ZeroKnowledgeProof(p, q, g)


def test_generate_private_public_key(zkp_obj):
    x, y = zkp_obj.generate_private_public_key()
    assert 1 <= x < zkp_obj.q
    assert pow(zkp_obj.g, x, zkp_obj.p) == y


def test_generate_commitment(zkp_obj):
    r, commitment = zkp_obj.generate_commitment()
    assert 1 <= r < zkp_obj.q
    assert pow(zkp_obj.g, r, zkp_obj.p) == commitment


def test_generate_challenge(zkp_obj):
    challenge = zkp_obj.generate_challenge()
    assert 1 <= challenge < zkp_obj.q


def test_generate_response(zkp_obj):
    r = number.getRandomRange(1, zkp_obj.q - 1)
    x, _ = zkp_obj.generate_private_public_key()
    challenge = zkp_obj.generate_challenge()
    response = zkp_obj.generate_response(r, challenge, x)
    assert response == (r + challenge * x) % zkp_obj.q

