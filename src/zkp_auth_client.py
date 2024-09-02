import grpc
import zkp_auth_pb2
import zkp_auth_pb2_grpc
from zkp import ZeroKnowledgeProof
import logging
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_variables():
    try:
        p = int(os.getenv('ZKP_PRIME'))
        g = int(os.getenv('ZKP_GENERATOR'))
        if not p or not g:
            raise ValueError("ZKP_PRIME or ZKP_GENERATOR is not set properly.")
    except (TypeError, ValueError) as e:
        logger.error(f"Environment variable error: {e}")
        raise SystemExit(1)

    q = (p - 1) // 2

    grpc_server_url = os.getenv('GRPC_SERVER_URL')
    if not grpc_server_url:
        logger.error("Environment variable GRPC_SERVER_URL is not set.")
        raise SystemExit(1)

    return p, q, g, grpc_server_url


def register_user(stub, zkp, user_id):
    x1, y1 = zkp.generate_private_public_key()
    x2, y2 = zkp.generate_private_public_key()

    logger.info(f'Registering {user_id} with public keys y1={y1} and y2={y2}')

    register_request = zkp_auth_pb2.RegisterRequest(
        user=user_id,
        y1=y1,
        y2=y2
    )
    register_response = stub.Register(register_request)

    if not register_response:
        logger.error(f"Registration of {user_id} failed.")
        raise Exception('Registration failed')

    logger.info(f'Registered {user_id} successfully')
    return x1, x2


def create_authentication_challenge(stub, user_id):
    challenge_request = zkp_auth_pb2.AuthenticationChallengeRequest(user=user_id)
    challenge_response = stub.CreateAuthenticationChallenge(challenge_request)

    if not challenge_response.auth_id:
        logger.error('Failed to receive authentication challenge')
        raise Exception('Failed to receive challenge')

    logger.info(f'Challenge received for {user_id}: c={challenge_response.c}')
    return challenge_response.auth_id, challenge_response.c


def generate_authentication_response(zkp, c, x1, x2, q):
    r1, _ = zkp.generate_commitment()
    r2, _ = zkp.generate_commitment()
    s1 = zkp.generate_response(r1, c, x1)
    s2 = zkp.generate_response(r2, c, x2)
    s = (s1 + s2) % q

    logger.info(f'Generated response: s={s}')
    return s


def verify_authentication(stub, auth_id, s):
    verify_request = zkp_auth_pb2.AuthenticationAnswerRequest(auth_id=auth_id, s=s)
    verify_response = stub.VerifyAuthentication(verify_request)

    if verify_response.session_id:
        logger.info(f"Authentication successful, session ID: {verify_response.session_id}")
    else:
        logger.error("Authentication failed")
        raise Exception('Authentication failed')


def main():
    try:
        p, q, g, grpc_server_url = get_env_variables()
        zkp = ZeroKnowledgeProof(p, q, g)

        # Configure gRPC channel to use HTTP/2
        options = [
            ('grpc.enable_http_proxy', 0),  # Disable HTTP proxy
            ('grpc.keepalive_timeout_ms', 10000)  # Keepalive timeout
        ]

        with grpc.insecure_channel(grpc_server_url, options=options) as channel:
            stub = zkp_auth_pb2_grpc.AuthStub(channel)

            user_id = 'user1'
            x1, x2 = register_user(stub, zkp, user_id)
            auth_id, c = create_authentication_challenge(stub, user_id)
            s = generate_authentication_response(zkp, c, x1, x2, q)
            verify_authentication(stub, auth_id, s)

    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()} - {e.details()}")
    except SystemExit:
        pass  # Allow SystemExit to propagate
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    main()
