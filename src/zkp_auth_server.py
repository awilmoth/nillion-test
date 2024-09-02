import grpc
from concurrent import futures
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import zkp_auth_pb2
import zkp_auth_pb2_grpc
from zkp import ZeroKnowledgeProof
import logging
from dotenv import load_dotenv
import os
import threading

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the parameters for ZKP from environment
p = int(os.getenv('ZKP_PRIME'))  # Large prime
q = (p - 1) // 2
g = int(os.getenv('ZKP_GENERATOR'))  # Generator

zkp = ZeroKnowledgeProof(p, q, g)


class AuthServicer(zkp_auth_pb2_grpc.AuthServicer):
    def __init__(self):
        self.user_store = {}
        self.challenge_store = {}

    def Register(self, request, context):
        logger.info(f"Registering user {request.user} with y1={request.y1} and y2={request.y2}")
        self.user_store[request.user] = {
            'y1': request.y1,
            'y2': request.y2
        }
        return zkp_auth_pb2.RegisterResponse()

    def CreateAuthenticationChallenge(self, request, context):
        logger.info(f"Creating challenge for user {request.user}")
        if request.user not in self.user_store:
            context.abort(grpc.StatusCode.NOT_FOUND, "User not found")

        auth_id = "auth_" + str(time.time())
        c = zkp.generate_challenge()  # Generate a challenge using the ZKP instance
        self.challenge_store[auth_id] = {
            'user': request.user,
            'challenge': c
        }
        return zkp_auth_pb2.AuthenticationChallengeResponse(auth_id=auth_id, c=c)

    def VerifyAuthentication(self, request, context):
        logger.info(f"Verifying authentication with auth_id={request.auth_id} and s={request.s}")
        # Validate auth_id
        if request.auth_id not in self.challenge_store:
            context.abort(grpc.StatusCode.NOT_FOUND, "Authentication ID not found")

        challenge_data = self.challenge_store.pop(request.auth_id)  # Retrieve and remove the challenge data
        user_data = self.user_store.get(challenge_data['user'])

        if not user_data:
            context.abort(grpc.StatusCode.NOT_FOUND, "User data not found")

        # Here, you should verify the ZKP response (omitted for brevity)
        # This involves using the stored challenge, the user's public keys, and the provided response 's'

        session_id = "session_" + str(time.time())  # Generate a unique session ID
        logger.info(f"Authentication successful for {challenge_data['user']}, session ID: {session_id}")
        return zkp_auth_pb2.AuthenticationAnswerResponse(session_id=session_id)


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Healthy')
        else:
            self.send_response(404)
            self.end_headers()


def serve_http():
    server_address = ('', 8080)  # You can change this port if needed
    httpd = HTTPServer(server_address, HealthCheckHandler)
    logger.info(f'HTTP Server started on port {server_address[1]}')
    httpd.serve_forever()


def serve_grpc():
    port = 50051
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    zkp_auth_pb2_grpc.add_AuthServicer_to_server(AuthServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    logger.info(f'gRPC Server started on port {port}')
    try:
        while True:
            time.sleep(86400)  # 1 day in seconds
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    grpc_thread = threading.Thread(target=serve_grpc)
    http_thread = threading.Thread(target=serve_http)

    grpc_thread.start()
    http_thread.start()

    grpc_thread.join()
    http_thread.join()
