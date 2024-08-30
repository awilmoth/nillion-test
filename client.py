import grpc
import zkp_auth_pb2
import zkp_auth_pb2_grpc
from zkp import ZeroKnowledgeProof
from Crypto.Util import number

# Parameters for the ZKP (these need to match the server's settings)
p = 7477000007  # Example large prime
q = (p - 1) // 2
g = 5  # Generator

zkp = ZeroKnowledgeProof(p, q, g)


def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = zkp_auth_pb2_grpc.AuthStub(channel)

        # Register User
        x1, y1 = zkp.generate_private_public_key()
        x2, y2 = zkp.generate_private_public_key()

        print(f'Registering user1 with y1={y1} and y2={y2}')

        # Create RegisterRequest with y1 and y2 as int64
        register_request = zkp_auth_pb2.RegisterRequest(
            user='user1',
            y1=y1,
            y2=y2
        )

        register_response = stub.Register(register_request)
        print(f'Registered user1 with y1 and y2')

        # Create Authentication Challenge
        challenge_response = stub.CreateAuthenticationChallenge(
            zkp_auth_pb2.AuthenticationChallengeRequest(user='user1'))
        if challenge_response.auth_id == '':
            raise Exception('Failed to receive challenge')
        auth_id = challenge_response.auth_id
        c = challenge_response.c
        print(f'Challenge received: {c}')

        # Generate Response
        r1, _ = zkp.generate_commitment()
        r2, _ = zkp.generate_commitment()
        s1 = zkp.generate_response(r1, c, x1)
        s2 = zkp.generate_response(r2, c, x2)
        s = (s1 + s2) % q

        print(f'Sending response: s={s}')

        # Create AuthenticationAnswerRequest with s as int64
        verify_response = stub.VerifyAuthentication(
            zkp_auth_pb2.AuthenticationAnswerRequest(auth_id=auth_id, s=s)
        )
        if verify_response.session_id:
            print(f"Authentication successful, session ID: {verify_response.session_id}")
        else:
            print("Authentication failed")


if __name__ == '__main__':
    run()
