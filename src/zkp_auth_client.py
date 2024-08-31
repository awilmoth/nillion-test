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
            logger.error("ZKP_PRIME or ZKP_GENERATOR is not set properly.")
            raise SystemExit(1)
    except (TypeError, ValueError) as e:
        logger.error(f"Environment variable error: {e}")
        raise SystemExit(1)

    q = (p - 1) // 2

    grpc_server_url = os.getenv('GRPC_SERVER_URL')
    if not grpc_server_url:
        logger.error("GRPC_SERVER_URL is not set.")
        raise SystemExit(1)

    return p, q, g, grpc_server_url


def zkp_run():
    try:
        p, q, g, grpc_server_url = get_env_variables()
        zkp = ZeroKnowledgeProof(p, q, g)

        with grpc.insecure_channel(grpc_server_url) as channel:
            stub = zkp_auth_pb2_grpc.AuthStub(channel)

            # Register User
            x1, y1 = zkp.generate_private_public_key()
            x2, y2 = zkp.generate_private_public_key()

            logger.info(f'Registering user1 with y1={y1} and y2={y2}')

            register_request = zkp_auth_pb2.RegisterRequest(
                user='user1',
                y1=y1,
                y2=y2
            )

            register_response = stub.Register(register_request)
            logger.info('Registered user1 with y1 and y2')

            # Create Authentication Challenge
            challenge_response = stub.CreateAuthenticationChallenge(
                zkp_auth_pb2.AuthenticationChallengeRequest(user='user1'))
            if not challenge_response.auth_id:
                raise Exception('Failed to receive challenge')

            auth_id = challenge_response.auth_id
            c = challenge_response.c
            logger.info(f'Challenge received: {c}')

            # Generate Response
            r1, _ = zkp.generate_commitment()
            r2, _ = zkp.generate_commitment()
            s1 = zkp.generate_response(r1, c, x1)
            s2 = zkp.generate_response(r2, c, x2)
            s = (s1 + s2) % q

            logger.info(f'Sending response: s={s}')

            verify_response = stub.VerifyAuthentication(
                zkp_auth_pb2.AuthenticationAnswerRequest(auth_id=auth_id, s=s)
            )
            if verify_response.session_id:
                logger.info(f"Authentication successful, session ID: {verify_response.session_id}")
            else:
                logger.error("Authentication failed")
    except grpc.RpcError as e:
        logger.error(f"gRPC error: {e.code()} - {e.details()}")
    except SystemExit:
        pass  # Let it raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    zkp_run()
