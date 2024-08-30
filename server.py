import grpc
from concurrent import futures
import time
import zkp_auth_pb2
import zkp_auth_pb2_grpc
from zkp import ZeroKnowledgeProof

# Define the parameters for ZKP
p = 7477000007  # Example large prime
q = (p - 1) // 2
g = 5  # Generator

zkp = ZeroKnowledgeProof(p, q, g)


class AuthServicer(zkp_auth_pb2_grpc.AuthServicer):
    def Register(self, request, context):
        print(f"Registering user {request.user} with y1={request.y1} and y2={request.y2}")
        # Store user's public keys, etc.
        return zkp_auth_pb2.RegisterResponse()

    def CreateAuthenticationChallenge(self, request, context):
        print(f"Creating challenge for user {request.user}")
        auth_id = "some_unique_id"
        c = zkp.generate_challenge()  # Generate a challenge using the ZKP instance
        return zkp_auth_pb2.AuthenticationChallengeResponse(auth_id=auth_id, c=c)

    def VerifyAuthentication(self, request, context):
        print(f"Verifying authentication with auth_id={request.auth_id} and s={request.s}")
        # Verify the response, etc.
        session_id = "some_session_id"  # Some session value if verification succeeds
        return zkp_auth_pb2.AuthenticationAnswerResponse(session_id=session_id)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    zkp_auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # 1 day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
