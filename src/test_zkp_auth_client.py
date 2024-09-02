import unittest
from unittest.mock import patch, MagicMock
import os
from zkp_auth_client import zkp_run, get_env_variables


class TestRunFunction(unittest.TestCase):

    @patch.dict(os.environ, {
        'ZKP_PRIME': '7477000007',
        'ZKP_GENERATOR': '5',
        'GRPC_SERVER_URL': 'localhost:50051'
    })
    @patch('zkp_auth_pb2_grpc.AuthStub')
    @patch('grpc.insecure_channel')
    # def test_run_success(self, mock_insecure_channel, mock_AuthStub):
    #     # Mocking
    #     mock_channel = MagicMock()
    #     mock_insecure_channel.return_value.__enter__.return_value = mock_channel
    #     mock_stub = MagicMock()
    #     mock_AuthStub.return_value = mock_stub
    #
    #     # Setting up mock return values
    #     mock_stub.Register.return_value = MagicMock()
    #     mock_stub.CreateAuthenticationChallenge.return_value = MagicMock(auth_id="auth_id", c=1234)
    #     mock_stub.VerifyAuthentication.return_value = MagicMock(session_id="session_id")
    #
    #     # Run the function
    #     with self.assertLogs('zkp_auth_client', level='INFO') as log:
    #         zkp_run()
    #
    #     # Asserts: Ensure general content rather than exact string matches due to dynamic values in logs
    #     self.assertTrue(any("Registered user1 with y1 and y2" in message for message in log.output))
    #     self.assertTrue(any("Challenge received: 1234" in message for message in log.output))
    #     self.assertTrue(any("Sending response: s=" in message for message in log.output))
    #     self.assertTrue(any("Authentication successful, session ID: session_id" in message for message in log.output))

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_env_variables(self):
        with self.assertRaises(SystemExit):
            get_env_variables()

    @patch.dict(os.environ, {
        'ZKP_PRIME': 'invalid',
        'ZKP_GENERATOR': '5',
        'GRPC_SERVER_URL': 'localhost:50051'
    })
    def test_invalid_prime_env(self):
        with self.assertRaises(SystemExit):
            get_env_variables()

    @patch.dict(os.environ, {
        'ZKP_PRIME': '7477000007',
        'ZKP_GENERATOR': '5'
    }, clear=True)
    def test_missing_grpc_server_url(self):
        with self.assertRaises(SystemExit):
            get_env_variables()


if __name__ == '__main__':
    unittest.main()
